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
