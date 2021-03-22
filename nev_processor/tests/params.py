from base_processor.timeseries.tests import TimeSeriesTest, ChannelTest

# -----------------------------
# parameters for channel tests
# -----------------------------

# ----------------------- test channels -----------------------

channels_00 = [
	# continuous channels
	ChannelTest(name='lfp 1',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 2',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 3',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 4',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 5',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 6',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 7',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 8',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 9',     nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 10',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 11',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 12',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 13',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 14',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 15',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 16',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 17',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 18',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 19',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 20',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 21',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 22',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 23',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 24',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 25',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 26',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 27',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 28',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 29',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 30',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 31',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='lfp 32',    nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='analog 1',  nsamples=10002,  rate=1000.0,   channel_type='CONTINUOUS'),
	ChannelTest(name='raw 1',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 2',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 3',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 4',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 5',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 6',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 7',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 8',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 9',    nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 10',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 11',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 12',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 13',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 14',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 15',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 16',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 17',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 18',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 19',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 20',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 21',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 22',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 23',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 24',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 25',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 26',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 27',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 28',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 29',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 30',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 31',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='raw 32',   nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	ChannelTest(name='analog 2', nsamples=300060, rate=30000.0, channel_type='CONTINUOUS'),
	# spike channels
	ChannelTest(name='Channel 1',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 2',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 3',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 4',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 5',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 6',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 7',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 8',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 9',        nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 10',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 11',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 12',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 13',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 14',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 15',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 16',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 17',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 18',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 19',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 20',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 21',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 22',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 23',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 24',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 25',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 26',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 27',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 28',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 29',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 30',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 31',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
	ChannelTest(name='Channel 32',       nsamples=300060, rate=30000.0,  channel_type='UNIT'),
]

channels_01 = [
       # continuous channels
       ChannelTest(name='Sin 20Hz',     nsamples=15000,  rate=1000.0,   channel_type='CONTINUOUS'),
       ChannelTest(name='Sin 10Hz',     nsamples=15000,  rate=1000.0,   channel_type='CONTINUOUS'),
        ]
       
 # ----------------------- parametrize -----------------------
 
params_global = [
        TimeSeriesTest(
               name            = 'testSineWave',
               nchannels       = 2,
               channels        = channels_01,
               nsamples        = 15000,
               result          = 'pass',
               spikes          = False,
               template        = True,
               inputs          = {
                       'file': [
                           '/test-resources/sin_wave.nev',
                           '/test-resources/sin_wave.ns2',
                       ]
               }),
	TimeSeriesTest(
		name 	  	= 'testData',
		nchannels 	= len(channels_00),
		channels  	= channels_00,
		result    	= 'pass',
		spikes		= True,
		inputs    	= {
			'file': [
			    '/test-resources/testData.nev',
			    '/test-resources/testData.nf3',
			    '/test-resources/testData.ns2',
			    '/test-resources/testData.ns5'
			]
		}),
]
