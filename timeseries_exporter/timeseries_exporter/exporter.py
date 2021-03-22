import json
import os
import os.path
from uuid import uuid4

from datetime import datetime, timedelta
from dateutil import tz

import numpy as np
from pynwb import NWBFile, TimeSeries
from pynwb import NWBHDF5IO
from hdmf.data_utils import AbstractDataChunkIterator, DataChunk
from hdmf.backends.hdf5.h5_utils import H5DataIO

from base_processor import BaseProcessor
from base_processor.settings import Logging
from timeseries_db import TimeSeriesDatabase, DatabaseSettings

ENVIRONMENT = os.environ.get('ENVIRONMENT', "None")
USE_SSL = ENVIRONMENT.lower() != 'local'

class TimeSeriesExporter(BaseProcessor):

    required_inputs = [
        "channels",
        "package_id",
        "user_id",
    ]

    def __init__(self, use_ssl=USE_SSL, *args, **kwargs):
        super(TimeSeriesExporter, self).__init__(*args, **kwargs)
        self.db = TimeSeriesDatabase(
            logger=Logging().logger, settings=DatabaseSettings(use_ssl=use_ssl)
        )
        # NWB file:
        self.nwb_upload_key = None
        self.nwb_output_path = None

    @property
    def channels(self):
        # Try to open as a JSON file, as the base-processor will convert a
        # JSON file into a Python object. If the conversion has taken place,
        # just return the input values, as-is.
        try:
            with open(self.inputs['channels']) as f:
                return json.load(f)
        except:
            return self.inputs['channels']

    @property
    def session_start_time(self):
        return min(c['start'] for c in self.channels)

    @property
    def session_end_time(self):
        return max(c['end'] for c in self.channels)

    # TODO: Add this to base-processor
    def get_file_size(self, key):
        response = self.db.S3_CLIENT.head_object(
            Bucket=self.settings.storage_bucket, Key=key
        )
        file_size = response['ContentLength']
        self.LOGGER.info('{}: size = {}'.format(key, file_size))
        return file_size

    def _create_upload_key(self, user_id, filename):
        """
        Since we are exporting a previously imported file and not an uploaded
        one, `settings.storage_directory` may be empty. If this is the case,
        we can use the first two characters of `settings.job_id` (import ID)
        as a prefix for the key (for namespacing in S3), or failing that,
        `settings.aws_batch_job_id`.

        The final key will be of the form:

            `<user_id>/exports/<import-id>/<filename>`

        Parameters
        ----------
        filename : str
            The name of the file to be included in the generated key.

        Returns
        -------
        str
        """
        if self.settings.storage_directory:
            return os.path.join(self.settings.storage_directory, filename)
        return os.path.join(user_id if user_id else uuid4().get_hex(),
                            "exports",
                            self.settings.job_id,
                            filename)

    def task(self):
        package_id = str(self.inputs['package_id'])
        user_id = str(self.inputs['user_id'])
        description = "NWB output from Pennsieve ({})".format(package_id)

        self.nwb_output_path = "{job}.nwb".format(job=self.settings.aws_batch_job_id)

        nwbfile = NWBFile(
            session_description=description,

            # This needs to be unique, but could be different.
            identifier=package_id,

            # The session is set to the start of the timeseries. All other
            # timestamps in the series are relative to this time.
            session_start_time=datetime.fromtimestamp(0, tz.UTC) + timedelta(
                microseconds=self.session_start_time))

        for acquisition in self.acquisitions():
            nwbfile.add_acquisition(acquisition)

        # Write the data to file
        with NWBHDF5IO(self.nwb_output_path, 'w') as io:
            io.write(nwbfile)

        # Upload to S3:
        self.nwb_upload_key = self._create_upload_key(user_id, self.nwb_output_path)
        self._upload(self.nwb_output_path, self.nwb_upload_key)

        # Generate the asset and upload it.  Since this is exported into a new
        # package, the NWB file is created as a source instead of a processed
        # view.
        file_size = self.get_file_size(self.nwb_upload_key)
        asset = dict(
            bucket=self.settings.storage_bucket,
            key=self.nwb_upload_key,
            type='source',
            size=file_size
        )
        self.publish_outputs("asset", asset)

    def acquisitions(self):
        """
        Build a new acquisition for each channel
        """
        for channel in self.channels:

            self.LOGGER.info("Reading channel {channel}".format(channel=channel['nodeId']))
            self.db.set_channel(channel)

            # Iteratively read timestamps and data.  The S3 assets have to be
            # read twice in order to stream both the data and the timestamps,
            # since they are written separately, and syncronously. Reading them
            # only once would require one of those streams to be read entirely
            # into memory, leading to OOM erros.

            data = H5DataIO(data=ColumnChunkIterator(self.channel_chunk_iterator(channel)),
                            chunks=True,
                            maxshape=(None,))

            timestamps = H5DataIO(data=ColumnChunkIterator(self.timestamp_iterator(channel)),
                                  chunks=True,
                                  maxshape=(None,))

            yield TimeSeries(name=channel['name'],
                             data=data,
                             timestamps=timestamps,
                             unit=channel['unit'])

    def channel_chunk_iterator(self, channel):
        """
        Generator that yields data chunks for each channel
        """
        self.db.set_channel(channel)
        n_written = 0
        for (ts_range, chunk) in self.db.read_chunks():
            self.LOGGER.info("Reading {range}".format(range=ts_range))

            # Drop timestamps and flatten
            data = chunk[:, 1]

            # Indices for this chunk of data start at the beginning of the channel range
            selection = np.s_[n_written : n_written + len(data)]

            yield DataChunk(data=data, selection=selection)

            n_written += len(data)

    def timestamp_iterator(self, channel):
        self.db.set_channel(channel)
        n_written = 0
        for (ts_range, chunk) in self.db.read_chunks():
            self.LOGGER.info("Reading {range}".format(range=ts_range))

            # Drop data and flatten, and convert to seconds (NWB standard unit)
            timestamps = (chunk[:, 0] - self.session_start_time) / 1e6

            # Indices for this chunk of timestamps start at the beginning of the channel range
            selection = np.s_[n_written : n_written + len(timestamps)]

            yield DataChunk(data=timestamps, selection=selection)

            n_written += len(timestamps)


class ColumnChunkIterator(AbstractDataChunkIterator):

    def __init__(self, chunk_iter):
        self.chunk_iter = chunk_iter

    def __iter__(self):
        return self

    def __next__(self):
        return self.chunk_iter.next()

    next = __next__

    @property
    def dtype(self):
        return np.float64

    @property
    def maxshape(self):
        return None

    def recommended_chunk_shape(self):
        return None

    def recommended_data_shape(self):
        return (1,)
