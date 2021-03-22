
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils
import numpy as np

from nicolet import NicoletFile

class NicoletProcessor(BaseTimeSeriesProcessor):

    def task(self):
        nicolet_file = NicoletFile(self.inputs['file'])

        chan_d = dict()
        for chan_seg in nicolet_file:

            start_time_us = utils.usecs_since_epoch(chan_seg['start'])
            end_time_us = utils.usecs_since_epoch(chan_seg['end'])

            # get timestamps in microseconds
            samples = chan_seg['data'].size
            timestamps = np.linspace(start_time_us, end_time_us, num=samples)
            timestamps = timestamps.astype(int)

            chan_seg.update(dict(
                    timestamps=timestamps)
            )

            # groupg all chunks by channel
            if str(chan_seg['name']) not in chan_d:
                chan_d[str(chan_seg['name'])] = [chan_seg]
            else:
                chan_d[str(chan_seg['name'])].append(chan_seg)

        # iterate through all channel groups and all chunks per channel
        for ch_index, (k,v) in enumerate(chan_d.iteritems()):
            for n, ch in enumerate(v):

                # create channel if it does not exist, otherwise, get it
                channel = self.get_or_create_channel(
                    name  = str(ch['name']).strip(),
                    unit  = ch['units'],
                    rate  = ch['fs'],
                    type  = 'continuous')

                self.write_channel_data(
                    channel = channel,
                    timestamps = ch['timestamps'],
                    values  =   ch['data']
                    )

        self.finalize()
