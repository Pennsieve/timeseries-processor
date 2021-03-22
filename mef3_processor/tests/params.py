from base_processor.timeseries.tests import TimeSeriesTest

# -----------------------------
# parameters for channel tests
# -----------------------------

# ----------------------- parametrize -----------------------

params_global = [
	TimeSeriesTest(
		name 	  	= 'sine_wave',
		template        = True,
                nchannels  	= 2,
		nsamples	= 12000,
		rate		= 800.0,
		result    	= 'pass',
		inputs    	= {
			'file': '/test-resources/sine/sine_wave.mefd.gz'
		}),
	TimeSeriesTest(
		name 	  	= '1_9_2017.mefd',
		nchannels  	= 4,
		nsamples	= 4936815,
		rate		= 250.0,
		result    	= 'pass',
                inputs    	= {
			'file': '/test-resources/1_9_2017.mefd.gz'
		}),
]


params_append = [
  # two existing channels, append should create two more.
  TimeSeriesTest(
    name      = '1_9_2017',
    nchannels = 4,
    nsamples  = 4936815,
    rate      = 250.0,
    result    = 'pass',
    inputs    = {
        'mode': 'append',
        'file': '/test-resources/1_9_2017.mefd.gz',
        'channels': [
            {
                'id': 'N:channel:E0-E3',
                'name': 'E0-E3',
                'rate': 250.0,
                'type': 'continuous',
                'unit': 'uV',
                'group': 'default',
                'start': 1483941658410000,
                'end': 1483941658410000,
                'lastAnnotation': 0,
                'properties': []
            },
            {
                'id': 'N:channel:E12-E15',
                'name': 'E12-E15',
                'rate': 250.0,
                'type': 'continuous',
                'unit': 'uV',
                'group': 'default',
                'start': 1483941658410000,
                'end': 1483941658410000,
                'lastAnnotation': 0,
                'properties': []
            }
        ]
    }),
]
