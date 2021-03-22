from base_processor.timeseries.tests import TimeSeriesTest, ChannelTest

# -----------------------------
# parameters for channel tests
# -----------------------------

# ----------------------- test channels -----------------------

channels_00 = [
    # continuous channels
    ChannelTest(name='EKG-1000.0', nsamples=1414172, rate=1000.0, channel_type='CONTINUOUS'),
    ChannelTest(name='BP-1000.0', nsamples=1414172, rate=1000.0, channel_type='CONTINUOUS'),
    ChannelTest(name='RAE-1000.0', nsamples=1414172, rate=1000.0, channel_type='CONTINUOUS'),
    ChannelTest(name='LVP-1000.0', nsamples=1414172, rate=1000.0, channel_type='CONTINUOUS'),
    ChannelTest(name='ANS-5000.0', nsamples=7070856, rate=5000.0, channel_type='CONTINUOUS')
]

# ----------------------- parametrize -----------------------

params_global = [
    TimeSeriesTest(
        name        = 'file2',
        nchannels   = len(channels_00),
        channels    = channels_00,
        result      = 'pass',
        inputs      = {
            'file': [
                '/test-resources/file2.smr',
            ]
        }),
]
