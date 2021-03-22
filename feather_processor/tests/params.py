from base_processor.timeseries.tests import TimeSeriesTest, ChannelTest

# -----------------------------
# parameters tests per channel
# -----------------------------

channels_01 = [
   ChannelTest(name='noise',          nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='pulse',          nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='ramp',           nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='sine 1 Hz',      nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='sine 15 Hz',     nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='sine 17 Hz',     nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='sine 50 Hz',     nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='sine 8 Hz',      nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='sine 8.1777 Hz', nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='sine 8.5 Hz',    nsamples=2000, rate=200.0, channel_type='CONTINUOUS'),
   ChannelTest(name='squarewave',     nsamples=2000, rate=200.0, channel_type='CONTINUOUS')]

# -----------------------------
# parameters for global tests
# -----------------------------

params_global = [
   TimeSeriesTest(
    name='test.feather.template',
    nchannels=2,
    nsamples=12000,
    rate=800,
    template=True,
    result='pass',
    inputs = {
        'file': '/test-resources/sin_wave.feather'
    }),

 TimeSeriesTest(
    name='test.feather',
    nchannels=11,
    nsamples=2000,
    rate=200,
    result='pass',
    inputs = {
        'file': '/test-resources/test.feather'
    }),

  TimeSeriesTest(
    name='no_index.feather',
    nchannels=11,
    nsamples=2000,
    rate=400,
    result='fail',
    inputs = {
        'file': '/test-resources/no_index.feather'
    }),

  TimeSeriesTest(
    name='image.feather',
    nchannels=11,
    nsamples=2000,
    rate=400,
    result='fail',
    inputs = {
        'file': '/test-resources/image.feather'
    }),

  TimeSeriesTest(
    name='test.feather',
    nchannels=len(channels_01),
    channels=channels_01,
    result='pass',
    inputs = {
        'file': '/test-resources/test.feather'
    })
]
