import pytest
from amshared.driverpack import DriverPack


def test_driverpack_singleton(drvpack):
    dp = DriverPack(drvpack, singleton=True)

    dp.arginject(x=1)
    dp.arginject(y=2)
    dp.arginject(a='one', b='two')
    dp.arginject(z=3, c='three')  # extra

    fun_inst = dp['fun']
    assert fun_inst is dp['fun']
    dp.argpop('x')
    assert ' is ' in dp['fun']()  # 'x' not required: driver instance reused

    cls_inst = dp['cls']
    assert cls_inst is dp['cls']
    dp.argpop('y')
    assert ' means ' in dp['cls']()


def test_driverpack_fails(drvpack):
    dp = DriverPack(drvpack, singleton=False)

    dp.arginject(x=1)
    dp.arginject(y=2)
    dp.arginject(a='one', b='two')
    dp.arginject(z=3, c='three')  # extra

    fun_inst = dp['fun']
    assert fun_inst is not dp['fun']

    cls_inst = dp['cls']
    dp.argpop('y')
    with pytest.raises(TypeError, match='y'):
        print(dp['cls'])
    assert ' means ' in cls_inst()
