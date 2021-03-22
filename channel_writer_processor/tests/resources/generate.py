import numpy as np

def write_data(name, timestamps, values):
    interleaved = np.empty((timestamps.size + values.size), dtype=np.float64)
    interleaved[0::2] = timestamps
    interleaved[1::2] = values

    # append serialized interleaved data to file
    with open('{}.ts.bin'.format(name),'w') as f:
        f.write(interleaved.tobytes())

# gaps (100kHz)
timestamps = np.hstack((
    np.linspace(0,    90, 10),
    np.linspace(150, 240, 10),
    np.linspace(300, 390, 10),
               [421, 430, 440]))
values = np.arange(timestamps.size) * float(timestamps.size)
write_data('gaps', timestamps, values)

# large continuous (1kHz)
timestamps = np.arange(0,20123)*1000
values = np.sin(np.arange(0, 20123)*.01)
write_data('continuous-1khz', timestamps, values)

# large continuous w/ realistic timestamps
# rate: 123.33497779970399Hz
import time
period = 8108
length = 111111
start = 1522429225763934
print "starting time: {:d}".format(start)
timestamps = start + np.arange(length)*period
values = np.arange(length, dtype=np.float64)
write_data('continuous-123.335Hz', timestamps, values)
