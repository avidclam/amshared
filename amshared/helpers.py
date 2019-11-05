"""
Tiny useful functions, various topics.
"""
import random
import time


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
    """Converts string to float or int, or returns default.

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
