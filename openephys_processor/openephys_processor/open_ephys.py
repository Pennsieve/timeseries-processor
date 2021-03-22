# -*- coding: utf-8 -*-

import os
import numpy as np
from datetime import datetime
from tempfile import mkdtemp

def read_header(f):
    '''
    Read header information from the first 1024 bytes of an OpenEphys file.

    Parameters
    ----------
    | f : file
    |     An open file handle to an OpenEphys file

    Returns
    -------
    | header : dict
    |     Dictionary of header info
    '''
    header = {}

    # Read the data as a string
    # Remove newlines and redundant "header." prefixes
    # The result should be a series of "key = value" strings, separated
    # by semicolons.
    # header_string = f.read(1024).replace('\n','').replace('header.','')
    header_string = f.read(1024).replace('\n','').replace('header.','')

    # Parse each key   = value string separately
    for pair in header_string.split(';'):
        if '=' in pair:
            key, value = pair.split(' = ')
            key        = key.strip()
            value      = value.strip()

            # Convert some values to numeric
            if key in ['bitVolts', 'sampleRate']:
                header[key] = float(value)
            elif key in ['blockLength', 'bufferSize', 'header_bytes']:
                header[key] = int(value)
            elif key == 'date_created':
                header[key] = datetime.strptime(value, "'%d-%b-%Y %H%M%S'")
            elif "'" in value: #strip out quotes around strings
                header[key] = value[1:-1]
            else:
                # Keep as string
                header[key] = value

    return header

def get_type(fname):
    with file(fname, 'rb') as f:

        # check if file is openephys metadata or a message event
        if os.path.splitext(fname)[-1].upper() == '.OPENEPHYS':
            return 'OPENEPHYS'
        elif os.path.basename(fname).endswith('.events'):
            return 'EVENTS_MESSAGE'

        try:
            s =  read_header(f)['description']
        except:
            s = 'OTHER'

        if 'sample count' in s:
            return 'CONTINUOUS'
        elif 'eventType' in s:
            return 'SPIKE'
        elif 'sample position' in s:
            return 'EVENT'
        else:
            return s

def load_continuous(fname, tmp_dir):
    with file(fname,'rb') as f:
        header             = read_header(f)
        spec_record_marker = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 255])

        # calculate number of records
        block_len  = header['blockLength']
        record_len = 2 * block_len + 22
        file_len   = os.fstat(f.fileno()).st_size
        n_records  = int((file_len - 1024) / record_len)

        # initialize memory, using memmap arrays
        pkg_dir = mkdtemp(dir=tmp_dir)         # use pkg_dir for temp files (gets cleaned up after import)
        chan_name = header['channel']          # use chan name to allow parallelization
        path = os.path.join(pkg_dir,chan_name) # create path

        samples    = np.memmap(path+'_samples.dat',    dtype='int16',  mode='w+', shape=(int(n_records*block_len)))
        timestamps = np.memmap(path+'_timestamps.dat', dtype='int64',  mode='w+', shape=(n_records))
        rec_nums   = np.memmap(path+'_rec_nums.dat',   dtype='uint16', mode='w+', shape=(n_records))

        '''
        samples    = np.zeros(int(n_records*block_len))
        timestamps = np.zeros(n_records)
        rec_nums   = np.zeros(n_records)
        '''

        for rec in range(n_records):
            timestamps[rec] = np.fromfile(f, np.dtype('<i8'), 1)
            N               = np.fromfile(f, np.dtype('<u2'), 1).item()
            rec_nums[rec]   = np.fromfile(f, np.dtype('<u2'), 1)
            data            = np.fromfile(f, np.dtype('>i2'), block_len)  # read N big-endian int16 samples
            record_marker   = np.fromfile(f, np.dtype('<u1'), 10)

            samples[rec*block_len:(rec+1)*block_len] = data

    data = samples * header['bitVolts']

    data = {
        'data'       : samples,
        'timestamps' : timestamps,
        'rec_nums'   : rec_nums,
        'header'     : header,
        'units'      : 'uV'
    }

    return data

def load_spikes(fname):
    with file(fname,'rb') as f:
        header = read_header(f)

        n_channels = int(header['num_channels'])
        n_samples  = 40 # **NOT CURRENTLY WRITTEN TO HEADER**

        # Calculate record lenght and num records
        record_len = 2*n_channels*n_samples + 4*n_channels + 2*n_channels + 44
        file_len   = os.fstat(f.fileno()).st_size
        n_records  = int((file_len - 1024) / record_len)

        # initialize memory, using memmap arrays
        pkg_dir = mkdtemp()             # use pkg_dir for temp files (gets cleaned up after import)
        chan_name = header['electrode']          # use chan name to allow parallelization
        path = os.path.join(pkg_dir,chan_name) # create path

        spikes     = np.memmap(path+'_spikes.dat',     dtype='uint16',  mode='w+', shape=(n_records, n_channels, n_samples))
        timestamps = np.memmap(path+'_timestamps.dat', dtype='int64',   mode='w+', shape=(n_records))
        source     = np.memmap(path+'_source.dat',     dtype='uint16',  mode='w+', shape=(n_records))
        gain       = np.memmap(path+'_gain.dat',       dtype='float32', mode='w+', shape=(n_records, n_channels))
        thresh     = np.memmap(path+'_thresh.dat',     dtype='uint16',  mode='w+', shape=(n_records, n_channels))
        sortedId   = np.memmap(path+'_sortedId.dat',   dtype='uint16',  mode='w+', shape=(n_records, n_channels))
        recNum     = np.memmap(path+'_recNum.dat',     dtype='uint16',  mode='w+', shape=(n_records))

        '''
        spikes     = np.zeros((n_records, n_channels, n_samples))
        timestamps = np.zeros(n_records)
        source     = np.zeros(n_records)
        gain       = np.zeros((n_records, n_channels))
        thresh     = np.zeros((n_records, n_channels))
        sortedId   = np.zeros((n_records, n_channels))
        recNum     = np.zeros(n_records)
        '''

        for rec in range(n_records):
            eventType          = np.fromfile(f, np.dtype('<u1'), 1) #always equal to 4, discard
            timestamps[rec]    = np.fromfile(f, np.dtype('<i8'), 1)
            software_timestamp = np.fromfile(f, np.dtype('<i8'), 1)
            source[rec]        = np.fromfile(f, np.dtype('<u2'), 1)
            n_channels         = np.fromfile(f, np.dtype('<u2'), 1)
            n_samples          = np.fromfile(f, np.dtype('<u2'), 1)
            sortedId[rec]      = np.fromfile(f, np.dtype('<u2'), 1)
            electrodeId        = np.fromfile(f, np.dtype('<u2'), 1)
            channel            = np.fromfile(f, np.dtype('<u2'), 1)
            color              = np.fromfile(f, np.dtype('<u1'), 3)
            pcProj             = np.fromfile(f, np.float32, 2)
            sampleFreq         = np.fromfile(f, np.dtype('<u2'), 1)
            waveforms          = np.fromfile(f, np.dtype('<u2'), n_channels*n_samples)
            gain[rec,:]        = np.fromfile(f, np.float32, n_channels)
            thresh[rec,:]      = np.fromfile(f, np.dtype('<u2'), n_channels)
            recNum[rec]        = np.fromfile(f, np.dtype('<u2'), 1)

            if isinstance(n_channels, np.ndarray):
                n_channels = n_channels[0]
            if isinstance(n_samples, np.ndarray):
                n_samples = n_samples[0]

            waveforms = np.reshape(waveforms, (n_channels, n_samples))
            waveforms = (np.float64(waveforms) - 32768) / gain[rec,:] / 1000

            spikes[rec,:,:] = waveforms

    data = {
        'header'     : header,
        'spikes'     : spikes,
        'units'      : 'uV',
        'timestamps' : timestamps,
        'source'     : source,
        'gain'       : gain,
        'thresh'     : thresh,
        'rec_nums'   : recNum,
        'unitID'     : sortedId,
    }

    return data

def load_events(fname,pkg):
    with file(fname,'rb') as f:
        header = read_header(f)

        record_len = 16
        file_len   = os.fstat(f.fileno()).st_size
        n_records  = int((file_len - 1024) / record_len)

        channel    = np.zeros(n_records)
        timestamps = np.zeros(n_records)
        sampleNum  = np.zeros(n_records)
        nodeId     = np.zeros(n_records)
        eventType  = np.zeros(n_records)
        eventId    = np.zeros(n_records)
        rec_nums   = np.zeros(n_records)

        for rec in range(n_records):
            timestamps[rec] = np.fromfile(f, np.dtype('<i8'), 1)
            sampleNum[rec]  = np.fromfile(f, np.dtype('<i2'), 1)
            eventType[rec]  = np.fromfile(f, np.dtype('<u1'), 1)
            nodeId[rec]     = np.fromfile(f, np.dtype('<u1'), 1)
            eventId[rec]    = np.fromfile(f, np.dtype('<u1'), 1)
            channel[rec]    = np.fromfile(f, np.dtype('<u1'), 1)
            rec_nums[rec]   = np.fromfile(f, np.dtype('<u2'), 1)

    data = {
        'header'     : header,
        'channel'    : channel,
        'timestamps' : timestamps,
        'eventType'  : eventType,
        'nodeId'     : nodeId,
        'eventId'    : eventId,
        'rec_nums'   : rec_nums,
        'sampleNum'  : sampleNum,
    }

    return data
