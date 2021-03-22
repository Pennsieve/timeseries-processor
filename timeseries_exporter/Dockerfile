# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408 as test

RUN apk add --no-cache --update \
  --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
  build-base \
  postgresql-dev \
  lapack \
  lapack-dev \
  gfortran

RUN apk add --no-cache --update \
  --repository=http://dl-cdn.alpinelinux.org/alpine/v3.12/community \
  'hdf5' \
  'hdf5-dev'

# install requirements
COPY timeseries_exporter/requirements.txt /app/
RUN pip install  -r /app/requirements.txt

# code: processor
COPY timeseries_db/timeseries_db             /app/timeseries_db
COPY timeseries_db/tests                     /app/tests
COPY timeseries_exporter/timeseries_exporter /app/timeseries_exporter
COPY timeseries_exporter/run.py              /app/run.py

# code: tests
COPY timeseries_exporter/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408 as prod

RUN apk add --no-cache --update \
  --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
  build-base \
  postgresql-dev \
  lapack \
  lapack-dev \
  gfortran \
  wget

RUN apk add --no-cache --update \
    --repository=http://dl-cdn.alpinelinux.org/alpine/v3.12/community/ \
    hdf5 \
    hdf5-dev

# Get AWS root cert for securing postgres connections
RUN mkdir -p /root/.postgresql \
  && wget -qO /root/.postgresql/root.crt https://s3.amazonaws.com/rds-downloads/rds-ca-2019-root.pem

# install requirements
COPY timeseries_exporter/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# code: processor
COPY timeseries_db/timeseries_db             /app/timeseries_db
COPY timeseries_exporter/timeseries_exporter /app/timeseries_exporter
COPY timeseries_exporter/run.py              /app/run.py

WORKDIR /app
ENTRYPOINT [""]
