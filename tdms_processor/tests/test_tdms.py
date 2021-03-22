#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from tdms_processor import TDMSProcessor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test

from params import params_global

@mock_s3
@mock_ssm
@pytest.mark.parametrize("ts_expected", params_global)
def test_success(ts_expected):
    init_ssm()
    task = TDMSProcessor(inputs=ts_expected.inputs)
    timeseries_test(task, ts_expected)
