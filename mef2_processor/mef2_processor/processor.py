import os
import uuid
import pandas as pd
import numpy as np
import shutil

# MEF specific modules
from pymeflib import convert_to_raw, read_header

# internal modules
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

class MEF2Processor(BaseTimeSeriesProcessor):

    def write_mef_chunk(self, dat, channel, start_time,block_times,block_index,sample_rate):
        start_index = 0
        curr_total_samples = 0
        dat_length = len(dat)

        while start_index < len(dat) and block_index + 1 < len(block_times):

            # get current block start time and number of samples
            tmp_start_time  = block_times.iloc[block_index]['block_start_time']
            tmp_num_samples = block_times.iloc[block_index]['num_samples']

            # compute end time based on block start time and number of samples
            curr_total_samples = curr_total_samples + tmp_num_samples
            computed_end_time  = int(tmp_start_time + tmp_num_samples/sample_rate * 1e6)

            # get next block start time
            next_start_time = block_times.iloc[block_index + 1]['block_start_time']

            curr_total_samples = int(curr_total_samples)

            tmp_dat            = dat[start_index : start_index + curr_total_samples]
            start_index        = start_index + curr_total_samples

            # if start_time of next block is before the end_time of previous block, set end_time correctly
            # This often is a slight shift of 1 us
            if next_start_time < computed_end_time:
                computed_end_time = next_start_time

            # calculate any additional points to add based on current computed end time and current samples
            point_diff      = int(round(((computed_end_time - start_time)/1e6 * sample_rate) - curr_total_samples))
            points_expected = round(((computed_end_time - start_time)/1e6 * sample_rate))

            if point_diff > 0:
                tmp_dat = np.append(tmp_dat,(tmp_dat[len(tmp_dat)-1].repeat(point_diff)))
            elif point_diff < 0:
                tmp_dat = tmp_dat[:point_diff]

            timestamps = np.arange(start_time, computed_end_time, step=(1/float(sample_rate))*1e6)

            # correct timestamp if necessary
            if len(timestamps) - len(tmp_dat) > 0:
                timestamps = timestamps[:-1]

            # check if timestamps and data dimensions match
            if abs(len(timestamps) - len(tmp_dat)) > 2:
                self.LOGGER.info('Error writing block: {}/{}'.format(block_index, len(block_times)))
                self.LOGGER.info('timestamps [{}] and data [{}] dimensions do not match'.format(len(timestamps), len(tmp_dat)))

            self.write_channel_data(
                channel    = channel,
                timestamps = timestamps,
                values     = tmp_dat)

            start_time = next_start_time
            curr_total_samples = 0

            block_index += 1

        # write last block of data
        #
        tmp_start_time  = block_times.iloc[block_index]['block_start_time']
        tmp_num_samples = block_times.iloc[block_index]['num_samples']

        computed_end_time  = int(tmp_start_time + tmp_num_samples/sample_rate * 1e6)
        tmp_dat            = dat[start_index : start_index + tmp_num_samples]

        if len(tmp_dat) > 0:

            timestamps = np.arange(start_time, computed_end_time, step=(1/float(sample_rate))*1e6)

            # correct timestamp if necessary
            if len(timestamps) - len(tmp_dat) > 0:
                timestamps = timestamps[:-1]

            if abs(len(timestamps) - len(tmp_dat)) > 2:
                self.LOGGER.info('Error writing block: {}/{}'.format(block_index, len(block_times)))
                self.LOGGER.info('timestamps [{}] and data [{}] dimensions do not match'.format(len(timestamps), len(tmp_dat)))

            self.write_channel_data(
                channel    = channel,
                timestamps = timestamps,
                values     = tmp_dat)

    def write_data(self, channel, data, start, end, rate):
        timestamps = np.arange(start, end, step=(1/float(rate))*1e6)

        self.write_channel_data(
            channel    = channel,
            timestamps = timestamps,
            values     = data)

    def find_chunks(self, file_path, suffix):
        chunks             = []
        chunk_start_times  = []
        follows_gap_flag   = []
        for f in os.listdir(os.path.dirname(file_path)):
            if f.endswith('_' + suffix + ".raw32"):
                chunks.append(os.path.dirname(file_path) + '/' + f)
                drive, path = os.path.splitdrive(f)
                path, filename = os.path.split(f)

                parts = filename.split('_')
                suf = parts[-1]
                flag = int(parts[-2])
                chunk_start_time = int(parts[-3])

                follows_gap_flag.append(flag)
                chunk_start_times.append(chunk_start_time)

        return zip(chunk_start_times, chunks, follows_gap_flag)

    def clean(self, chunk_files):
        if not isinstance(chunk_files, list):
            f = []; f.append(chunk_files)
            chunk_files = f
        for filename in chunk_files:
            try:
                os.remove(filename)
            except OSError:
                pass

    def task(self):
        fname = self.inputs.get('file')

        if not isinstance(fname, list):
            f = []; f.append(fname)
            fname = f

        # for each mef file, cycle through and read header
        for f in fname:
            file_path = os.path.abspath(f)

            header= read_header(file_path)

            # sample size for all signals
            signal_name = str(header[0]).strip()

            if signal_name == "":
                signal_name = os.path.basename((os.path.splitext(f)[0])).strip()

            # information from the header
            n_samples                 = header[1]
            recording_start_time      = header[2]
            recording_end_time        = header[3]
            sample_rate               = header[4]
            voltage_conversion_factor = header[5]
            length                    = (n_samples - 1) / sample_rate * 1e6
            start_time                = recording_start_time
            end_time                  = recording_end_time #need to use computed time
            unit                      = 'uV'

            # create channel (or get already existing channel)
            channel = self.get_or_create_channel(
                name        = str(signal_name).strip(),
                unit        = unit,
                rate        = sample_rate,
                type        = 'continuous')

            # data
            suffix = str(uuid.uuid4()) # add unique suffix to allow easy removal

            # convert to raw
            convert_to_raw(file_path, suffix)
            extension = len(os.path.splitext(file_path)[1])

            # read in block and sample counts
            csv_fname   = '{}_block_times_{}.csv'.format(file_path[0:-extension],suffix)
            block_times = pd.read_csv(csv_fname)

            # find list of raw files
            time_chunks = self.find_chunks(file_path, suffix)
            time_chunks.sort() # sort by start_time

            # read in raw files and write
            # loop through each raw file, which consists of 2500 blocks each
            for j in range(len(time_chunks)):

                # read in data
                dat = np.fromfile(time_chunks[j][1], dtype=np.dtype('<i4'))
                dat = dat * voltage_conversion_factor

                # find start_time of current file
                start_time = time_chunks[j][0]

                # find current place in mef block info file
                block_info = block_times.loc[block_times['block_start_time'] == start_time]
                block_index = block_info.index[0]

                self.write_mef_chunk(dat, channel, start_time, block_times, block_index, sample_rate)

            chunks = list(zip(*time_chunks)[1]) # get chunk filenames for cleaning workdir
            chunks.append(csv_fname)

            self.clean(chunks)

        self.finalize()
