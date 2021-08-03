import os
import numpy as np

# our stuffs
from timeseries_db import TimeSeriesDatabase, DatabaseSettings
from base_processor import BaseProcessor

# spike file parsing
HEADER_SIZE  = 24
HEADER_DTYPE = np.dtype([
                        ('offset',          np.int64),
                        ('num_spikes',      np.int64),
                        ('num_samples',     np.int64)])

SPIKE_DTYPE = np.dtype([
                        ('spike',           np.int64),
                        ('unit',            np.int8)])

WAVEFORM_DTYPE = np.dtype([
                        ('waveform',        np.float64)])

# File chunk size (in samples)
CHUNK_SIZE = long(os.environ.get('CHUNK_SIZE', 1e5))

ENVIRONMENT = os.environ.get('ENVIRONMENT', "None")
USE_SSL = ENVIRONMENT.lower() != 'local'

class ChannelDataWriter(BaseProcessor):
    required_inputs = ['file', 'channel']

    def __init__(self, append=False, use_ssl=USE_SSL, *args, **kwargs):
        # initialize settings inside processor

        super(ChannelDataWriter, self).__init__(*args, **kwargs)

        self.settings = DatabaseSettings(use_ssl=use_ssl)

        self.sampling_rate = None
        self.num_values_written = 0
        self.num_gaps_found = 0
        self.db = TimeSeriesDatabase(
            logger    = self.LOGGER,
            settings  = self.settings
        )

    @property
    def channel(self):
        return self.inputs.get('channel')

    def set_offset(self, fname, offset):
        f = open(fname, "rb")
        f.seek(offset, os.SEEK_SET)
        return f

    def validate_waveforms(self, fname, offset, nsamples, nspikes):
        '''
        Make sure the number of wavefors to read is correct:
            number_spikes = (file_size_bytes - (header_size + spikes_size)) / 8 * num_samples
        '''
        wf_num = (os.stat(fname).st_size - offset)/(8 * nsamples)
        try:
            assert wf_num == nspikes
        except AssertionError:
            message_brief = '{}: Number of waveforms is not consistent '\
                            'with number of spikes'.format(fname)

            message_detailed = 'Number of Spikes: {} does not match the number'\
                               ' of waveforms {} for {}'.format(wf_num,nspikes,fname)

            self.LOGGER.error(message_detailed)
            raise Exception(message_brief)

    def get_spike_data(self, fname):
        '''
        Parses spike binary file and returns timestamps for spikes

        TODO: figure out what to do with waveforms...
        '''

        # get number of spikes in file
        offset, spike_num, samples_num = np.fromfile(fname, dtype=HEADER_DTYPE, count=1)[0]
        print offset, spike_num, samples_num

        f = self.set_offset(fname, HEADER_SIZE)
        spikes = np.fromfile(f, dtype=SPIKE_DTYPE, count=spike_num)

        self.validate_waveforms(
            fname    = fname,
            offset   = HEADER_SIZE + offset,
            nsamples = samples_num,
            nspikes  = spike_num)

        try:
            waveforms = np.memmap(
                                  filename = fname,
                                  dtype    = WAVEFORM_DTYPE,
                                  shape    = (spike_num, samples_num),
                                  offset   = HEADER_SIZE + offset)
        except Exception as e:
            message = 'Waveforms could not be read for {}\n'\
                            '\t Exited with exception: {}'.format(fname, e)
            self.LOGGER.error(message)
            raise Exception(message)

        return spikes, waveforms

    def process_unit(self):
        spikes, waveforms = self.get_spike_data(self.inputs['file'])
        num_written = self.db.write_unit(spikes, waveforms, self.inputs['file'])
        self.num_values_written += num_written

    def write_continuous(self, values, timestamps):
        """
        Write continuous data to the time series database. First identifies
        contiguous segments by finding gaps in the data.
        """
        chunks = list(self.find_chunks(timestamps))
        num_gaps = len(chunks) - 1
        self.num_gaps_found += num_gaps

        for start, end in chunks:
            num_written = self.db.write_continuous(values[start:end], timestamps[start])
            self.num_values_written += num_written

    def find_chunks(self, timestamps):
        '''
        Returns the index ranges for contiguous segments in data.
        Boundaries are identified as follows:

            (timestamp_difference) > 2 * sampling_period

        '''
        sampling_rate = self.get_sampling_rate(timestamps)
        gap_threshold = (1.0/sampling_rate)*1e6 * 2

        boundaries = np.concatenate(
            ([0], np.where( np.diff(timestamps) > gap_threshold)[0] + 1, [len(timestamps)]))

        for i in np.arange(len(boundaries)-1):
            yield boundaries[i], boundaries[i + 1]

    def get_sampling_rate(self, timestamps):
        """
        Returns sampling rate of data.

        1. Get sampling rate from channel info.
        2. Calculate rate from timestamps.
        3. Compare these two values for sanity reasons.
        4. Return sampling rate (channel info)

        Reasonable assumption: first two timestamps are intended to be contiguous.
        """
        if self.sampling_rate is None:
            sampling_period = np.median(np.diff(timestamps[:10]))
            inferred_sampling_rate = 1e6 / sampling_period
            sampling_rate = float(self.channel['rate'])
            error = abs(inferred_sampling_rate-sampling_rate) * 1.0 / sampling_rate
            if error > 0.02:
                # error is greater than 2%
                raise Exception("Inferred rate from timestamps ({ts_rate:.4f}) does not match channel rate ({ch_rate:.4f})." \
                        .format(ts_rate=inferred_sampling_rate, ch_rate=sampling_rate))
            self.sampling_rate = sampling_rate
            self.LOGGER.info("SAMPLING RATE: {}".format(self.sampling_rate))
        return self.sampling_rate

    def task(self):
        self.db.set_channel(self.channel)

        if self.channel['type'] == 'CONTINUOUS':
            continuous_file = self.inputs.get('file', None)

            if continuous_file is not None:
                # load timestamps/values; data is interleaved
                self.LOGGER.info("Writing channel data for channel {}".format(self.channel['nodeId']))

                data = read_continuous_file(continuous_file)
                num_samples = data.shape[0]

                for index in np.arange(0, num_samples, CHUNK_SIZE):
                    print("Write values in channel_writer: " + str(index))
                    index_stop = min(index + CHUNK_SIZE, num_samples)
                    self.LOGGER.info("PROCESSING INDEX start={}, stop={}".format(index, index_stop))
                    timestamps_chunk = data[index:index_stop, 0].astype(np.int64)
                    values_chunk = data[index:index_stop, 1]
                    self.write_continuous(values_chunk, timestamps_chunk)

        elif self.channel['type'] == 'UNIT':
            self.process_unit()


def read_continuous_file(filename):
    '''
    Read a file of continuos (timestamp, value) pairs into a NumPy array.

    These files are written in BaseTimeSeriesProcessor.write_channel_data
    '''
    file_size = os.path.getsize(filename)

    # 8-bytes per value, 2 values per row (timestamp/reading)
    assert file_size % 16 == 0
    num_samples = file_size / 16

    return np.memmap(filename, dtype=np.float64, mode='r',
                     shape=(num_samples, 2), order='C')
