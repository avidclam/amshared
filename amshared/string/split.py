from typing import List


def split(string: str, sep=None, min_=None, max_=None, pad='') -> List:
    """Splits string into list with control over number of elements.

    Args:
        string: str to stplit
        sep: separator to use for .split(sep)
        min_: minimum number of elements in list, use ``pad`` to fill in
        max_: maximum number of elements in the resulting list
        pad: value to fill in

    Returns:
        List of str

    """
    if sep is None:
        parts = [string]
    elif sep in string:
        parts = [s.strip() for s in string.split(sep)]
    else:
        parts = [string.strip()]
    if isinstance(min_, int) and min_ > len(parts):
        result = parts + [pad] * (min_ - len(parts))
    else:
        result = parts
    if isinstance(max_, int):
        result = result[:max_]
    return result
