#!/usr/bin/env python

import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from bfts_processor import BFTSProcessor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test

from params import params_global, params_append


@mock_s3()
@mock_ssm()
@pytest.mark.parametrize("ts_expected", params_global)
def test_bfts(ts_expected):
    init_ssm()

    task = BFTSProcessor(inputs=ts_expected.inputs)

    # Test BFTS Processor
    timeseries_test(task, ts_expected)


@mock_s3()
@mock_ssm()
@pytest.mark.parametrize("ts_expected", params_append)
def test_bfts_append(ts_expected):
    init_ssm()

    task = BFTSProcessor(inputs=ts_expected.inputs)

    # Test BFTS Processor
    timeseries_test(task, ts_expected)
