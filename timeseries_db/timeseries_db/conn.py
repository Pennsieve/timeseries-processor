import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import FLOAT, INT8RANGE

import boto3
from botocore.client import Config

Base = declarative_base()
Base.metadata.schema = "timeseries"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Models
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class TimeseriesRange(Base):
    __tablename__ = 'ranges'

    id = Column(Integer, primary_key=True)
    channel = Column(String)
    rate = Column(FLOAT)
    location = Column(String)
    follows_gap = Column(Boolean)

    # Range bounds are [start_time, end_time)
    range = Column(INT8RANGE, unique=True)

    def __str__(self):
        return "TimeseriesRange({channel}, rate={rate}, range={range})" \
            .format(channel=self.channel, rate=self.rate, range=self.range)


class TimeseriesUnitRange(Base):
    __tablename__ = 'unit_ranges'

    id = Column(Integer, primary_key=True)
    channel = Column(String)
    range = Column(INT8RANGE, unique=True)
    count = Column(Integer)
    tsindex = Column(String)
    tsblob = Column(String)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Connections
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_postgres(db_settings):
    connect_args = {"sslmode": "verify-ca"} if db_settings.use_ssl else {"sslmode": "disable"}
    engine = create_engine(
        db_settings.postgres_connection_string, connect_args=connect_args
    )
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    return engine, session


def get_s3_client(endpoint_url=None):
    session = boto3.session.Session()
    if not endpoint_url:
        endpoint_url = os.environ.get('S3_ENDPOINT', None)
    return session.client('s3',
                          config=Config(signature_version='s3v4'),
                          endpoint_url=endpoint_url)
