#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from nev_processor import NevProcessor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test, channels_test

from params import params_global


@mock_ssm
@mock_s3
@pytest.mark.parametrize("ts_expected", params_global)
def test_nev(ts_expected):
    init_ssm()
    task = NevProcessor(inputs=ts_expected.inputs)
    # Test Nev Processor
    timeseries_test(task, ts_expected)
