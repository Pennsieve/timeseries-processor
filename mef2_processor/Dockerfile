# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-ubuntu-test:6-43b7408 as test

# install requirements
COPY mef2_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# setup pymef_lib
COPY mef2_processor/mef         /app/mef
COPY mef2_processor/setup.py    /app/

RUN cd /app/ && \
    python setup.py build && \
    python setup.py install

# code: processor
COPY mef2_processor/mef2_processor /app/mef2_processor
COPY mef2_processor/run.py         /app/run.py

# code: tests
COPY mef2_processor/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-ubuntu:81-86b6e41 as prod

COPY --from=test /usr/local/lib/python2.7/site-packages/Cython                             /usr/local/lib/python2.7/site-packages/
COPY --from=test /usr/local/lib/python2.7/site-packages/cython.py                          /usr/local/lib/python2.7/site-packages/
COPY --from=test /usr/local/lib/python2.7/site-packages/pymeflib.so                        /usr/local/lib/python2.7/site-packages/pymeflib.so

# code: processor
COPY mef2_processor/mef2_processor /app/mef2_processor
COPY mef2_processor/run.py         /app/run.py

WORKDIR /app
ENTRYPOINT [""]
