from amshared import helpers
from datetime import datetime, timedelta


def test_random_retard():
    max_sec = 2
    tolerance = 20  # ms
    time_before = datetime.now()
    retarded = helpers.random_retard(1, max_sec) * 1000
    time_after = datetime.now()
    deltams = (time_after - time_before) / timedelta(milliseconds=1)
    assert deltams - retarded < tolerance
    assert retarded - max_sec * 1000 < tolerance


def test_safe_numeric():
    num = helpers.safe_numeric(3.14)
    assert type(num) == float
    assert num == 3.14
    num = helpers.safe_numeric(3.0)
    assert type(num) == int
    assert num == 3
    num = helpers.safe_numeric('3.14')
    assert type(num) == float
    assert num == 3.14
    num = helpers.safe_numeric('3.00')
    assert type(num) == int
    assert num == 3
    num = helpers.safe_numeric('Number 3.00')
    assert type(num) == int
    assert num == 0
    num = helpers.safe_numeric('Number 3.00', 3)
    assert type(num) == int
    assert num == 3
