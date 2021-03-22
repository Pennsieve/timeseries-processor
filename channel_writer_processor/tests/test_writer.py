import os
import pytest
import numpy as np

# our module(s)
from channel_writer_processor import ChannelDataWriter, read_continuous_file
from base_processor.tests import setup_processor
from timeseries_db.tests import db_fixture

ch1 = {
    'file': '/test-resources/continuous-1khz.ts.bin',
    'channel': {
        'nodeId': 'N:channel:continuous-1kHz',
        'type': 'CONTINUOUS',
        'name': 'continuous-1khz',
        'rate': 1000,
        'start': 0
    }
}

ch2 = {
    'file': '/test-resources/continuous-123.335Hz.ts.bin',
    'channel': {
        'nodeId': 'N:channel:continuous-123Hz',
        'type': 'CONTINUOUS',
        'name': 'continuous (123.335Hz)',
        'rate': 123.33497779970399,
        'start': 1522429225763934
    }
}

ch3 = {
    'file': '/test-resources/channel-2.ts.bin',
    'channel': {
        'nodeId': 'N:channel:some-channel-id3',
        'type': 'UNIT',
        'name': 'SE1_Ch0',
        'rate': 25000.00,
        'start': 0
    }
}

ch4 = {
    'file': '/test-resources/nev-spikes.ts.bin',
    'channel': {
        'nodeId': 'N:channel:some-channel-id4',
        'type': 'UNIT',
        'name': 'Channel 32',
        'rate': 30000.00,
        'start': 0
    }
}

gaps = {
    'file': '/test-resources/gaps.ts.bin',
    'channel': {
        'nodeId': 'N:channel:some-channel-with-gaps',
        'type': 'CONTINUOUS',
        'name': 'Some channel w/ gaps',
        'rate': 100000,
        'start': 0
    }
}

ch2_append = {
    'append': True,
    'file': '/test-resources/continuous-123.335Hz.ts.bin',
    'channel': {
        'nodeId': 'N:channel:continuous-123Hz',
        'type': 'CONTINUOUS',
        'name': 'continuous (123.335Hz)',
        'rate': 123.33497779970399,
        'start': 1522429225763934
    }
}

params_data = [
    # (file, num values, num gaps, env vars)
    (gaps, 33,      3, {}),
    (ch1,  20123,   0, {}),
    (ch2,  111111,  0, {}),
    (ch3,  455,     0, {}),
    (ch4,  107,     0, {}),
    (ch2_append, 111111, 0, {'WRITE_MODE': 'APPEND'})
]


@pytest.mark.parametrize("inputs, num_values, num_gaps, env", params_data)
def test_writer(inputs, num_values, num_gaps, env, db_fixture):
    os.environ.update(env)

    # init task
    task = ChannelDataWriter(use_ssl=False, inputs=inputs)
    setup_processor(task)

    if inputs.get('append', False):
        # run twice to test appends
        task.run()

    task.run()

    assert task.num_values_written == num_values
    assert task.num_gaps_found == num_gaps

    # Test reading data back in
    if inputs.get('channel').get('type') == 'CONTINUOUS':
        channel_data = task.db.read_channel()
        data = read_continuous_file(inputs['file']).copy()

        # It is not possible to reproduce the `gaps` test data with 100%
        # accuracy from the database because signals that are within a tolerance
        # of 2 * sample_period are considered continuous. Eg the [421, 430, 440]
        # timestamps are stored together in a range as [421, 431, 441].
        if inputs.get('channel').get('nodeId') == 'N:channel:some-channel-with-gaps':
            data[-2, 0] = 431
            data[-1, 0] = 441

        np.testing.assert_array_equal(data, channel_data)

    # TODO - read spike data
    elif inputs.get('channel').get('type') == 'UNIT':
        pass


    task.db.PG_SESSION.close()
