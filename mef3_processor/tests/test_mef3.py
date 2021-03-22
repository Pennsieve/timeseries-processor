#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from mef3_processor import MEF3Processor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test, channels_test
    
from params import params_global, params_append


@mock_ssm
@mock_s3
@pytest.mark.parametrize("ts_expected", params_global)
def test_mef3(ts_expected):
    init_ssm()
    task = MEF3Processor(inputs=ts_expected.inputs)

    # Test MEF3 Processor
    timeseries_test(task, ts_expected)

@mock_s3()
@mock_ssm()
@pytest.mark.parametrize("ts_expected", params_append)
def test_mef3_append(ts_expected):
    init_ssm()

    task = MEF3Processor(inputs=ts_expected.inputs)

    # Test MEF3 Appen d
    timeseries_test(task, ts_expected)
