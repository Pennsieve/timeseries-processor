from base_processor.timeseries.tests import TimeSeriesTest

# -----------------------------
# parameters for global tests
# -----------------------------

params_global = [
  TimeSeriesTest(
    name      = 'persyst-test-3',
    nchannels = 2,
    template  = True,
    nsamples  = 12000,
    result    = 'pass',
    rate      = 800,
    inputs    = {
        'file': [
            '/test-resources/wave_sin.dat',
            '/test-resources/wave_sin.lay'
        ]
    }),
  TimeSeriesTest(
    name      = 'persyst-test-2',
    nchannels = 4,
    nsamples  = 7587,
    result    = 'pass',
    rate      = 250,
    inputs    = {
        'file': [
            '/test-resources/130998627754330000.DAT',
            '/test-resources/130998627754330000.lay'
        ]
    }),
  TimeSeriesTest(
    name      = 'persyst-test',
    nchannels = 35,
    nsamples  = 930749,
    result    = 'pass',
    rate      = 256,
    inputs    = {
        'file': [
            '/test-resources/test-persyst.dat',
            '/test-resources/test-persyst.lay'
        ]
    }),
]
