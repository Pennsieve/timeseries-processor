
from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

import neo
import os
import quantities as pq
import numpy as np

class NexProcessor(BaseTimeSeriesProcessor):

    def task(self):
        '''
        NeuroExplorer files typically represent a single channel. This channel
        might have multiple variables that are stored in the file: 0) neuron
        1) event 2) interval 3) waveform 4) pop,vector 5) continuous 6) markers.
        Here we create a the package based on the variables stored in each of the
        associated files in the input argument. Note that 'file' is in fact a
        grouped list of files (all .nex files in uploaded task).
        '''
        fname = self.inputs['file']

        if not isinstance(fname, list):
            fname = [fname]

        for file in fname:
            reader = neo.io.NeuroExplorerIO(filename=str(file))

            # Nex files have a single segment with multiple (analog,spike,event,epoch)
            segment = reader.read_segment(
                                    lazy    = False,
                                    cascade = True)

            # import data
            self.import_neo_continuous(segments=[segment])

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
