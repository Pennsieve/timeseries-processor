import time
import numpy as np
import pandas as pd

period = 1000
length = 214000

# signals
sin  = np.sin(np.arange(0,length)*0.01)
incr = np.linspace(0,100, length, dtype=np.float)

cur_index = 0
index = np.array([])

while len(index) < length:
    chunk_length = np.random.randint(1000, 5000)
    span = np.arange(cur_index, cur_index+chunk_length)
    gap = np.random.randint(1000,5000)
    cur_index = cur_index + chunk_length + gap
    index = np.hstack((index, span))[:length]

index = np.array(index*period + time.time()*1e6, dtype=long)

df = pd.DataFrame(index=index, data={'sin':sin, 'incr':incr})
df.index.name = 'timestamp'

df.to_csv('large_gaps_usec_index.bfts')
print df.head(10)

from pennsieve.utils import usecs_to_datetime
df.index = [usecs_to_datetime(x) for x in df.index.to_series()]

df.to_csv('large_gaps_dt_index.bfts')
print df.head(10)