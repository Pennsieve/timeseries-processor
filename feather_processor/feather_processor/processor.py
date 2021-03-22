
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils
import pandas as pd

class FeatherProcessor(BaseTimeSeriesProcessor):

    def task(self):
        """
        Feather format processor.
        """
        # read file
        df = pd.read_feather(self.inputs['file'])
        cols = df.columns

        # set index
        if 'index' not in cols:
            raise Exception(
                    "Expecting column named 'index'; not found")

        df.set_index('index', inplace=True)
        df.index = df.index.to_series().apply(utils.infer_epoch).values

        #infer sample rate
        sample_rate, period = utils.infer_sample_rate(df.index)

        unit = 'uV'
        for ch in cols:
            if str(ch) == 'index':
                continue
            channel = self.get_or_create_channel(
                    name = ch.strip(),
                    unit = unit,
                    rate = sample_rate,
                    type = 'continuous')

            channel_data = df[ch].dropna()
            self.write_channel_data(
                channel = channel,
                timestamps = channel_data.index,
                values = channel_data.values
            )

        self.finalize()
