import numpy as np
from amshared.islike import *


def gen():
    yield None


samples = (
    None, False, -1, -.5, np.int64(-1), np.uint(10), np.pi, '',
    (None,), {}, [], gen(),
    np.array((-1, 0, .5), dtype=np.float), np.array(('a', 'b', 'c'))
)


functions = (is_iter, is_list, is_dict, is_gen, is_array, like_int, like_float)


def test_islike():
    assert [sum(map(f, samples)) for f in functions] == [7, 1, 1, 1, 3, 3, 2]
