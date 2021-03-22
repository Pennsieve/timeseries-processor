# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408 as test

# code: processor
COPY nicolet_processor/nicolet_processor   /app/nicolet_processor
COPY nicolet_processor/run.py         	   /app/run.py

# code: tests
COPY nicolet_processor/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:6-43b7408 as prod

# code: processor
COPY nicolet_processor/nicolet_processor /app/nicolet_processor
COPY nicolet_processor/run.py            /app/run.py

WORKDIR /app
ENTRYPOINT [""]
