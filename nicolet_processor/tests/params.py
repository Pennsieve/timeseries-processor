from base_processor.timeseries.tests import TimeSeriesTest, ChannelTest

# ----------------------- channels for test.e -----------------------

channels_01 = [
   ChannelTest(name='Fp1',    nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='Fp2',    nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='F3',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='F4',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='C3',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='C4',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='P3',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='P4',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='O1',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='O2',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='F7',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='F8',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='T3',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='T4',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='T5',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='T6',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='A1',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='A2',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='Fz',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='Cz',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='Pz',     nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='Fpz',    nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='EKG',    nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='Photic', nsamples=307200,     rate=256.0, channel_type='CONTINUOUS'),
   ChannelTest(name='Rate',   nsamples=1200,       rate=1.0,   channel_type='CONTINUOUS'),
   ChannelTest(name='IBI',    nsamples=1200,       rate=1.0,   channel_type='CONTINUOUS'),
   ChannelTest(name='Bursts', nsamples=1200,       rate=1.0,   channel_type='CONTINUOUS'),
   ChannelTest(name='Suppr',  nsamples=1200,       rate=1.0,   channel_type='CONTINUOUS')]

# ----------------------- parametrize -----------------------
params_channel = [
    TimeSeriesTest(name='test.e', nchannels=len(channels_01), channels=channels_01, result='pass',
    inputs = {
    	'file': '/test-resources/test.e'
    }),
]
