# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE BUILDER (WITH NEXUS CREDENTIALS)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408 as test-builder

ARG PENNSIEVE_NEXUS_USER
ARG PENNSIEVE_NEXUS_PW

# install requirements
COPY nev_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# install packages from Nexus
RUN pip install --extra-index-url "https://$PENNSIEVE_NEXUS_USER:$PENNSIEVE_NEXUS_PW@nexus.pennsieve.cc/repository/pypi-prod/simple" neo==0.5.1

# TODO: add changes to nexus release
COPY nev_processor/nev_processor/blackrockio.py /usr/local/lib/python2.7/site-packages/neo/io/blackrockio.py

# code: processor
COPY nev_processor/nev_processor  /app/nev_processor
COPY nev_processor/run.py         /app/run.py

# code: tests
COPY nev_processor/tests /app/tests

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81 as test

COPY --from=test-builder /app /app
COPY --from=test-builder /usr/local/lib/python2.7/site-packages/neo /usr/local/lib/python2.7/site-packages/neo

WORKDIR /app
ENTRYPOINT [""]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE BUILDER (WITH NEXUS CREDENTIALS)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod-builder

ARG PENNSIEVE_NEXUS_USER
ARG PENNSIEVE_NEXUS_PW

# install requirements
COPY nev_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# install packages from Nexus
RUN pip install --extra-index-url "https://$PENNSIEVE_NEXUS_USER:$PENNSIEVE_NEXUS_PW@nexus.pennsieve.cc/repository/pypi-prod/simple" neo==0.5.1

# TODO: add changes to nexus release
COPY nev_processor/nev_processor/blackrockio.py /usr/local/lib/python2.7/site-packages/neo/io/blackrockio.py

# code: processor
COPY nev_processor/nev_processor  /app/nev_processor
COPY nev_processor/run.py         /app/run.py

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod

COPY --from=prod-builder /app /app
COPY --from=prod-builder /usr/local/lib/python2.7/site-packages/neo /usr/local/lib/python2.7/site-packages/neo

WORKDIR /app
ENTRYPOINT [""]
