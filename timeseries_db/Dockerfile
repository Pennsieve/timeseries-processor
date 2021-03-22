# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408 as test

RUN apk add --no-cache --update postgresql-dev

# install requirements
COPY timeseries_db/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# code: processor
COPY timeseries_db/timeseries_db /app/timeseries_db

# code: tests
COPY timeseries_db/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]
