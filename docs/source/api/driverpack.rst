driverpack
==========

.. automodule:: amshared.driverpack
    :members:

DriverExample
-------------

.. code-block:: python

    from amshared.driverpack import DriverPack, DriverExample

    dp = DriverPack({'example': DriverExample})
    with dp['example'](additional='Some Value') as driver:
        print(driver.env['driver_pack'].driver_keys)
        print(f"Current key is '{driver.env['driver_key']}'")
        print(f"Additional parameter value is '{driver.env['additional']}'")

Will print:

.. code-block:: text

    dict_keys(['example'])
    Current key is 'example'
    Additional parameter value is 'Some Value'


