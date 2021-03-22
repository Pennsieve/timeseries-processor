# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-ubuntu-test:6-43b7408 as test

# install requirements
COPY mef3_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# setup pymef_lib
COPY mef3_processor/mef        /app/mef
COPY mef3_processor/setup.py   /app/
COPY mef3_processor/pymef      /app/pymef

RUN cd /app/ && \
    python setup.py build && \
    python setup.py install

# setup pymef
RUN cd /app/pymef && \
    python setup.py build && \
    python setup.py install

# code: processor
COPY mef3_processor/mef3_processor   /app/mef3_processor
COPY mef3_processor/run.py           /app/run.py

# code: tests
COPY mef3_processor/tests            /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-ubuntu:81-86b6e41 as prod

COPY --from=test /usr/local/lib/python2.7/site-packages/Cython                             /usr/local/lib/python2.7/site-packages/
COPY --from=test /usr/local/lib/python2.7/site-packages/cython.py                          /usr/local/lib/python2.7/site-packages/
COPY --from=test /usr/local/lib/python2.7/site-packages/pymef-0.2.0-py2.7-linux-x86_64.egg /usr/local/lib/python2.7/site-packages/
COPY --from=test /usr/local/lib/python2.7/site-packages/pymeflib.so                        /usr/local/lib/python2.7/site-packages/pymeflib.so

# install eggs
RUN easy_install /usr/local/lib/python2.7/site-packages/pymef-0.2.0-py2.7-linux-x86_64.egg

# code: processor
COPY mef3_processor/mef3_processor  /app/mef3_processor
COPY mef3_processor/run.py          /app/run.py

WORKDIR /app
ENTRYPOINT [""]
