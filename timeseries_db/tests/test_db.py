import numpy as np

from timeseries_db.tests import db_fixture

def test_database(db_fixture):
    db = db_fixture
    db.set_channel({
        'nodeId': 'N:channel:xyz',
        'rate': 10000,  # period of 100
        'type': 'CONTINUOUS'
    })

    chunk1 = np.array([0, 1, 2, 3, 4, 5])
    db.write_continuous(chunk1, start_time=5000)

    chunk2 = np.array([9, 8, 9])
    db.write_continuous(chunk2, start_time=6000)

    result = db.read_channel()

    np.testing.assert_array_equal(result, np.array([
        [5000.0, 0.0],
        [5100.0, 1.0],
        [5200.0, 2.0],
        [5300.0, 3.0],
        [5400.0, 4.0],
        [5500.0, 5.0],
        [6000.0, 9.0],
        [6100.0, 8.0],
        [6200.0, 9.0],
    ]))
