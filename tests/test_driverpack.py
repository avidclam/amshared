import pytest
from amshared.driverpack import DriverPack


def test_driverpack_singleton(drvpack):
    dp = DriverPack(drvpack, singleton=True)

    dp.inject_kwargs(x=1)
    dp.inject_kwargs(y=2)
    dp.inject_kwargs(a='one', b='two')
    dp.inject_kwargs(z=3, c='three')  # extra

    fun_inst = dp['fun']
    assert fun_inst is dp['fun']
    dp.pop_kwarg('x')
    assert ' is ' in dp['fun']()  # 'x' not required: driver instance reused

    cls_inst = dp['cls']
    assert cls_inst is dp['cls']
    dp.pop_kwarg('y')
    assert ' means ' in dp['cls']()


def test_driverpack_fails(drvpack):
    dp = DriverPack(drvpack, singleton=False)

    dp.inject_kwargs(x=1)
    dp.inject_kwargs(y=2)
    dp.inject_kwargs(a='one', b='two')
    dp.inject_kwargs(z=3, c='three')  # extra

    fun_inst = dp['fun']
    assert fun_inst is not dp['fun']

    cls_inst = dp['cls']
    dp.pop_kwarg('y')
    with pytest.raises(TypeError, match='y'):
        print(dp['cls'])
    assert ' means ' in cls_inst()


def test_driverpack_example(drvpack):
    dp = DriverPack(drvpack, singleton=True)
    with dp['example'](additional='Some Value') as driver:
        assert driver.env['driver_pack'] is dp
        assert 'example' in driver.env['driver_pack'].driver_keys
        assert 'example' == driver.env['driver_key']
        assert 'Some Value' == driver.env['additional']
