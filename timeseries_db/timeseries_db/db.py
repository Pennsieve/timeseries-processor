import gzip
import StringIO
import io
import numpy as np
from psycopg2.extras import NumericRange
from sqlalchemy.exc import IntegrityError
from concurrent.futures import ThreadPoolExecutor, as_completed

# pennsieve
from timeseries_db.conn import TimeseriesUnitRange, TimeseriesRange, \
    get_postgres, get_s3_client
import base_processor.timeseries.utils as utils

'''
Pennsieve Time Series Database Interface (Postgres & S3)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Timeseries data is stored in S3 as binary blobs of data values. Timestamps are
not stored in S3, but are implicitly defined by the range and rate of each
timeseries range.

For example, if a channel range starts at 200, ends at 501, and has a rate of
rate of 10000 (period of 100), the data stored in S3 corresponds to timestamps
200, 300, 400, 500.
'''

def compress_data(data):
    '''Compress a byte array.'''
    compressed_data_buffer = StringIO.StringIO()
    with gzip.GzipFile(fileobj=compressed_data_buffer, mode="w") as f:
        f.write(data)
    return compressed_data_buffer.getvalue()


def decompress_data(byte_stream):
    '''
    Decompress a byte stream from S3 into a buffer of bytes.

    It would be better not to read the byte stream into memory,
    but at least we know the size of the data is bounded.
    '''
    with gzip.GzipFile(fileobj=io.BytesIO(byte_stream.read())) as f:
        return f.read()


def sample_period(channel_rate):
    '''
    The sample period of a channel is the amount of time between data
    readings, in microseconds.
    '''
    return long(1e6) / float(channel_rate)


class TimeSeriesDatabase(object):
    def __init__(self, logger, settings):
        pg_engine, pg_session = get_postgres(settings)
        s3_client = get_s3_client()

        self.PG_SESSION = pg_session
        self.PG_ENGINE  = pg_engine
        self.S3_CLIENT  = s3_client
        self.LOGGER     = logger
        self.BATCH_SIZE = settings.timeseries_batch_size_mb * pow(2, 20) / long(8)
        self.settings   = settings

    def set_channel(self, channel):
        self.CHANNEL_ID   = channel['nodeId']
        self.CHANNEL_RATE = channel['rate']
        self.CHANNEL_TYPE = channel['type']

    def write_data_to_s3(self, file_name, data):
        self.S3_CLIENT.put_object(
           Bucket = self.settings.s3_bucket_timeseries,
           Key    = file_name,
           Body   = compress_data(data),
           ContentEncoding = "gzip")

    def read_channel(self):
        '''
        Read entire channel data into memory - read_chunks is more appropriate
        for streaming processing.
        '''
        channel_data = [data for _, data in self.read_chunks()]

        if not channel_data:
            return np.empty((0, 2), dtype=np.float64)

        return np.concatenate(channel_data, axis=0)

    def read_chunks(self):
        '''
        Return an iterator over all chunks for this channel.

        Returns:
            tuple(TimeseriesRange, np.ndarray(shape=(n,2))): A channel range,
            and an N x 2 array containing timestamp/data point pairs.
        '''
        query = self.PG_SESSION \
          .query(TimeseriesRange) \
          .filter_by(channel=self.CHANNEL_ID) \
          .order_by(TimeseriesRange.range)  # TODO: will this produce correct ordering?

        for ts_range in query:

            # TODO: read and return as INTEGERS
            # Recreate timestamps from range start time and sample rate
            timestamps = np.arange(ts_range.range.lower, ts_range.range.upper,
                                   sample_period(ts_range.rate), dtype=np.float64)

            data = self._read_chunk(ts_range)
            yield (ts_range, np.stack([timestamps, data], axis=-1))

    def _read_chunk(self, ts_range):
        self.LOGGER.debug("Reading %s", ts_range)

        resp = self.S3_CLIENT.get_object(
            Bucket=self.settings.s3_bucket_timeseries,
            Key=ts_range.location)

        data = decompress_data(resp['Body'])
        return np.frombuffer(data).byteswap()

    def _write_chunk(self, data, start_time):
        '''
        Write a contiguous chunk of 'continuous' data to the Pennsieve
        time series database. Each chunk will write a single binary
        asset on S3, and a entry in the Postgres DB ranges table.

        Args:
            data:           Numpy array of values
            start_time:     Start time of data, in usecs from epoch

        '''

        # Notes on end_time:
        #  * compute end time using rate & start time
        #  * forcing range [start,end)
        #  * end time is one usec after last valid time-point
        end_time = start_time + (len(data)-1) * (1.0e6/self.CHANNEL_RATE) + 1

        # include timespan in filename
        file_name = "{}_{}_{}.bfts.gz".format(self.CHANNEL_ID, int(start_time), int(end_time))

        # convert data to big endian(inplace) then get the bytes
        formatted_data = data.astype(np.float64).byteswap(True).tobytes()
        self.write_data_to_s3(file_name, formatted_data)

        #infer epoch on start/end times
        start_time = utils.infer_epoch(start_time)
        end_time = utils.infer_epoch(end_time)

        ts_range = TimeseriesRange(
            channel     = self.CHANNEL_ID,
            rate        = self.CHANNEL_RATE,
            range       = NumericRange(start_time, end_time), # [start_time, end_time)
            location    = file_name,
            follows_gap = False) # TODO: remove follows_gap field

        # write range data
        written = False
        self.PG_SESSION.add(ts_range)
        try:
            self.PG_SESSION.commit()
            written = True
        except IntegrityError as e:
            # ignore error when in append mode
            if self.settings.append_mode:
                self.LOGGER.info('Append mode; skipping overlap range: {}'.format(ts_range.range))
                self.PG_SESSION.rollback()
            else:
                raise e
        except Exception as e:
            raise e
        self.PG_SESSION.remove()

        return len(data) if written else 0

    def write_unit_channel(self, data, fname):
        '''
        spikes[0] -> spikes
        spikes[1] -> waveforms
        '''
        spikes    = list(zip(*data)[0])
        waveforms = list(zip(*data)[1])

        start_time = long(spikes[0]['spike'])
        end_time   = long(spikes[-1]['spike'])

        spike_filename  = "{}_{}_{}.bfsk.gz".format(self.CHANNEL_ID, start_time, end_time)
        wf_filename     = "{}_{}_{}.bfwv.gz".format(self.CHANNEL_ID, start_time, end_time)

        # do the binary data writing here (pass the spikes)

        spike_data = ''
        for spike in spikes:
            swapped_spike = spike['spike'].astype(long).byteswap().tobytes() + str(bytearray([spike['unit']]))
            spike_data += swapped_spike

        waveform_data = np.array(waveforms).astype(np.float64).byteswap(True).tobytes()

        self.write_data_to_s3(spike_filename, spike_data)
        self.write_data_to_s3(wf_filename, waveform_data)

        ts_unit_range = TimeseriesUnitRange(
            channel = self.CHANNEL_ID,
            count   = len(spikes),
            range   = NumericRange(start_time, end_time),
            tsindex = spike_filename,
            tsblob  = wf_filename
        )

        written = False
        self.PG_SESSION.add(ts_unit_range)
        try:
            self.PG_SESSION.commit()
            written = True
        except IntegrityError as e:
            if self.settings.append_mode:
                self.LOGGER.info('Append mode; skipping overlap range: {}'.format(ts_range.range))
                self.PG_SESSION.rollback()
            else:
                raise e
        self.PG_SESSION.remove()

        return len(spikes) if written else 0

    def write_continuous(self, data, start_time):
        '''
        Write a contiguous segment of time series data to the Pennsieve
        time series database. The segment is chunked based on size (if necessary).
        Then, asyncronously:
            1) Binary assets are written to S3, and
            2) Index entries are written to Postgres DB.

        Args:
            data:           Numpy array of values
            start_time:     Start time of data, in usecs from epoch

        '''
        # infer epoch start time
        start_time = utils.infer_epoch(start_time)

        with ThreadPoolExecutor(max_workers=self.settings.timeseries_max_write_threads) as e:
            futures = []
            for i, offset in enumerate(xrange(0, len(data), self.BATCH_SIZE)):
                batch_end        = offset + self.BATCH_SIZE
                chunk_start_time = start_time + offset * sample_period(self.CHANNEL_RATE)
                batch_data       = data[offset:batch_end]

                self.LOGGER.debug('Writing ({i:05d}) {ch_id}: start: {start:018d}, size: {size}'.format(
                    i=i, ch_id=self.CHANNEL_ID, start=long(chunk_start_time), size=len(batch_data)))

                # async write
                futures.append(e.submit(
                    fn         = self._write_chunk,
                    start_time = long(chunk_start_time),
                    data       = batch_data
                ))

            # will raise error, if exists
            num_written = sum([f.result() for f in as_completed(futures)])

        return num_written

    def write_unit(self, spikes, waveforms, fname):
        with ThreadPoolExecutor(max_workers=self.settings.timeseries_max_write_threads) as e:
            futures = []
            batch = []

            for idx in range(0, len(spikes)):
                batch.append((spikes[idx], waveforms[idx]))

                if len(batch) == self.BATCH_SIZE:
                    futures.append(e.submit(
                        fn      = self.write_unit_channel,
                        data    = batch,
                        fname    = fname
                    ))
                    batch = []

            if len(batch) > 0:
                futures.append(
                        e.submit(
                        fn      = self.write_unit_channel,
                        data    = batch,
                        fname    = fname
                ))

            num_spikes_written = sum([f.result() for f in as_completed(futures)])

        return num_spikes_written
