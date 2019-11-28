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


def test_driverpack_attributes_empty(drvpack):
    dp = DriverPack(drvpack, singleton=True)
    dp.update(x=1, y=2)
    assert dp.x is None
    assert dp.y is None


def test_driverpack_attributes_none(drvpack):
    dp = DriverPack(drvpack, singleton=True, keys_as_attributes=None)
    dp.update(x=1, y=2)
    assert dp.x == 1
    assert dp.y == 2


def test_driverpack_attributes_list(drvpack):
    dp = DriverPack(drvpack, singleton=True, keys_as_attributes=['x'])
    dp.update(x=1, y=2)
    assert dp.x == 1
    assert dp.y is None


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

    dp.pack.update(x=lambda: 11)
    dp.pack.update(a=lambda: 'eleven')

    fun_inst = dp['fun']
    assert fun_inst() == "'eleven' is 11"

    del dp.pack['a']
    with pytest.raises(TypeError, match='a'):
        fun_inst = dp['fun']

    def multiplied(x, a=2):
        return x * a

    dp.pack.update(mult=multiplied)
    assert dp['mult'] == 22
    dp.update(a=0)
    assert dp['mult'] == 0


def test_driverpack_cascade(drvpack):
    dp = DriverPack(drvpack, singleton=True, autoinject=True)

    dp['x'] = 11
    dp['a'] = 'eleven'

    fun_inst = dp['fun']
    assert fun_inst() == "'eleven' is 11"

    dp.cascade_delete('a')
    assert 'x' in dp
    assert 'fun' not in dp


def test_driverpack_close(drvpack):
    dp = DriverPack(drvpack, singleton=True, autoinject=True)

    dp['content'] = 'Secret'
    box = dp['secret']
    assert box.content == 'Secret'
    del dp['secret']
    assert hasattr(box, 'reveal') is True
    assert hasattr(box, 'content') is False


def test_driverpack_with(drvpack):
    with DriverPack(drvpack, singleton=True, autoinject=True) as dp:
        dp['content'] = 'Secret'
        box = dp['secret']
    assert hasattr(box, 'reveal') is True
    assert hasattr(box, 'content') is False
