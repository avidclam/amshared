import pytest
from amshared.lov import TagLoV


def test_namedlov():
    x0 = {'ONE': ['1', 'one'], 'TWO': ['2', 'two']}
    x1 = (('ONE', ['1', 'one']), ('TWO', ['2', 'two']))
    x2 = (('ONE', '1', 'one'), ('TWO', '2', 'two'))
    x3 = [{'ONE': '1, one'}, {'TWO': ['2', 'two']}]  # requires sep=','
    x4 = [{'ONE': ['1', 'one']}, {'TWO': {'2': 'numeric', 'two': 'string'}}]
    with pytest.raises(TypeError, match=r"required positional"):
        TagLoV()
    assert TagLoV(x0).data == x0
    assert TagLoV(x0).export() == [{tg: lv} for tg, lv in x0.items()]
    for x in (x1, x2, x3, x4):
        assert TagLoV(x, sep=',').data == x0
    tglv = TagLoV(x4)
    assert tglv.misc == {'TWO': {'2': 'numeric', 'two': 'string'}}
    assert [lov for lov in tglv.lovs] == [['1', 'one'], ['2', 'two']]
    nameroll, values = zip(*tglv.zip)
    assert nameroll == ('ONE', 'ONE', 'TWO', 'TWO')
    assert values == ('1', 'one', '2', 'two')
    mapped = tglv.map(lambda x, **kw: f"{kw.get(x[0])}{1000 * int(x[0])}")
    assert mapped['TWO'] == 'numeric2000'
