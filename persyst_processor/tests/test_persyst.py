import os
import boto3
import pytest
from moto import mock_s3
from moto import mock_ssm

# our module(s)
from persyst_processor import PersystProcessor
from base_processor.tests import init_ssm
from base_processor.timeseries.tests import timeseries_test


from params import params_global

@mock_s3
@mock_ssm
@pytest.mark.parametrize("ts_expected", params_global)
def test_channel(ts_expected):
    init_ssm()

    task = PersystProcessor(inputs=ts_expected.inputs)
    timeseries_test(task, ts_expected)
