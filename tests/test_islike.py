from amshared.islike import *


functions = (is_iter, is_list, is_dict, is_array, like_int, like_float)


def nmatch(f, x):
    return sum(map(f, x))


def test_islike(json_samples):
    assert [nmatch(f, json_samples) for f in functions] == [6, 1, 1, 3, 3, 2]
