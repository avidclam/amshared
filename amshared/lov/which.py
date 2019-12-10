from typing import Any, Sequence, Callable, Union, Optional
import pandas as pd
import numpy as np
from .taglov import TagLoV


def which_lov(series: pd.Series,
              patterns: Sequence[Sequence[Any]],
              method: Optional[Union[Callable, str]] = None,
              **kwargs) -> np.ndarray:
    """Which list-of-values does every element of series match first?

    Warnings:
        Order of LoVs is important as only the first match is considered.

    Args:
        series: pandas Series of data with index
        patterns: list of lists-of-values
        method: method to use for pattern matching

            Options are:
             - None: elements of series and values are checked for equality
             - 'match', 'contains', 'startswith', 'endswith': pandas'\
                Series.str.<...> methods used, with arguments passed as kwargs
             - custom function that accepts series, values (flat list of all\
                values across all LoVs) and kwargs
        **kwargs:
            additional keyword arguments to pass to matching functions

    Returns:
        Numeric numpy array
            - 0 means no match found in any of the LoV
            - 1 means some value of LoV #0 matched
            - 2 means some value of LoV #1 matched
            - etc.

    """
    elov = [(i + 1, v) for i, lov in enumerate(patterns) for v in lov]
    if not elov:
        return np.zeros(series.size, int)
    num, value = zip(*elov)
    lov_idx_plus = np.concatenate(([0], num))
    if method is None:
        mm = series.to_numpy() == np.array(value)[:, np.newaxis]
    elif not callable(method):  # assume name of pd.Series.str method
        ptns = pd.Series(value)
        kwargs['na'] = False
        do_match = getattr(series.str, method)
        mm = ptns.apply(do_match, **kwargs).values
    else:
        mm = method(series, value, **kwargs)
    return lov_idx_plus[mm.any(axis=0) + mm.argmax(axis=0)]


def which_tag(series: pd.Series,
              taglov: Union[TagLoV, Any],
              na: Any,
              donor: pd.Series = None,
              method: Optional[Union[Callable, str]] = None,
              **kwargs):
    """Returns tag of the first matched List-of-Values.

    For each element in ``series`` returned is the tag of the list-of-values
    in the dictionary of LoVs ``taglov`` which first matches the element with
    one of its values *OR* value from donor with the same index *OR* ``na``.
    For matching methods see :any:`which_lov`.

    Args:
        series: pandas Series of data
        taglov: tagged list of values: TagLov object or anything that can
            properly initialise it, including None
        na: value to use if element is not matched, last resort
        donor: pandas Series of data to pick in case element is not matched
        method: name of Series.str.<...> method or None for equality check or
            custom function
        **kwargs: arguments to the method

    Returns:
        Series

    """
    if series.empty:
        return series
    if not isinstance(taglov, TagLoV):
        taglov = TagLoV(taglov)
    lov_idx_plus = which_lov(series, taglov.lovs, method, **kwargs)
    tags_plus = np.array((na, *taglov.tags))
    result = pd.Series(tags_plus[lov_idx_plus], index=series.index)
    if isinstance(donor, pd.Series):  # take unmatched values from donor
        unmatched_idx = series.index[~lov_idx_plus.astype(bool)]
        if not unmatched_idx.empty:
            take_idx = unmatched_idx.intersection(donor.index)
            if not take_idx.empty:
                result[take_idx] = donor[take_idx]
    return result
