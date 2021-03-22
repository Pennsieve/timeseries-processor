#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from moberg_processor import MobergProcessor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test, channels_test


from params import params_channel

@mock_ssm
@mock_s3
@pytest.mark.parametrize("ts_expected", params_channel)
def test_moberg(ts_expected):
    init_ssm()

    # Test Moberg Processor
    task = MobergProcessor(inputs=ts_expected.inputs)
    channels_test(task, ts_expected)
