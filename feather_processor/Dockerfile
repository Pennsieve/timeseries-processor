# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408  as test

RUN apk add --no-cache bison \
                       boost-dev \
                       boost-filesystem \
                       boost-program_options \
                       boost-regex \
                       boost-system \
                       boost-unit_test_framework \
                       ca-certificates \
                       cmake \
                       curl \
                       flex \
                       gcc \
                       g++ \
                       git \
                       make \
                       pkgconf \
                       python2-dev

RUN pip install cython

##
## arrow
##
RUN mkdir -p /usr/local/src/arrow && \
    cd /usr/local/src/arrow && \
    curl -fsSL https://github.com/apache/arrow/archive/apache-arrow-0.9.0.tar.gz | tar zx --strip-components=1

RUN cd /usr/local/src/arrow/cpp && \
    cmake \
      -DCMAKE_INSTALL_PREFIX=/opt/arrow \
      -DCMAKE_BUILD_TYPE=Release \
      -DARROW_PYTHON=on \
      . && \
    make -j4 && \
    make install

##
## parquet-cpp
##
RUN mkdir -p /usr/local/src/parquet-cpp && \
    cd /usr/local/src/parquet-cpp && \
    curl -fsSL https://github.com/apache/parquet-cpp/archive/apache-parquet-cpp-1.4.0.tar.gz | tar zx --strip-components=1

RUN cd /usr/local/src/parquet-cpp && \
    cmake \
      -DCMAKE_INSTALL_PREFIX=/opt/parquet-cpp \
      -DCMAKE_BUILD_TYPE=Release \
      -DPARQUET_ARROW=On \
      -DPARQUET_BUILD_TESTS=Off \
      . && \
    make -j4 && \
    make install

##
## pyarrow
##
RUN cd /usr/local/src/arrow/python && \
    pip install -r requirements.txt && \
    ARROW_SOURCE_PATH=/usr/local/src/arrow \
    ARROW_HOME=/opt/arrow \
    ARROW_VERSION=0.9.0 \
    PARQUET_SOURCE_PATH=/usr/local/src/parquet-cpp \
    PARQUET_HOME=/opt/parquet-cpp \
    PARQUET_VERSION=1.4.0 \
    python setup.py build_ext \
      --with-parquet \
      --build-type=release \
      install

ENV LD_LIBRARY_PATH=/opt/arrow/lib:/usr/local/src/arrow/cpp/jemalloc_ep-prefix/src/jemalloc_ep/dist/lib:${LD_LIBRARY_PATH}

# install test env
RUN pip install --no-cache-dir boto3 moto pylint pytest pytest-cov

# install requirements
COPY feather_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

RUN cp -R /usr/local/src/arrow/python/pyarrow/ /usr/lib/python2.7/ && \
    cp -R /usr/local/src/arrow/cpp/build/release/* /usr/lib/

# code: processor
COPY feather_processor/feather_processor  /app/feather_processor
COPY feather_processor/run.py             /app/run.py

# code: tests
COPY feather_processor/tests /app/tests

RUN pip install feather-format

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:6-43b7408 as prod

COPY --from=test /usr/local/src/arrow/python/pyarrow/ /usr/lib/python2.7/
COPY --from=test /usr/local/src/arrow/cpp/build/release/* /usr/lib/

# install requirements
COPY feather_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# code: processor
COPY feather_processor/feather_processor  /app/feather_processor
COPY feather_processor/run.py             /app/run.py

WORKDIR /app
ENTRYPOINT [""]
