import os
import glob
import struct
import itertools
import numpy as np
from copy import deepcopy
from collections import namedtuple
import xml.etree.ElementTree as ET
from numpy.lib.stride_tricks import as_strided
import tarfile

# our stuff
import tsutils

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Classes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MobergSignal(object):
    def __init__(self, index, name, data_format):
        self.index  = index
        self.name   = name
        self.format = data_format


class MobergBlock(object):
    def __init__(self, index, clock_us, sample_interval, \
                 bytes_per_sample, bytes_per_value, is_composite, data_format):
        self.index = index # block offset
        self.start_usec = clock_us
        self.sample_interval = sample_interval
        self.bytes_per_sample = bytes_per_sample
        self.bytes_per_value = bytes_per_value
        self.is_composite = is_composite
        self.data_format = data_format

        # NOTE:
        #   The following are determined after parsing the
        #   settings file and/or evaluating all block indices.
        self.length = 0
        self.last   = False

    @property
    def end_usec(self):
        return self.start_usec + self.length * self.sample_interval

class MobergSource(object):
    def __init__(self, name, modality, location, type, data_type, filepath=None):
        self.name              = name
        self.modality          = modality
        self.location          = location
        self.type              = type
        self.data_type         = data_type
        self.is_composite      = False
        self.filepath          = filepath

        # files
        self._index_file       = None
        self._data_file        = None
        self._settings_file    = None
        self._textdata_file    = None

        # data
        self.signals           = []
        self._blocks           = []

        # signal details
        self._total_samples    = None
        self._dtype            = None
        self._conversion       = 1
        self.units             = 'Unknown'

        # low-level details
        self._file_size        = None
        self._bytes_per_value  = None
        self._bytes_per_sample = None
        self._mem_map          = None
        self._byte_aligned     = True
        self._byte_overflow    = False

    @property
    def num_signals(self):
        return len(self.signals)

    @property
    def num_blocks(self):
        return len(self._blocks)

    @property
    def mem_map(self):
        if self._mem_map is None:
            self._set_memmap()
        return self._mem_map

    def add_index(self, f):
        self._index_file = f
        self._blocks = list(parse_index_file(f))

        if len(self._blocks) > 0:
            first = self._blocks[0]
            self.is_composite = first.is_composite

            # TODO ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #  Below should be handled on a per-signal basis
            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            self._bytes_per_value = first.bytes_per_value
            if self.is_composite:
                self._bytes_per_sample = first.bytes_per_sample
            else:
                self._bytes_per_sample = first.bytes_per_value
            # numpy data type (or string for non-numpy)
            if not self.is_composite:
                self._dtype = dtype_from_format(self.data_type, first.bytes_per_value)

    def add_settings(self, f):
        self._settings_file = f

    def add_data(self, f):
        self._data_file = f
        self._file_size = os.path.getsize(self.data_path)

    def add_text_data(self, f):
        self._textdata_file = f

    def _calculate_block_sizes(self):
        """
        Using index locations, determine size of each block (in entries)
        """
        self.log('Calculating block sizes...')
        # return if no blocks
        if len(self._blocks)==0: return []
        # find block positions
        breaks = np.array([i.index for i in self._blocks] + [self._total_samples])
        # find block lengths
        block_sizes = breaks[1:]-breaks[:-1]
        # sanity check
        assert np.sum(block_sizes) == self._total_samples, \
                    "Number of samples from indices does not match byte calculation"
        # assign block lengths
        for block,size in itertools.izip(self._blocks, block_sizes):
            block.length = size
        block.last = True

        self.log('Blocks;  num={n}, min-size={min}, max-size={max}'.format(
                    n=len(block_sizes), min=np.min(block_sizes), max=np.max(block_sizes)))
        return block_sizes

    def _parse_settings(self):
        self.log('Parsing settings file...')
        if self._settings_file is None:
            return

        # get things from settings
        tree = ET.parse(os.path.abspath(self._settings_file))
        root = tree.getroot()
        self.units = root.find('Units').text
        if self.type == 'SampleSeries':
            # conversion factor
            conversion_str = root.find('SampleConversion').text.strip()
            input_lo, input_hi, output_lo, output_hi = map(float, conversion_str.split(','))
            conversion = output_hi/input_hi
            self._conversion = conversion
            assert conversion == (output_lo/input_lo), "SampleConversion is not symmetrical"

        if self.is_composite:
            # composite signals
            sigs = root.findall('CompositeElements/CompositeElement')
            sig_details = [x.attrib.get('type',',unknown,') for x in sigs]
            sig_types   = [x.split(',')[3] for x in sig_details]
            sig_names   = [x.split(',')[1] for x in sig_details]

            if len(set(sig_types)) != 1:
                raise Exception(
                        "Multiple data types across composite signals is not yet supported",
                        signal_types = sig_types)

            # TODO:
            #   This should be handled on a per-signal level, but how that translates
            #   to memmap dtype is unclear. Thought is needed.
            self._dtype = dtype_from_format(
                dformat = set(sig_types).pop(),
                nbytes  = self._blocks[0].bytes_per_value)

            # create signals
            self.signals = [
                MobergSignal(
                    index       = i,
                    name        = '{} - {}'.format(self.modality, n),
                    data_format = t)
                for i,(n,t) in enumerate(zip(sig_names,sig_types))
            ]

        else:
            # if not composite, create one signal
            self.signals = [
                MobergSignal(index=0, name=self.modality, data_format=self.data_type)
            ]

        self.log('Found signals: {}'.format(','.join([s.name for s in self.signals])))
        self.log('Done parsing settings file.')

    def _set_memmap(self):
        """
        Shared numpy memory-map for all signals. This should be passed to
        _get_block_chunked_signals() when retrieving block/signal data.
        """
        # shape of data over entire file
        shape = (self.num_signals, self._total_samples)
        if isinstance(self._dtype, type):
            # native NumPy data type; normal mem-mapped matrix
            self._mem_map = np.memmap(
                filename = self.data_path,
                dtype    = self._dtype,
                shape    = shape,
                mode     = 'r', # read-only
                order    = 'F') # column-major
        else:
            #  We need to map to individual bytes of file data, then
            #  set the view to a higher-byte interpretation. Method found here:
            #  https://stackoverflow.com/questions/12080279/how-do-i-create-a-numpy-dtype-that-includes-24-bit-integers/34128171#34128171
            self._byte_aligned = False
            if self._dtype == 'f24':
                # 24-bit float
                raise Exception("24-bit floating point not supported")

            elif self._dtype == 'i24':
                # handle last sample separately (not using mem-map)
                nsamples = self._total_samples - 1
                shape = (self.num_signals, nsamples)
                nbytes = self._file_size - self._bytes_per_sample
                self.log('Mapping raw bytes')
                # 24-bit integer
                raw_bytes = np.memmap(
                    filename = self.data_path,
                    dtype    = np.dtype('u1'),
                    shape    = (nbytes,),
                    mode     = 'r') # read-only

                self.log('Creating 32-bit view, shape={}'.format(shape))
                self._mem_map = as_strided(
                    raw_bytes.view(np.int32),
                    strides   = (self._bytes_per_value, self._bytes_per_sample),
                    shape     = shape,
                    writeable = False)

            else:
                raise Exception("Unknown data type: {}".format(self._dtype))

    def _get_overflow_value(self, signal_i):
        assert self._dtype == 'i24', "Overflow bytes only supported for 24-bit signed integers"
        # get byte offset position (column oriented file)
        offset = self._file_size-((self.num_signals-signal_i)*self._bytes_per_value)-1
        # read bytes
        with open(self.data_path, 'rb') as f:
            f.seek(offset)
            data = f.read(self._bytes_per_value)
        # map to int32
        data = data + '\0'*(4-self._bytes_per_value)
        return struct.unpack('<i', data)[0]

    def _get_block_chunked_signals(self, block):
        """
        For a given block, returns series of signals chunked over time
        such that the data will fit in memory.

        returns (`num_signals` x `num_chunks`) signals
        """

        # separate data by signals
        max_read_chunk_size = 100000
        for i,signal in enumerate(self.signals):
            # chunk data
            for j, offset in enumerate(np.arange(0, block.length, step=max_read_chunk_size)):
                # grab subslice of memory map that aligns to block-chunk
                offset    = min(offset, block.length)
                step      = min(max_read_chunk_size, block.length-offset)
                idx_start = block.index + offset
                idx_end   = idx_start + step
                sdata     = self.mem_map[i, idx_start:idx_end]

                # correct, if necessary
                if not self._byte_aligned:
                    if block.last and (offset + step) >= block.length:
                        """
                        NOTE: Accessing (last_block, last_sample) can
                              cause a segfault when dealing with byte-unaligned
                              data (24-bit) as 32-bit numpy strided "view".

                              Instead, we read in the last sample from the
                              bytes directly rather than relying on numpy.
                        """
                        v = np.array([self._get_overflow_value(i)], dtype=np.int32)
                        sdata = np.concatenate([sdata, v])
                    # correct 24-bit aligned data to fit 32-bit dtype
                    sdata = tsutils.correct_24bit_signed(sdata)

                # timing
                start = block.start_usec + offset*block.sample_interval

                # assign data/properties to signal
                s = deepcopy(signal)
                s.sample_interval = block.sample_interval
                s.start           = start
                s.length          = len(sdata)
                s.data            = np.multiply(sdata, self._conversion)

                # lazy return
                yield s
                del s

    def get_data(self):
        """
        Goals:
        1. Using data type, create memory-map to data source file (if possible)
           - Using bytes_per_value, data format, and #signals
        2. Get data blocks and their sizes
        3. Break up blocks into chunkable data (that fit into memory)
        4. Yield that data to be processed by importer
        """
        self.log('Retrieving source data...')
        self._parse_settings()

        # num samples based on bytes
        self._total_samples = self._file_size/self._bytes_per_sample

        # data
        self._calculate_block_sizes()
        for block in self._blocks:
            for signal in self._get_block_chunked_signals(block):
                yield signal

        # clean up
        self.log('Done retrieving source data.')
        del self._mem_map
        self._mem_map = None

    @property
    def data_path(self):
        return os.path.abspath(self._data_file)

    @classmethod
    def from_files(cls, files):
        modality, location, src_type, data_type, src_name = \
                                    filename(files[0]).split(',')[:-1]
        src = cls(name      = src_name,
                  modality  = modality,
                  location  = location,
                  type      = src_type,
                  data_type = data_type)

        for f in files:
            ext = f.split(',')[-1].lower()
            if ext   == 'index':
                src.add_index(f)
            elif ext == 'data':
                src.add_data(f)
            elif ext == 'settings':
                src.add_settings(f)
            elif ext == 'textdata':
                src.add_text_data(f)
            else:
                # TODO: log that file is not supported
                pass
        return src

    def log(self, msg):
        pass
        # logger.info('{name} {src} - {msg}'.format(name=self.name, src=self.modality, msg=msg))

    def __repr__(self):
        return "<MobergSource name='{name}' modality='{modality}' type='{type}'>".format(
                name=self.name, modality=self.modality, type=self.type)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def filename(f):
    return os.path.basename(f)

def dtype_from_format(dformat, nbytes):
    dformat = dformat.strip().lower()
    if nbytes == 4:
        # 32-bit data. Nice and easy: native NumPy support.
        if dformat == 'float':
            dtype = np.float32
        elif dformat in ['integer','integeraggregate']:
            dtype = np.int32
        else:
            raise Exception("Unknown type - not supported")
    elif nbytes == 3:
        # 24-bit data. Ooph, not easy: no native NumPy support.
        if dformat == 'float':
            dtype = 'f24'
        elif dformat in ['integer','integeraggregate']:
            dtype = 'i24'
        else:
            raise Exception("Unknown type - not supported")
    else:
        raise Exception('Unsupported byte length: {} bytes'.format(nbytes))

    if dformat == 'composite':
        raise Exception('Format should be signal-specific data type, not composite')
    elif dformat == 'char':
        raise NotImplementedError("Char data format not supported yet")

    return dtype

def is_source_file(f):
    f = os.path.basename(f)
    return f.count(',') == 5


def parse_patient_files(files):
    source_files = set(filter(is_source_file, files))
    additional_files = set(files).difference(source_files)

    # source objects
    sources = get_moberg_sources(files=source_files)
    return sources

def get_moberg_sources(files):
    prefixes = set(','.join(x.split(',')[:-1]) for x in files)
    grouped = [
        filter(lambda x: x.startswith(prefix), files)
        for prefix in prefixes
    ]
    return [MobergSource.from_files(files) for files in grouped]

def get_index_record(data):
    """
    From Moberg "DataStorageFormats" documentation (doc #: 422-0248-00)

    .---------.---------.-------------.----------------------------------------
    |Offset   | Size    |             |
    |(bytes)  | (bytes) | Format      | Contents
    |---------|---------|-------------|----------------------------------------
    | 0       | 8       | 64 bit uint | Index of the first sample in this data run.
    |         |         |             | This index times the number of bytes per
    |         |         |             | sample will yield the file read position
    |         |         |             | where this data run begins.
    |---------|---------|-------------|----------------------------------------
    | 8       | 8       | 64 bit uint | System clock time (in uS) identifying the
    |         |         |             | starting time of the data run.
    |---------|---------|-------------|----------------------------------------
    | 16      | 4       | 32 bit uint | Sample interval - fractional portion.
    |---------|---------|-------------|----------------------------------------
    | 20      | 4       | 32 bit uint | Sample interval - integer portion.
    |         |         |             | Sample interval (uS) = integer portion
    |         |         |             |    + (fractional portion / (2^32))
    |---------|---------|-------------|----------------------------------------
    | 24.     | 1.      | 8 bit uint. | Format identifier.
    |         |         |             | The lower 7 bits define the sample format:
    |         |         |             |   0x05: Uncompressed 24-bit
    |         |         |             |   0x04: Uncompressed 32-bit
    |         |         |             |   0x00: Composite with multiple formats
    |         |         |             | Additionally the most significant bit (0x80)
    |         |         |             | will be set when dealing with composite data.
    |---------|---------|-------------|----------------------------------------
    | 25.     | 1.      | 8 bit uint. | Checksum. Sum of all the preceding bytes.
    |---------|---------|-------------|----------------------------------------
    | 26.     | 2       | 16 bit uint | Bytes per composite sample
    .---------.---------.-------------.----------------------------------------
    """

    fmt = 'LLIIBBH'

    (index,
    clock_us,
    sample_interval_frac,
    sample_interval_int,
    format_identifier,
    checksum,
    bytes_per_sample) = struct.unpack(fmt, data)

    sample_interval = sample_interval_int + (sample_interval_frac  * 1.0 / 2**32)

    # parse format bits
    is_composite = False
    if bool(format_identifier & 0x80):
        # 0x80 - is composite
        format_identifier -= 0x80
        is_composite = True

    if format_identifier == 0x04:
        data_format = 'uncompressed 32bit'
        bytes_per_value = 4
    elif format_identifier == 0x05:
        data_format = 'uncompressed 24bit'
        bytes_per_value = 3
    elif format_identifier == 0x00:
        # 0x00 also signifies composite with MULTIPLE data formats
        raise Exception("Composite with multiple formats currently not supported.")
    else:
        raise NotImplementedError("Data format not recognized")

    # return friendly thing
    return MobergBlock(
        index = index,
        clock_us = clock_us,
        sample_interval = sample_interval,
        bytes_per_sample = bytes_per_sample,
        bytes_per_value  = bytes_per_value,
        is_composite = is_composite,
        data_format = data_format
    )

def parse_index_file(filename):
    with open(filename, 'rb') as f:
        d = f.read(28)
        while len(d) == 28:
            # parse index record bytes
            yield get_index_record(d)
            # read again
            d = f.read(28)

def process_patient_file(file):
    tree = ET.parse(file)
    root = tree.getroot()

    # extract all key/value pairs
    data = {x.tag: x.text.strip() for x in root.getchildren() if x.text.strip()!=''}

    # determine package name
    patient_str = '{} {}'.format(data.get('PatientFirstName',''), data.get('PatientLastName', ''))
    if len(patient_str) < 3:
        patient_str = data.get('MedicalRecordNumber', 'Moberg Patient')
    data['_name'] = 'Patient: {}'.format(patient_str)
    return data

def extract_files(fname):
    directory = os.path.dirname(os.path.abspath(fname))
    tar = tarfile.open(fname)
    tar.extractall(directory)
    files_total  = tar.getnames()
    files_total = ['{}/{}'.format(directory, i) for i in files_total]

    # remove potential ._ (resource fork) files
    pruned_files = filter(lambda x: '._' not in x, files_total)
    tar.close()
    files = {
        'files'             : pruned_files,
        'cleanup-resources' : files_total
    }
    return files

def cleanup(files):
    for f in files:
        try:
            os.remove(f)
        except OSError:
            pass
