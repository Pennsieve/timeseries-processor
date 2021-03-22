import json
import os
import re
from os.path import exists, realpath
from datetime import datetime
from dateutil import tz
import numpy as np

from pynwb import NWBHDF5IO
import pytest
from psycopg2.extras import NumericRange

from base_processor.tests import setup_processor
from timeseries_db.conn import TimeseriesRange
from timeseries_db.tests import db_fixture
from timeseries_exporter import TimeSeriesExporter


@pytest.fixture(scope='function')
def inputs():
    inputs = {
        "channels": realpath("/test-resources/channels.json"),
        "package_id": 2,
        "user_id": 100
    }
    yield inputs


def test_simple_export(inputs, db_fixture):
    db = db_fixture

    inputs = {
        "channels": realpath("/test-resources/two-channels.json"),
        "package_id": 2,
        "user_id": 100
    }

    # Setup test data
    # ------------------------------------------------------
    with open(inputs["channels"]) as f:
        channels = json.load(f)

        db.set_channel(channels[0])
        ch1_data = np.array([0, 1, 2, 3, 4, 5])
        db.write_continuous(ch1_data, start_time=channels[0]['start'])

        db.set_channel(channels[1])
        ch2_data = np.array([6, 6, 6])
        db.write_continuous(ch2_data, start_time=channels[1]['start'])

    # Run processor
    # ------------------------------------------------------
    task = TimeSeriesExporter(use_ssl=False, inputs=inputs)
    setup_processor(task)
    task.run()

    with NWBHDF5IO(task.nwb_output_path, 'r') as io:
        nwbfile = io.read()
        assert nwbfile.session_start_time == datetime(1970, 1, 1, 0, 0, 0, 5000, tzinfo=tz.UTC)

        assert len(nwbfile.acquisition) == 2

        timeseries = nwbfile.acquisition['Channel 1']
        assert timeseries.unit == 'uV'
        np.testing.assert_array_equal(timeseries.data[:], np.array([0, 1, 2, 3, 4, 5]))
        np.testing.assert_array_equal(timeseries.timestamps, np.array(
            [0.0, 0.0001, 0.0002, 0.0003, 0.0004, 0.0005]))

        timeseries = nwbfile.acquisition['Channel 2']
        assert timeseries.unit == 'V'
        np.testing.assert_array_equal(timeseries.data[:], np.array([6, 6, 6]))
        np.testing.assert_array_equal(timeseries.timestamps, np.array([0.0005, 0.0007, 0.0009]))


def test_complex_export(inputs, db_fixture):
    db = db_fixture

    # Setup test data
    # ------------------------------------------------------
    for (root, _, files) in os.walk("/test-resources/data"):
        for channel_file in files:
            channel, start_time, end_time = channel_file.split('.')[0].split('_')

            db.PG_SESSION.add(TimeseriesRange(
                channel=channel,
                # TODO: pull rate from channels.json
                rate=499.906982421875,
                range=NumericRange(long(start_time), long(end_time)),
                location=channel_file,
                follows_gap=False))

            local_channel_file = os.path.join(root, channel_file)
            db.S3_CLIENT.upload_file(local_channel_file,
                                     db.settings.s3_bucket_timeseries,
                                     channel_file)

            db.PG_SESSION.commit()

    # Run processor
    # ------------------------------------------------------
    task = TimeSeriesExporter(use_ssl=False, inputs=inputs)
    setup_processor(task)
    task.run()

    # Check that the upload key contains at least a one character "directory":
    assert re.search(r"/?[a-zA-Z0-9]+/", task.nwb_upload_key) is not None

    # Check that the NWB file exists on S3:
    task.db.S3_CLIENT.head_object(Bucket=task.settings.storage_bucket, Key=task.nwb_upload_key)

    # And that the asset file was writte to disk:
    assert exists('asset.json')
