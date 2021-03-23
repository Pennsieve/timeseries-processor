# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81  as test

# code: processor
COPY bfts_processor/bfts_processor /app/bfts_processor
COPY bfts_processor/run.py         /app/run.py

# code: tests
COPY bfts_processor/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81  as prod

# code: processor
COPY bfts_processor/bfts_processor /app/bfts_processor
COPY bfts_processor/run.py         /app/run.py

WORKDIR /app
ENTRYPOINT [""]
