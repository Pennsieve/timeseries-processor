# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81 as test

RUN apk add --no-cache --update libstdc++

# install requirements
COPY edf_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# code: processor
COPY edf_processor/edf_processor   /app/edf_processor
COPY edf_processor/run.py          /app/run.py

# code: tests
COPY edf_processor/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod

RUN apk add --no-cache --update gcc musl-dev libstdc++

# install requirements
COPY edf_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r  /app/requirements.txt

# code: processor
COPY edf_processor/edf_processor  /app/edf_processor
COPY edf_processor/run.py         /app/run.py

WORKDIR /app
ENTRYPOINT [""]
