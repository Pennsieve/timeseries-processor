
import numpy as np
import pandas as pd

from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

class BFTSProcessor(BaseTimeSeriesProcessor):
    required_inputs = ['file']

    def task(self):
        file = self.inputs.get('file')

        # read the file in reasonably-sized chunks
        for idx,data in enumerate(pd.read_csv(file, index_col=0, chunksize=10000)):

            # if number, assume index is usecs
            if isinstance(data.index[0], basestring):
                # if string, assume index is datetimeindex.
                index_dt = pd.to_datetime(data.index)
                data.index = index_dt.to_series().apply(utils.usecs_since_epoch)

            # ensure entries are sorted by time
            data.sort_index(inplace=True)

            #infer sample rate
            sample_rate, period = utils.infer_sample_rate(data.index)

            unit = 'uV'
            for ch_index,ch in enumerate(data):

                # create channel
                channel = self.get_or_create_channel(
                    name  = ch.strip(),
                    unit  = unit,
                    rate  = sample_rate,
                    type  = 'continuous')

                channel_data  = data[ch].dropna()
                self.write_channel_data(
                    channel    = channel,
                    timestamps = channel_data.index,
                    values     = channel_data.values
                )

        self.finalize()
