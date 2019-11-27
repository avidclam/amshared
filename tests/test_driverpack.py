# TODO: tests for cascade_delete and enter-exit
import pytest
from amshared.driverpack import DriverPack, DRIVER_KEY, DP_INSTANCE


def test_driverpack_singleton(drvpack):
    dp = DriverPack(drvpack, singleton=True, autoinject=False)

    dp.update(x=1)
    dp.update(y=2)
    dp.update(a='one', b='two')
    dp.update(z=3, c='three')  # extra

    fun_inst = dp['fun']
    assert fun_inst is dp['fun']
    del dp['x']
    assert ' is ' in dp['fun']()  # 'x' not required: driver instance reused

    cls_inst = dp['cls']
    assert cls_inst is dp['cls']
    del dp['y']
    assert ' means ' in dp['cls']()


def test_driverpack_fails(drvpack):
    dp = DriverPack(drvpack, singleton=False, autoinject=False)

    dp.update(x=1)
    dp.update(y=2)
    dp.update(a='one', b='two')
    dp.update(z=3, c='three')  # extra

    fun_inst = dp['fun']
    assert fun_inst is not dp['fun']

    cls_inst = dp['cls']
    del dp['y']
    with pytest.raises(TypeError, match='y'):
        print(dp['cls'])
    assert ' means ' in cls_inst()


def test_driverpack_example(drvpack):
    dp = DriverPack(drvpack, singleton=True, autoinject=False)
    with dp['example'](additional='Some Value') as driver:
        assert driver.env['driver_pack'] is dp
        assert 'example' in driver.env['driver_pack'].pack
        assert 'example' == driver.env['driver_key']
        assert 'Some Value' == driver.env['additional']


def test_driverpack_autoinject(drvpack):
    dp = DriverPack(drvpack, singleton=False, autoinject=True)

    dp.driver_set(x=lambda: 11)
    dp.driver_set(a=lambda: 'eleven')

    fun_inst = dp['fun']
    assert fun_inst() == "'eleven' is 11"

    dp.driver_pop('a')
    with pytest.raises(TypeError, match='a'):
        fun_inst = dp['fun']

    def multiplied(x, a=2):
        return x*a

    dp.driver_set(mult=multiplied)
    assert dp['mult'] == 22
    dp.update(a=0)
    assert dp['mult'] == 0
