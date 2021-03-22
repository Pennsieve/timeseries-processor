
import open_ephys as oe
from datetime import timedelta
from base_processor.timeseries.base import chunks

from base_processor.timeseries import BaseTimeSeriesProcessor
import base_processor.timeseries.utils as utils

class OpenEphysProcessor(BaseTimeSeriesProcessor):

    def upload_continuous(self, fname):
        # get signal data
        data = oe.load_continuous(fname, self.settings.scratch_dir)
        channel_data = data['data']
        channel_name = str(data['header']['channel'])
        header = data['header']
        samples = len(channel_data)
        sample_rate = data['header']['sampleRate']

        # define start_time, end_time and duration of the signal
        # NOTE: timestamps are in samples and relative to when the channel was
        #       created. To get absolute time, timestamps must be converted
        #       to seconds and then added to 'date_created'
        tStart       = data['header']['date_created']
        tStart      += timedelta(seconds=data['timestamps'][0] / data['header']['sampleRate'])
        tDur         = len(data['data']) / data['header']['sampleRate']
        tEnd         = tStart + timedelta(seconds=tDur)

        # convert to usecs and define timestamps
        tStart       = utils.usecs_since_epoch(tStart)
        tEnd         = utils.usecs_since_epoch(tEnd)
        unit = 'uV' # hard-coding to uV for now


        for chunk in chunks(tStart,tEnd, samples):
        # create channel object
            channel = self.get_or_create_channel(
                name  = str(channel_name).strip(),
                unit  = unit,
                rate  = sample_rate,
                type  = 'continuous')

            self.write_channel_data(
                channel    = channel,
                timestamps = chunk.timestamps + data['timestamps'][0]/sample_rate * 1e6,
                values     = channel_data[chunk.start_index : chunk.end_index]
            )

    def upload_spikes(self, fname):
        '''
        upload spikes.

        NOTE: we assume the spikes are presented in chronological order.
        '''
        # get spike data
        data = oe.load_spikes(fname)
        electrode_data = data['spikes']
        electrode_name = '{}-{}'.format(str(data['header']['electrode']), 'oe')
        sample_rate    = data['header']['sampleRate']

        t_start        = utils.infer_epoch(data['header']['date_created']) # convert t_start to usecs
        t_start       += data['timestamps'][0]/sample_rate * 1e6
        timestamps = t_start + data['timestamps']/sample_rate * 1e6

        # Channel_data structure: [n_spikes x n_channels x n_samples]
        n_spikes, n_channels, n_samples = electrode_data.shape
        spike_duration = n_samples / sample_rate * 1e6 #spike dur in uSec

        t_end = t_start + spike_duration

        for j in range(n_channels):
            channel_name = electrode_name+'_Ch{}'.format(j)
            channel = self.get_or_create_channel(
                name  = str(channel_name).strip(),
                unit  = str(data['units']),
                rate  = sample_rate,
                type  = 'unit')

            spike_list = []
            for i in range(n_spikes):
                timestamp = timestamps[i]

                chan_start = min(t_start, timestamp)
                chan_end   = max(t_end, timestamp)

                spike_list.append(self.create_spike(
                    timestamp = timestamp,
                    waveforms = electrode_data[i,[j],:],
                    unit      = int(data['unitID'][i][0])
                ))

            chan_start = int(chan_start[0]) if isinstance(chan_start, list) else int(chan_start)
            chan_end   = int(chan_end[0])   if isinstance(chan_end, list)   else int(chan_end)

            if len(spike_list) > 0:
                # writing spike data to channel and file
                self.write_spike_data(
                    channel       = channel,
                    spikes        = spike_list,
                    nsamples      = n_samples,
                    start         = int(chan_start),
                    end           = int(chan_end)
                )

    def task(self):
        '''
        OpenEphys format processor
        '''
        files = self.inputs['file']

        # place all inputs in list to handle individual input files
        if not isinstance(files, list):
            files = [files]

        for fname in files:
            file_type = oe.get_type(fname)

            if file_type == 'CONTINUOUS':
                self.upload_continuous(fname)
            elif file_type == 'SPIKE':
                self.upload_spikes(fname)
            elif file_type == 'EVENT':
                # TODO: add event support
                pass
            elif file_type in ['EVENTS_MESSAGE', 'OPENEPHYS']:
                pass
            else:
                raise Exception("Unsupported file format: {}".format(fname))

        self.finalize()
