from base_processor.timeseries.tests import TimeSeriesTest, ChannelTest

channels_00 = [
ChannelTest(name='EEG - ECG', nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - Fp1', nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - O2',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - T5',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - P3',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='HR',        nsamples=1056913,  rate=0.98,  channel_type='CONTINUOUS'),
ChannelTest(name='EEG - LOC', nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - P4',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - ROC', nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - O1',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - Fp2', nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - F7',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - A1',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - F8',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - T3',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - C3',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - F4',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - Pz',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='SpO2',      nsamples=989390,   rate=0.98,  channel_type='CONTINUOUS'),
ChannelTest(name='EEG - T4',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - C4',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='CVP',       nsamples=0,        rate=93.7,  channel_type='CONTINUOUS'),
ChannelTest(name='EEG - T6',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='CVP',       nsamples=13644024, rate=124.9, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - A2',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - Fz',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - F3',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS'),
ChannelTest(name='EEG - Cz',  nsamples=262144,   rate=256.0, channel_type='CONTINUOUS')]

# parametrize
params_channel = [
    TimeSeriesTest(
        name      = 'data.moberg.gz',
        nchannels = len(channels_00),
        channels  = channels_00,
        result    = 'pass',
        inputs    = {
            'file' : '/test-resources/data.moberg.gz'
        })
]
