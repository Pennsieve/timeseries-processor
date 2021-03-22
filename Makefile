.PHONY: help test build push clean

SERVICE ?=
IMAGE_TAG ?= "local"
S3_PATH = "s3://pennsieve-ops-use1/testing-resources/timeseries-processor/"
TEST_RUN_ID ?= $(shell date +%Y%m%d%H%M%S)

export IMAGE_TAG
export SERVICE
export S3_PATH
export TEST_RUN_ID

ifeq ($(SERVICE), )
	SERVICES = $(shell cat docker-compose*yml | egrep "_(exporter|processor):" | sed 's/\://g' | sort | uniq | xargs)
else
	SERVICES = $(SERVICE)
endif

info:
	@echo "SERVICES:"
	@$(foreach service, $(SERVICES), echo "  * ${service}";)
	@echo "IMAGE_TAG = ${IMAGE_TAG}"

.DEFAULT: help
help:
	@echo "Make Help"
	@echo "make test     - build test image, run tests"
	@echo "make build    - build docker image"
	@echo "make push     - push docker image"
	@echo "make clean    - remove stale docker images"
	@echo "make download - download resources for all tests"

download:
	aws s3 sync $(S3_PATH) ./

test-%:
	@echo "Testing $*"
	TEST_RUN_ID=$(TEST_RUN_ID) IMAGE_TAG=$(IMAGE_TAG) docker-compose build $*
	TEST_RUN_ID=$(TEST_RUN_ID) IMAGE_TAG=$(IMAGE_TAG) docker-compose run $* || { $(MAKE) clean && exit 1; }
	$(MAKE) clean

test: info
	$(MAKE) download
	$(MAKE) test-timeseries_db || exit 1
	$(foreach service, $(SERVICES), $(MAKE) test-$(service) || exit 1;)

build: info
	IMAGE_TAG=$(IMAGE_TAG) docker-compose -f docker-compose-build.yml build $(SERVICE)

push: info
	IMAGE_TAG=$(IMAGE_TAG) docker-compose -f docker-compose-build.yml push $(SERVICE)

clean:
	docker-compose down
	docker-compose rm
