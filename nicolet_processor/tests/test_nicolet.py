#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from nicolet_processor import NicoletProcessor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test, channels_test

from params import params_channel

@mock_s3
@mock_ssm
@pytest.mark.parametrize("ts_expected", params_channel)
def test_channel(ts_expected):
    init_ssm()

    task = NicoletProcessor(inputs=ts_expected.inputs)
    channels_test(task, ts_expected)
