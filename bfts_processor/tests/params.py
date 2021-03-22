from base_processor.timeseries.tests import TimeSeriesTest

# -----------------------------
# parameters for global tests
# -----------------------------

params_global = [
  TimeSeriesTest(
    name      = 'template',
    nchannels = 2,
    nsamples  = 12000,
    rate      = 800.0,
    template  = True,
    result    = 'pass',
    inputs    = {
        'file': '/test-resources/sin_wave.bfts'
    }),
  TimeSeriesTest(
    name      = 'simple',
    nchannels = 2,
    nsamples  = 6,
    rate      = 1000.0,
    result    = 'pass',
    inputs    = {
        'file': '/test-resources/simple.bfts'
    }),
  TimeSeriesTest(
    name      ='large_gaps_usec_index',
    nchannels = 2,
    nsamples  = 214000,
    rate      = 1000.0,
    result    = 'pass',
    inputs    = {
        'file': '/test-resources/large_gaps_usec_index.bfts'
    }),
  TimeSeriesTest(
    name      = 'large_gaps_dt_index.bfts',
    nchannels = 2,
    nsamples  = 214000,
    rate      = 1000.0,
    result    = 'pass',
    inputs    = {
        'file': '/test-resources/large_gaps_dt_index.bfts'
    }),
  TimeSeriesTest(
    name      = 'large_gaps_unordered_dt_index',
    nchannels = 2,
    nsamples  = 207126,
    rate      = 1000.0,
    result    = 'pass',
    inputs    = {
        'file': '/test-resources/large_gaps_unordered_dt_index.bfts'
    }),
]

params_append = [
  # no existing channels
  TimeSeriesTest(
    name      = 'large_gaps_unordered_dt_index',
    nchannels = 2,
    nsamples  = 207126,
    rate      = 1000.0,
    result    = 'pass',
    inputs    = {
        'mode': 'append',
        'file': '/test-resources/large_gaps_unordered_dt_index.bfts'
    }),

  # correct channels
  TimeSeriesTest(
    name      = 'simple',
    nchannels = 2,
    nsamples  = 6,
    rate      = 1000.0,
    result    = 'pass',
    inputs    = {
        'mode': 'append',
        'file': '/test-resources/simple.bfts',
        'channels': [
            {
                'id': 'channel-1-id',
                'name': 'Channel-1',
                'rate': 1000,
                'type': 'continuous',
                'unit': 'V',
                'group': 'default',
                'start': 0,
                'end': 6000,
                'lastAnnotation': 123,
                'properties': []
            },
            {
                'id': 'channel-2-id',
                'name': 'Channel-2',
                'rate': 1000,
                'type': 'continuous',
                'unit': 'V',
                'group': 'default',
                'start': 0,
                'end': 6000,
                'lastAnnotation': 123,
                'properties': []
            }
        ]
    }),

  # channels are incorrect format
  TimeSeriesTest(
    name      = 'simple',
    nchannels = 2,
    nsamples  = 6,
    rate      = 1000.0,
    result    = 'fail',
    inputs    = {
        'mode': 'append',
        'file': '/test-resources/simple.bfts',
        'channels': {
            'incorrect format for channels': 'failure'
        }
    }),
]
