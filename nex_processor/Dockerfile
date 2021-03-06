# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE BUILDER (WITH NEXUS CREDENTIALS)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81 as test-builder

ARG PENNSIEVE_NEXUS_USER
ARG PENNSIEVE_NEXUS_PW

RUN apk add --no-cache --update libstdc++

# install requirements
COPY nex_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# install packages from Nexus
RUN pip install --user --extra-index-url "https://$PENNSIEVE_NEXUS_USER:$PENNSIEVE_NEXUS_PW@nexus.pennsieve.cc/repository/pypi-prod/simple" neo==0.5.1

# code: processor
COPY nex_processor/nex_processor  /app/nex_processor
COPY nex_processor/run.py         /app/run.py

# code: tests
COPY nex_processor/tests /app/tests

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81 as test

COPY --from=test-builder /app /app
COPY --from=test-builder /root/.local /root/.local

WORKDIR /app
ENTRYPOINT [""]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE BUILDER (WITH NEXUS CREDENTIALS)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod-builder

ARG PENNSIEVE_NEXUS_USER
ARG PENNSIEVE_NEXUS_PW

RUN apk add --no-cache --update libstdc++

# install requirements
COPY nex_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# install packages from Nexus
RUN pip install --user --extra-index-url "https://$PENNSIEVE_NEXUS_USER:$PENNSIEVE_NEXUS_PW@nexus.pennsieve.cc/repository/pypi-prod/simple" neo==0.5.1

# code: processor
COPY nex_processor/nex_processor  /app/nex_processor
COPY nex_processor/run.py         /app/run.py

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod

COPY --from=prod-builder /app /app
COPY --from=prod-builder /root/.local /root/.local

WORKDIR /app
ENTRYPOINT [""]
