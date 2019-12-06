import pandas as pd
import numpy as np
from amshared.string import NamedLoV


def equality_matrix(x, y):
    return np.array(x) == np.array(y)[:, np.newaxis]


def which_name(series: pd.Series,
               named_patterns,
               nomatch=None,
               method=None,  # 'match', 'contains' or function
               **kwds):
    if series.empty:
        return series
    if method is None:
        method = equality_matrix
    try:
        if not isinstance(nomatch, str) and len(nomatch) == len(series):
            transfer = True
        else:
            transfer = False
    except TypeError:
        transfer = False
    if not isinstance(named_patterns, NamedLoV):
        named_patterns = NamedLoV(named_patterns)
    if not named_patterns.values:  # Nothing matches
        if transfer:
            return series.copy()
        else:
            return pd.Series([nomatch] * series.size, index=series.index)
    else:
        name_seq, pattern_seq = zip(*named_patterns.zip)
        names = pd.Series([*name_seq, ''] if transfer else [*name_seq, nomatch])
        patterns = pd.Series(pattern_seq)
        if not callable(method):  # assume method of pd.Series.str
            kwds['na'] = False
            do_match = getattr(series.str, method)
            mm = patterns.apply(do_match, **kwds).values
        else:
            mm = method(series, patterns)
        surematch = np.ones_like(mm[0])  # something has to be matched!
        result = names[np.vstack([mm, surematch]).argmax(axis=0)]
        result.index = series.index
        if transfer:  # Transfer values from series to non-matched result
            nomatch_idx = ~mm.any(axis=0)
            if len(nomatch_idx) > 0:
                result[nomatch_idx] = series[nomatch_idx]
        return result
