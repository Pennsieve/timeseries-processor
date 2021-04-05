# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81 as test

RUN apk add --no-cache --update libstdc++

# code: processor
COPY openephys_processor/openephys_processor     /app/openephys_processor
COPY openephys_processor/run.py                  /app/run.py
COPY openephys_processor/tests/openephys_workdir /app/openephys_workdir

# code: tests
COPY openephys_processor/tests                   /app/tests

WORKDIR /app
ENTRYPOINT [""]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod

RUN apk add --no-cache --update libstdc++

# code: processor
COPY openephys_processor/openephys_processor        /app/openephys_processor
COPY openephys_processor/run.py                     /app/run.py
COPY openephys_processor/tests/openephys_workdir	/app/openephys_workdir

WORKDIR /app
ENTRYPOINT [""]
