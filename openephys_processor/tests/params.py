from base_processor.timeseries.tests import TimeSeriesTest, ChannelTest

# -----------------------------
# parameters for global tests
# -----------------------------

# ----------------------- test channels for  100_ -----------------------

channels_01 = [
    ChannelTest(name='CH1-oe',      nsamples=4146176,     rate=25000.0, channel_type='CONTINUOUS'),
    ChannelTest(name='CH14-oe',     nsamples=4146176,     rate=25000.0, channel_type='CONTINUOUS'),
    ChannelTest(name='CH45-oe',     nsamples=4146176,     rate=25000.0, channel_type='CONTINUOUS'),
    ChannelTest(name='SE1-oe_Ch0',  nsamples=4146176,     rate=25000.0, channel_type='UNIT'),
]

channels_02 = [
    ChannelTest(name='Sin 10Hz',     nsamples=12000,     rate=800.0, channel_type='CONTINUOUS'),
    ChannelTest(name='Sin 20Hz',     nsamples=12000,     rate=800.0, channel_type='CONTINUOUS')
]

# ----------------------- parametrize -----------------------

params_global = [
    # test for individual file
    TimeSeriesTest(
        name        = 'AUX1-oe',
        nchannels   = 1,
        nsamples    = 14788608,
        rate        = 30000.0,
        result      = 'pass',
        inputs      = {
            'file': '/test-resources/100_AUX1.continuous'
        }),
    TimeSeriesTest(
        name        = 'AUX1-oe',
        nchannels   = len(channels_02),
        channels    = channels_02,
        nsamples    = 12000,
        template    = True,
        rate        = 800.0,
        result      = 'pass',
        inputs      = {
            'file': [
                '/test-resources/sin_10.continuous',
                '/test-resources/sin_20.continuous'
        ]}),
    ]
