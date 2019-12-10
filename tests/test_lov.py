import pytest
import pandas as pd
import numpy as np
from amshared.lov import TagLoV, which_lov, which_tag


def test_taglov():
    x0 = [('ONE', ['1', 'one']), ('TWO', ['2', 'two'])]  # canonical form
    x1 = (('ONE', '1', 'one'), ('TWO', '2', 'two'))
    x2 = {'ONE': ['1', 'one'], 'TWO': ['2', 'two']}
    x3 = [{'ONE': '1, one'}, {'TWO': ['2', 'two']}]  # requires sep=','
    x4 = [('ONE', ['1', 'one']), ('TWO', {'2': 'numeric', 'two': 'string'})]
    x5 = (('ONE', ['1', 'one']), ('ONE', ['1.1', 'one.one']))  # repeting tags
    x6 = 'just string'

    with pytest.raises(TypeError, match=r"positional"):
        tl = TagLoV()
    assert TagLoV(x0).data == x0
    assert TagLoV(x0).canonical == x0
    assert list(TagLoV(x0).tags) == ['ONE', 'TWO']
    for x in (x1, x2, x3, x4):
        tl = TagLoV(x, sep=',')
        assert tl.data == x0
        assert len(tl.data) == len(tl.misc)
    assert TagLoV(x4).canonical == x4
    assert list(TagLoV(x5).tags) == ['ONE'] * 2
    assert TagLoV(x6).canonical == [(x6, [])]
    tl = TagLoV(x4)
    assert tl.misc == [None, {'2': 'numeric', 'two': 'string'}]
    assert [lov for lov in tl.lovs] == [['1', 'one'], ['2', 'two']]
    tagroll, values = zip(*tl.zip)
    assert tagroll == ('ONE', 'ONE', 'TWO', 'TWO')
    assert values == ('1', 'one', '2', 'two')
    mapped = tl.map(lambda x, **kw: f"{kw.get(x[0])}{1000 * int(x[0])}")
    assert list(mapped)[1][1] == 'numeric2000'


def test_which_zero():
    taglov = TagLoV(None)
    series = pd.Series([0, 5, 2, 30])
    donor = pd.Series(['MISS']*2, index=[1, 3])
    wt = which_tag(series, taglov, na='-', donor=donor, method=None)
    ref_tag = pd.Series(['-', 'MISS', '-', 'MISS'])
    assert wt.equals(ref_tag)


def test_which_equal_numeric():
    taglov = TagLoV([{'zero': [0]},
                     {'5-20': range(5, 21)},
                     {'1-15': range(1, 16)}])
    series = pd.Series([0, 5, 2, 30])
    wl = which_lov(series, taglov.lovs, method=None)
    wt = which_tag(series, taglov, na='-', method=None)
    ref_lov = np.array([1, 2, 3, 0])
    ref_tag = pd.Series(['zero', '5-20', '1-15', '-'])
    assert np.array_equal(wl, ref_lov)
    assert wt.equals(ref_tag)
    donor = pd.Series(['MISS'], index=[3])
    wt = which_tag(series, taglov, na='-', donor=donor, method=None)
    ref_tag = pd.Series(['zero', '5-20', '1-15', 'MISS'])
    assert wt.equals(ref_tag)


def test_which_strings():
    taglov = TagLoV([{'1': 'one'},
                     {'20': 'twenty'},
                     {'?': 'ele, twe'}], sep=',')
    series = pd.Series(['sixty-one', 'twelve', 'twenty', 'twelvety'])
    wt = which_tag(series, taglov, na='-', method=None)
    ref_tag = pd.Series(['-', '-', '20', '-'])
    assert wt.equals(ref_tag)
    wt = which_tag(series, taglov, na='-', method='match')
    ref_tag = pd.Series(['-', '?', '20', '?'])
    assert wt.equals(ref_tag)
    wt = which_tag(series, taglov, na='-', method='startswith')
    ref_tag = pd.Series(['-', '?', '20', '?'])
    assert wt.equals(ref_tag)
    wt = which_tag(series, taglov, na='-', method='contains')
    ref_tag = pd.Series(['1', '?', '20', '?'])
    assert wt.equals(ref_tag)
    wt = which_tag(series, taglov, na='-', method='endswith')
    ref_tag = pd.Series(['1', '-', '20', '-'])
    assert wt.equals(ref_tag)


def test_which_custom():
    taglov = TagLoV([{'1': 'one'},
                     {'20': 'twenty'},
                     {'?': 'ele, twe'}], sep=',')
    series = pd.Series(['sixty-one', 'twelve', 'twenty', 'twelvety'])

    def match_nlast(x, y, n=1):  # n trailing symbols match
        xnp = pd.Series(x).str.slice(-n).to_numpy()
        ynp = pd.Series(y).str.slice(-n).to_numpy()
        return xnp == ynp[:, np.newaxis]

    wt = which_tag(series, taglov, na='-', donor=series,
                   method=match_nlast, n=2)
    ref_tag = pd.Series(['1', 'twelve', '20', '20'])
    assert wt.equals(ref_tag)
    wt = which_tag(series, taglov, na='-', method=match_nlast, n=1)
    ref_tag = pd.Series(['1', '1', '20', '20'])
    assert wt.equals(ref_tag)
