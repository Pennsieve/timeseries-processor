from base_processor.timeseries.tests import TimeSeriesTest

# -----------------------------
# parameters for global tests
# -----------------------------

params_global = [
  TimeSeriesTest(
    name='test.tdms', nchannels=1, nsamples=4760000, rate=20000.0, result='pass',
    inputs = {
        'file': '/test-resources/test.tdms'
    }),
]