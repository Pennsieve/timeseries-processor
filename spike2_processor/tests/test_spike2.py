#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from spike2_processor import Spike2Processor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test, channels_test

from params import params_global


@mock_ssm
@mock_s3
@pytest.mark.parametrize("ts_expected", params_global)
def test_spike2(ts_expected):
    init_ssm()
    task = Spike2Processor(inputs=ts_expected.inputs)
    # Test Spike2 Processor
    timeseries_test(task, ts_expected)
