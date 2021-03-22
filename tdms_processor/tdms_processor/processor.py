
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

from nptdms import TdmsFile
import numpy as np

class TDMSProcessor(BaseTimeSeriesProcessor):

    def task(self):
        """
        Provides primitive parsing of .tdms files. Returns a TimeSeries object
        which represents the time-series metadata as stored on Pennsieve platform.

        Note #1: this uses npTDMS library which does not support DAQmx format.

        Note #2: this does not properly parse segments, as there were problems
                 where duplicate segments were found (tdms_file.segments). For now,
                 a single segment is expected per channel/object.

        Note #3: increment, n_samples, and length(data) were not consistent
                 for the sample data file I was using, so I'm not sure which value
                 was inconsistent. Right now, I'm trusting len(data) and increment
        """

        # load tdms file
        tdms_file = TdmsFile(self.inputs['file'])

        # find all groups in tdms file
        for g in tdms_file.groups():
            # find all channels in group
            for ch in tdms_file.group_channels(g):

                if not ch.has_data: continue

                # ignore if decimated signal
                decimated_level = ch.property('DecimationLevel')
                if decimated_level != 0:
                    continue

                # important properties in file header
                increment  = ch.property('wf_increment')
                start_time = ch.property('wf_start_time').replace(tzinfo=None)
                unit = ch.properties.get('unit_string', 'V')

                # assumptions:
                #  * increment in seconds
                #  * wf_samples is not accurate; using len(data) instead
                n_samples = ch.data.size

                # get times
                start_time_us = utils.usecs_since_epoch(start_time)

                # length of time
                length_sec = (n_samples-1) * increment
                length_us  = int(round(utils.secs_to_usecs(length_sec)))

                # end time
                end_time_us  = start_time_us + length_us

                # get time range
                timestamps = np.linspace(start_time_us, end_time_us, num=n_samples)
                timestamps = timestamps.astype(int)

                # create channel object
                channel = self.get_or_create_channel(
                        name = str(ch.channel).strip(),
                        unit = str(unit),
                        rate = 1.0/increment,
                        type = 'continuous')

                self.write_channel_data(
                    channel = channel,
                    timestamps = timestamps,
                    values = ch.data
                    )

        self.finalize()
