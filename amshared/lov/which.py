from typing import Any, Sequence, Callable, Union, Optional
import pandas as pd
import numpy as np
from .taglov import TagLoV


def equality_matrix(x: np.ndarray, y: np.ndarray):
    return x == y[:, np.newaxis]


def which_lov_pd(series: pd.Series,
                 patterns: Sequence[Sequence[Any]],
                 method: Optional[Union[Callable, str]] = None,
                 **kwargs) -> np.ndarray:
    if method is None:
        method = equality_matrix
    elov = [(i + 1, v) for i, lov in enumerate(patterns) for v in lov]
    if not elov:
        return np.zeros(series.size, int)
    num, value = zip(*elov)
    lov_idx_plus = np.concatenate(([0], num))
    if not callable(method):  # assume name of pd.Series.str method
        ptns = pd.Series(value)
        kwargs['na'] = False
        do_match = getattr(series.str, method)
        mm = ptns.apply(do_match, **kwargs).values
    else:
        mm = method(series.to_numpy(), np.array(value))
    return lov_idx_plus[mm.any(axis=0) + mm.argmax(axis=0)]


def which_tag(series: pd.Series,
              taglov,
              na,
              donor: pd.Series,
              method=None,
              **kwargs
              ):
    if series.empty:
        return series
    if not isinstance(taglov, TagLoV):
        taglov = TagLoV(taglov)
    lov_idx_plus = which_lov_pd(series, taglov.lovs, method, **kwargs)
    tags_plus = np.concatenate(([na], list(taglov.keys())))
    result = pd.Series(tags_plus[lov_idx_plus], index=series.index)
    if isinstance(donor, pd.Series):  # take unmatched values from donor
        unmatched_idx = series.index[~lov_idx_plus.astype(bool)]
        if not unmatched_idx.empty:
            take_idx = unmatched_idx.intersection(donor.index)
            if not take_idx.empty:
                result[take_idx] = donor[take_idx]
    return result
