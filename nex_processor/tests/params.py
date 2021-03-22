from base_processor.timeseries.tests import TimeSeriesTest, ChannelTest

# -----------------------------
# parameters for channel tests
# -----------------------------

# ----------------------- parametrize -----------------------

params_global = [
        TimeSeriesTest(
		name 	  	= 'Sin Wave',
		nchannels 	= 2,
                template        = True,
		nsamples 	= 15000,
		rate 		= 1000,
		result    	= 'pass',
		inputs    	= {
			'file': [
				'/test-resources/sin_wave_10Hz.nex',
				'/test-resources/sin_wave_20Hz.nex',
			]
		}),
        TimeSeriesTest(
		name 	  	= 'SE-CSC-LFP',
		nchannels 	= 4,
		nsamples 	= 135198,
		rate   		= 2000,
		result    	= 'pass',
		inputs    	= {
			'file': [
				'/test-resources/SE-CSC-LFP-Ch2_.nex',
				'/test-resources/SE-CSC-LFP-Ch3_.nex',
				'/test-resources/SE-CSC-LFP-Ch4_.nex',
				'/test-resources/SE-CSC-LFP-Ch5_.nex'
			]
		}),

	TimeSeriesTest(
		name 	  	= 'SE-CSC-RAW',
		nchannels 	= 4,
		nsamples 	= 2030000,
		rate 		= 30000,
		result    	= 'pass',
		inputs    	= {
			'file': [
				'/test-resources/SE-CSC-RAW-Ch2_.nex',
				'/test-resources/SE-CSC-RAW-Ch3_.nex',
				'/test-resources/SE-CSC-RAW-Ch4_.nex',
				'/test-resources/SE-CSC-RAW-Ch5_.nex'
			]
		}),
]
