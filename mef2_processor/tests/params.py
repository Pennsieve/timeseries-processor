from base_processor.timeseries.tests import TimeSeriesTest

# -----------------------------
# parameters for channel tests
# -----------------------------

# ----------------------- parametrize -----------------------

params_global = [
    TimeSeriesTest(
      name        = 'gaps',
      nchannels   = 5,
      nsamples    = 3206028,
      rate        = 250.0,
      result      = 'pass',
      inputs      = {
          'file': [
              '/test-resources/gaps/power.mef',
              '/test-resources/gaps/E5-E7.mef',
              '/test-resources/gaps/E2-E3.mef',
              '/test-resources/gaps/E10-E12.mef',
              '/test-resources/gaps/E8-E11.mef'
          ]
      }),

    TimeSeriesTest(
      name        = 'gaps',
      nchannels   = 1,
      nsamples    = 7576,
      rate        = 250.0,
      result      = 'pass',
      inputs      = {
          'file': [
              '/test-resources/adjacent/adjacent.mef',
          ]
      }),

    TimeSeriesTest(
        name      = 'sine_wave',
        nchannels = 1,
        nsamples  = 200,
        rate      = 200.0,
        result    = 'pass',
        inputs    = {
            'file': [
                '/test-resources/small/sine_wave.mef',
            ]
        }),

    TimeSeriesTest(
        name      = 'sine_wave_2',
        nchannels = 2,
        nsamples  = 12000,
        template  = True,
        rate      = 800.0,
        result    = 'pass',
        inputs    = {
            'file': [
                '/test-resources/Sin_20Hz.mef',
                '/test-resources/Sin_10Hz.mef',
            ]
        }),

]
