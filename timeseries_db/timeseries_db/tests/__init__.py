import pytest
from moto import mock_s3, mock_ssm

from base_processor.tests import init_ssm
from base_processor.settings import Logging
from timeseries_db import TimeSeriesDatabase, DatabaseSettings, conn


ssm_ts_values = [
    # timeseries: postgres
    ('test-data-postgres-db',      'postgres'),
    ('test-data-postgres-host',    'postgres'),
    ('test-postgres-password','password'),
    ('test-postgres-port',    '5432'),
    ('test-postgres-user',    'postgres'),

    # timeseries: s3
    ('test-timeseries-s3-bucket', 'timeseries-bucket')
]


def init_timeseries_ssm():
    # default
    init_ssm()
    # timeseries-specific
    init_ssm(values=ssm_ts_values)


@pytest.fixture(scope='function')
def db_fixture():
    with mock_s3(), mock_ssm():
        init_timeseries_ssm()
        db = TimeSeriesDatabase(
            logger=Logging().logger, settings=DatabaseSettings(use_ssl=False)
        )

        db.PG_SESSION.query(conn.TimeseriesRange).delete()
        db.PG_SESSION.query(conn.TimeseriesUnitRange).delete()
        db.PG_SESSION.commit()

        db.S3_CLIENT.create_bucket(Bucket=db.settings.s3_bucket_timeseries)

        try:
            yield db
        finally:
            db.PG_SESSION.close()
