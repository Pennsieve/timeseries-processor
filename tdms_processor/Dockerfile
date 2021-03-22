# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TEST IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas-test:6-43b7408 as test

# install requirements
COPY tdms_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# code: processor
COPY tdms_processor/tdms_processor	/app/tdms_processor
COPY tdms_processor/run.py 		    /app/run.py

# code: tests
COPY tdms_processor/tests /app/tests

WORKDIR /app
ENTRYPOINT [""]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PRODUCTION IMAGE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FROM pennsieve/base-processor-pandas:6-43b7408 as prod

# install requirements
COPY tdms_processor/requirements.txt /app/
RUN  pip install --no-cache-dir -r /app/requirements.txt

# code: processor
COPY tdms_processor/tdms_processor  /app/tdms_processor
COPY tdms_processor/run.py          /app/run.py

WORKDIR /app
ENTRYPOINT [""]
