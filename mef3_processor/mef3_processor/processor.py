
# MEF specific modules
from pymeflib import convert_to_raw, read_header
import pymef
from pymef import pymef3_file

# general modules
import numpy as np
import gzip

# internal modules
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils
import mef

class MEF3Processor(BaseTimeSeriesProcessor):

    def task(self):
        fname = self.inputs.get('file')
        max_read_chunk_size = 100000 # TODO: put this in settings

        # file extension is assumed to be .mefd.gz
        directory = mef.extract_directory(fname)

        # find .mefd in directory
        mefd_files = mef.find_mefd(directory)

        for mefd_session in mefd_files:

            # unzip all files
            mef.extract_all(mefd_session)

            # get .timd files within session
            self.LOGGER.info('Reading Session: {}'.format(fname))
            session_header = pymef.read_ts_channel_basic_info(mefd_session, None)

            # iterate through channels
            for ch in session_header:

                channel_name = ch['name']
                start_time = ch['start_time']
                end_time = ch['end_time']
                sample_rate = float(ch['fsamp'])
                voltage_conversion_factor = float(ch['ufact'])
                unit = 'uV' if ch['unit'] == 'microvolts' else ch['unit']
                length = ch['nsamp']

                # create channel if it does not exist. Otherwise, create it
                channel = self.get_or_create_channel(
                    name = str(channel_name).strip(),
                    unit = unit,
                    rate = sample_rate,
                    type = 'CONTINUOUS')

                # chunk channel
                chunk_start = start_time
                while chunk_start < end_time:
                    chunk_end = min(chunk_start + (max_read_chunk_size/sample_rate)*1e6,end_time)
                    data = pymef.read_ts_channels_uutc(mefd_session, None, [channel_name], [[chunk_start,chunk_end]])[0]
                    data = data * voltage_conversion_factor
                    data_nan = np.isnan(data)
                    nan_loc = np.where(data_nan)[0]

                    # if all gaps, skip
                    if np.sum(data_nan)==len(data):
                        pass

                    # if no gaps, upload
                    elif np.sum(nan_loc) == 0:
                        # including all points
                        timestamps = np.linspace(chunk_start, chunk_end, num=len(data))
                        self.write_channel_data(
                            channel     = channel,
                            timestamps  = timestamps,
                            values      = data)

                    # if gaps, split on Nan and upload each continuous segment
                    else:
                        # get start and stop times for all NaN delimited chunks
                        r = []
                        if nan_loc[0] != 0:
                            r.append([0, nan_loc[0]])

                        nan_loc_diff = np.where(np.diff(nan_loc)>1)[0]
                        for i in nan_loc_diff:
                            r.append([nan_loc[i]+1,nan_loc[i+1]])

                        # use temporary start/stop to chunk data
                        for idx in r:
                            tmp_start_time = chunk_start + (idx[0] / sample_rate)*1e6
                            tmp_end_time   = chunk_start + (idx[1] / sample_rate)*1e6
                            tmp_dat        = data[idx[0] : idx[1]]
                            # generating timestamps excluding last point (end time)
                            timestamps     = np.arange(tmp_start_time, tmp_end_time, step=(1/float(sample_rate))*1e6)

                            self.write_channel_data(
                                channel     = channel,
                                timestamps  = timestamps,
                                values      = tmp_dat)

                    # update chunk start
                    chunk_start = chunk_end

        mef.clean(mefd_session)
        self.finalize()
