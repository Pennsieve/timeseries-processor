# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408 as test

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

FROM pennsieve/base-processor-pandas:6-43b7408 as prod

# code: processor
COPY openephys_processor/openephys_processor        /app/openephys_processor
COPY openephys_processor/run.py                     /app/run.py
COPY openephys_processor/tests/openephys_workdir	/app/openephys_workdir

WORKDIR /app
ENTRYPOINT [""]
