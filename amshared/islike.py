"""
Functions that check if something **is** a certain type or behaves **like** one.
"""

from collections.abc import (
    Collection, Iterable, Generator, Mapping, MutableSequence
)


def is_iter(x):
    """Checks if argument is iterable."""
    return isinstance(x, Iterable)


def is_list(x):
    """Checks if argument is a list."""
    return isinstance(x, MutableSequence)


def is_dict(x):
    """Checks if argument is a dictionary."""
    return isinstance(x, Mapping)


def is_gen(x):
    """Checks if argument is a generator."""
    return isinstance(x, Generator)


def is_array(x):
    """Checks if argument is a collection but not a string, list or dict."""
    return isinstance(x, Collection) and not (
            isinstance(x, str) or is_list(x) or is_dict(x)
    )


def like_int(x):
    """Checks if argument behaves like a scalar integer."""
    try:
        result = not (is_iter(x) or isinstance(x, bool) or '.' in repr(x))
        x = 0 - x
        return result
    except TypeError:
        return False


def like_float(x):
    """Checks if argument behaves like a scalar float."""
    try:
        result = not is_iter(x) and '.' in repr(x)
        x = 0 - x
        return result
    except TypeError:
        return False
