# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81 as test

RUN apk add --no-cache --update postgresql-dev libstdc++

# install requirements
COPY timeseries_db/requirements.txt /app/
RUN  pip install --no-cache-dir -r  /app/requirements.txt

# code: processor
COPY timeseries_db/timeseries_db                       /app/timeseries_db
COPY timeseries_db/tests                               /app/tests
COPY channel_writer_processor/channel_writer_processor /app/channel_writer_processor
COPY channel_writer_processor/run.py                   /app/run.py

# code: tests
COPY channel_writer_processor/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod

RUN apk add --no-cache --update build-base postgresql-dev wget  libstdc++

# Get AWS root cert for securing postgres connections
RUN mkdir -p /root/.postgresql \
  && wget -qO /root/.postgresql/root.crt https://s3.amazonaws.com/rds-downloads/rds-ca-2019-root.pem

# install requirements
COPY timeseries_db/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# code: processor
COPY timeseries_db/timeseries_db                       /app/timeseries_db
COPY channel_writer_processor/channel_writer_processor /app/channel_writer_processor
COPY channel_writer_processor/run.py                   /app/run.py

WORKDIR /app
ENTRYPOINT [""]
