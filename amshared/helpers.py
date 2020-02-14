import random
import time
from hashlib import blake2s
from .islike import is_iter


def random_retard(min_=1, max_=10):
    """Sleeps for random time, in sec.

    Args:
        min_: Minimum sleep time
        max_: Maximum sleep time

    Returns:
        number of seconds actually slept

    """
    wait_sec = random.uniform(min_, max_)
    time.sleep(wait_sec)
    return wait_sec


def safe_numeric(string, default=0):
    """Converts string to int or float or returns default.

    Args:
        string: string to be converted to numeric
        default: number to return in case of failure

    Returns:
        integer value, if possible, otherwise float or default

    """
    try:
        n = float(string)
        if n == int(n):
            return int(n)
        else:
            return n
    except (ValueError, TypeError):
        return default


def str_hash(s, digest_size=16):
    """Generates hash out of a string.

    Args:
        s: string to find hash for
        digest_size: size of output digest in bytes

    Returns:
        hash hex digest string
    """
    try:
        return blake2s(s.encode('utf-8'), digest_size=digest_size).hexdigest()
    except AttributeError:
        return None


def iter_equal(x, y):
    """Checks if two iterables are of the same size and equal element-wise.

    If arguments are not iterable, performs regular equality check.

    Be careful as comparison will exhaust generators!

    Args:
        x: iterable
        y: iterable

    Returns:
        boolean
    """
    match = True
    if is_iter(x) and is_iter(y):
        yg = (yi for yi in y)
        for xi in x:
            try:
                yi = next(yg)
                match = match and xi == yi
            except StopIteration:  # y is shorter than x
                match = False
        if match:  # check if y is no longer than x
            try:
                yi = next(yg)
                match = False  # successful 'next' means y is longer than x
            except StopIteration:
                pass  # match proved
    else:
        match = x == y
    return match
