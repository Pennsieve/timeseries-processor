
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

import neo
import os
import quantities as pq
import numpy as np

from datetime import datetime

epoch = datetime.utcfromtimestamp(0)

class Spike2Processor(BaseTimeSeriesProcessor):

    def task(self):
        '''
        Spike2 format processor
        '''
        fname = self.inputs['file']

        if not isinstance(fname, list):
            fname = [fname]

        reader = neo.io.Spike2IO( filename = fname[0])

        segments = reader.read_segment(lazy = False, cascade = True,)
        channels = self.import_continuous(segments)

    def import_continuous(self, segments, usec_offset=0):

        for signal in segments.analogsignals:

            # signal info
            channel_name = signal.name.strip()
            sample_rate = float(signal.sampling_rate)
            channel_identifier = '{}-{}'.format(channel_name, sample_rate)

            start_time = long(usec_offset) + long(signal.t_start.rescale(pq.microsecond))
            end_time = long(usec_offset) + long(signal.t_stop.rescale(pq.microsecond))

            samples = len(signal.as_array())

            unit  = str(signal.units.dimensionality)

            timestamps = np.linspace(start_time, end_time, num=samples)
            timestamps = timestamps.astype(int)

            rate = 1e6 / float(timestamps[1] - timestamps[0])


            # write data in chunks that are 10% the size of the full array
            n = int(len(timestamps) * 0.1)
            for i in range(0, len(timestamps)-n, n):
                start = i
                end   = i + n

                tim = timestamps[start : end]
                sig = signal[start : end]

                # write data in the range
                self.write_chunk(tim, sig, channel_identifier, unit, rate)

            # writing any remaining data
            tim = timestamps[i+n : len(timestamps)]
            sig = signal[i+n : len(timestamps)]
            self.write_chunk(tim, sig, channel_identifier, unit, rate)

    def write_chunk(self, timestamps, signal, name='', unit='uV', rate=250):

        channel = self.get_or_create_channel(
                    name     = name,
                    rate     = rate,
                    unit     = unit,
                    type     = 'continuous')

        self.write_channel_data(
                channel    = channel,
                timestamps = timestamps,
                values     = signal.as_array().flatten(),
            )

        self.finalize()
