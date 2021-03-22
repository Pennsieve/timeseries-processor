
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

import neo
import os
import quantities as pq
import numpy as np

from datetime import datetime

epoch = datetime.utcfromtimestamp(0)

# NSx header data types
HEADER_DTYPE = np.dtype([
                      ('type',          'a8'),
                      ('spec',          'a2'),
                      ('hdr_bytes',     np.uint32),
                      ('label',         'a16'),
                      ('comments',      'a200'),
                      ('application',   'a52'),
                      ('timestamp',     np.uint32),
                      ('period',        np.uint32),
                      ('time_res',      np.uint32),
                      ('year',          np.uint16),
                      ('month',         np.uint16),
                      ('dweek',         np.uint16),
                      ('day',           np.uint16),
                      ('hour',          np.uint16),
                      ('min',           np.uint16),
                      ('sec',           np.uint16),
                      ('mill',          np.uint16)])

class NevProcessor(BaseTimeSeriesProcessor):

    def task(self):
        '''
        Nev format processor -- Ripple / Blackrock
        '''
        fname = self.inputs['file']

        if not isinstance(fname, list):
            fname = [fname]

        # read file
        basename = os.path.splitext(fname[0])[0]
        reader = neo.io.BlackrockIO(basename)
        block = reader.read_block(
                              lazy           = False,
                              cascade        = True,
                              load_events    = True,
                              load_waveforms = True,
                              channels       = 'all',
                              units          = 'all',
                              nsx_to_load    = 'all')

        if block.rec_datetime is not None:
            recording_time = block.rec_datetime
        else:
            recording_time = self.get_time_from_header(fname)

        # if time not found
        if recording_time is None:
            recording_time = epoch

        usec_offset = utils.usecs_since_epoch(recording_time)

        # import continuous signals
        self.import_neo_spiketrain(block, usec_offset=usec_offset)
        self.import_neo_continuous(segments=block.segments, usec_offset=usec_offset)

        self.finalize()

    def import_neo_continuous(self, segments, usec_offset=0):
        '''
        Import neo continuous signals.
        Notes:
         - Assumes rate is consistent for same channel across segments

             TODO: investigate rate error with large sampling rates
        '''
        for segment in segments:
            # find all continuous data
            for signal in segment.analogsignals:

                # signal info
                channel_name = signal.name.strip()
                sample_rate = float(signal.sampling_rate)
                channel_identifier = channel_name

                start_time = long(usec_offset) + long(signal.t_start.rescale(pq.microsecond))
                end_time = long(usec_offset) + long(signal.t_stop.rescale(pq.microsecond))

                samples = len(signal.as_array())

                unit  = str(signal.units.dimensionality)

                timestamps = np.linspace(start_time, end_time, num=samples)
                timestamps = timestamps.astype(int)

                rate = 1e6 / (float(timestamps[-1] - timestamps[0])/float(len(timestamps)))

                # create channel, get it if it already exists
                channel = self.get_or_create_channel(
                        name = channel_identifier,
                        rate = rate,
                        unit = unit,
                        type = 'continuous')

                self.write_channel_data(
                    channel    = channel,
                    timestamps = timestamps,
                    values     = signal.as_array().flatten(),
                )

    def import_neo_spiketrain(self, block, usec_offset=0):
        """
        Import neo spike train data

        Notes:
         - Assumes data exists within Block (neo)

        """
        channels = {}
        for unit in block.list_units:

            # unit number
            unit_id = int(unit.annotations.get('unit_id', 0))
            channel_id = unit.annotations.get('ch_idx', 0)

            if channel_id not in channels:
                channels[channel_id] = {'node': None, 'spikes': []}

            node = channels[channel_id]['node']
            channel_name = unit.channel_index.channel_names

            if node is not None and channel_name != node.name:
                message = "Unit's channel name [{}] does not match"\
                        " channel's name [{}]".format(channel_name, node.name)
                self.LOGGER.error(message)
                raise Exception(message)

            for spiketrain in unit.spiketrains:
                if spiketrain.name != unit.name:
                    message = 'NEV Processor Error: SpikeTrain is associated'\
                                ' with the wrong Unit'
                    self.LOGGER.error(message)
                    raise Exception(message)

                # ensure all time units in the SpikeTrain are in microseconds
                spiketrain = spiketrain.rescale(pq.microsecond)

                start_time = long(usec_offset) + long(spiketrain.t_start)
                end_time = long(usec_offset) + long(spiketrain.t_stop)

                sampling_rate = float(spiketrain.sampling_rate.rescale(pq.hertz))
                spike_duration = long(spiketrain.spike_duration.rescale(pq.microsecond))

                waveform_unit = str(spiketrain.waveforms.units.dimensionality)

                node = self.get_or_create_channel(
                            name  = str(channel_name).strip(),
                            rate  = sampling_rate,
                            unit  = waveform_unit,
                            type  = 'unit')

                timestamps = pq.Quantity(usec_offset, pq.microsecond) + spiketrain
                waveforms  = spiketrain.waveforms

                for spike in zip(timestamps, waveforms):
                    channels[channel_id]['spikes'].append(
                        self.create_spike(
                            timestamp = spike[0],
                            waveforms = spike[1],
                            unit      = unit_id
                        ))

            if node is not None:
                node.__dict__.update()
                channels[channel_id]['node'] = node

        for channel in channels.values():
            spikes = channel['spikes']
            chan = channel['node']
            # assumming all waveforms in channel contain same number of samples
            nsamples = len(spikes[0].waveforms[0])
            self.write_spike_data(
                channel  = chan,
                spikes   = spikes,
                nsamples = nsamples
            )

    def get_time_from_header(self, fname):
        # get first NSx file and read its header
        try:
            f = next(obj for obj in fname if '.ns' in obj)
        except:
            return None

        header = np.fromfile(f, dtype=HEADER_DTYPE, count=1)[0]

        date = (header['year'],
                header['month'],
                header['day'],
                header['hour'],
                header['min'],
                header['sec'])

        # TODO: add milliseconds

        date = datetime(*date)

        return date




