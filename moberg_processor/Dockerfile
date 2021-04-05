# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:1-5800e81 as test

RUN apk add --no-cache --update libstdc++

# install requirements
COPY moberg_processor/requirements.txt    /app/
RUN  pip install --no-cache-dir -r        /app/requirements.txt

# install tsutils
COPY moberg_processor/tsutils            /app/tsutils
COPY moberg_processor/setup.py           /app/

RUN cd /app/ && \
            python setup.py build && \
            python setup.py install

# code: processor
COPY moberg_processor/moberg_processor   /app/moberg_processor
COPY moberg_processor/run.py             /app/

# code: tests
COPY moberg_processor/tests              /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:1-5800e81 as prod

RUN apk add --no-cache --update libstdc++

COPY --from=test /usr/local/lib/python2.7/site-packages/Cython     /usr/local/lib/python2.7/site-packages/
COPY --from=test /usr/local/lib/python2.7/site-packages/cython.py  /usr/local/lib/python2.7/site-packages/
COPY --from=test /usr/local/lib/python2.7/site-packages/tsutils.so /usr/local/lib/python2.7/site-packages/tsutils.so

# code: processor
COPY moberg_processor/moberg_processor  /app/moberg_processor
COPY moberg_processor/run.py            /app/run.py

WORKDIR /app
ENTRYPOINT [""]
