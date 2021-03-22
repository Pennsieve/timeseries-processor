#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from openephys_processor import OpenEphysProcessor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test

from params import params_global

@mock_s3()
@mock_ssm()
@pytest.mark.parametrize("ts_expected", params_global)
def test_openephys(ts_expected):
    init_ssm()

    # init task
    task = OpenEphysProcessor(inputs=ts_expected.inputs)

    # Test OpenEphys Processor
    timeseries_test(task, ts_expected)
