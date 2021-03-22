
# internal modules
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

import moberg

import os
import numpy as np

# global
PATIENT_FILENAME = 'patient.info'

class MobergProcessor(BaseTimeSeriesProcessor):

    def task(self):
        fname = self.inputs.get('file')

        total_files = moberg.extract_files(fname)
        files = total_files['files']
        patient_files = filter(lambda x: os.path.basename(x) == PATIENT_FILENAME, files)

        if patient_files:
            patient_file = patient_files[0]
            # TODO: use patient data for concept/property creation, etc.
            data = moberg.process_patient_file(patient_file)

        sources = moberg.parse_patient_files(files)
        sources_series = filter(lambda x: x.type in ['SampleSeries','Numeric'], sources)

        sample_intervals = {}
        for src in sources_series:
            for signal in src.get_data():
                sample_interval = signal.sample_interval

                key_base = '{}-{}'.format(src.name, signal.name)
                if key_base not in sample_intervals:
                    sample_intervals[key_base] = np.array([])

                interval, is_new_rate = self.match_interval(sample_interval, sample_intervals[key_base])

                if is_new_rate:
                    sample_intervals[key_base] = np.append(sample_intervals[key_base], interval)

                sampling_rate_secs = 1.0e6/interval
                start_time = signal.start

                # compute end_time because of rate rounding
                end_time = signal.start+signal.length*interval

                channel = self.get_or_create_channel(
                            name        = signal.name,
                            unit        = src.units,
                            rate        = sampling_rate_secs,
                            type        = 'continuous')

                timestamps = np.arange(start_time, end_time, step=(1/float(sampling_rate_secs))*1e6)

                self.write_channel_data(
                    channel    = channel,
                    timestamps = timestamps,
                    values     = signal.data,
                )

        self.finalize()

        # cleanup extracted files
        moberg.cleanup(total_files['cleanup-resources'])

    def match_interval(self, interval, existing_intervals):
        """
        Moberg series can shift their sampling rate block-to-block. This is either a big shift, or a small
        shift in sampling interval. As frequency does change, we need to ensure those different
        frequencies are on different channels. However! Sometimes, the shift in sampling interval
        is so small such that it should be grouped with existing data on the same channel. For example,
        the sampling interval for one block may be 1.0001Hz and another .9998Hz.
        """
        interval_diff_thresh = 0.02 # percent difference

        if len(existing_intervals) == 0:
            # return (interval, new_rate?)
            return interval, True

        percent_diff = np.abs(interval - existing_intervals) * 1.0 / existing_intervals
        matches = existing_intervals[percent_diff < interval_diff_thresh]
        new_rate = False

        if len(matches)>0:
            # return (interval, new_rate?)
            return matches[0], False
        else:
            # return (interval, new_rate?)
            return interval, True
