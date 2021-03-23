# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81  as test

# code: processor
COPY persyst_processor/persyst_processor /app/persyst_processor
COPY persyst_processor/run.py            /app/run.py

# code: tests
COPY persyst_processor/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod

# code: processor
COPY persyst_processor/persyst_processor /app/persyst_processor
COPY persyst_processor/run.py            /app/run.py

WORKDIR /app
ENTRYPOINT [""]
