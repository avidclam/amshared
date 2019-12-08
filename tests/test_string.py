import pytest
from amshared import string


def test_split():
    instr = 'This ;is my ; string '
    assert len(string.split(instr, ';')) == 3
    assert string.split(instr, ';')[1] == 'is my'
    assert string.split(instr, None)[0][-1] == ' '
    assert string.split(instr, '$')[0][-1] == 'g'
    lst = string.split(instr, ';', min_=4, pad='exercise')
    expected = 'This is my string exercise'
    assert ' '.join(lst) == expected
    assert ' '.join(string.split(instr, ';', max_=2)) == 'This is my'


def test_namedlov():
    x0 = {'ONE': ['1', 'one'], 'TWO': ['2', 'two']}
    x1 = (('ONE', ['1', 'one']), ('TWO', ['2', 'two']))
    x2 = (('ONE', '1', 'one'), ('TWO', '2', 'two'))
    x3 = [{'ONE': '1, one'}, {'TWO': ['2', 'two']}]  # requires sep=','
    x4 = [{'ONE': ['1', 'one']}, {'TWO': {'2': 'numeric', 'two': 'string'}}]
    with pytest.raises(TypeError, match=r"required positional"):
        string.TagLoV()
    assert string.TagLoV(x0).data == x0
    assert string.TagLoV(x0).export() == [{nm: lv} for nm, lv in x0.items()]
    for x in (x1, x2, x3, x4):
        assert string.TagLoV(x, sep=',').data == x0
    nlv = string.TagLoV(x4)
    assert nlv.misc == {'TWO': {'2': 'numeric', 'two': 'string'}}
    nameroll, values = zip(*nlv.zip)
    assert nameroll == ('ONE', 'ONE', 'TWO', 'TWO')
    assert values == ('1', 'one', '2', 'two')
