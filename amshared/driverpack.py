"""
DriverPack implements simple dependency injection.

Drivers are callables with keyword arguments --- usually classes
or function-generating functions.
Each driver is identified by a key.
Dictionary of key-driver pairs is pack of drivers.

DriverPack is a factory that instantiates drivers on demand
using arguments obtained though ``arg_set`` method.
Only arguments found in a driver's signature are used.

If ``autoinject`` is set, drivers with the same name as missing arguments
are automatically instantiated.

Warning:
     Automatic injection is risky because it relies on naming conventions and
     is prone to circular dependencies!

Exceptions of ``TypeError`` resulting from missing arguments are not caught.

Note:
    If DriverPack's ``singleton`` parameter is True (default),
    driver instances are cached and reused in subsequent calls.
    However, in case the same driver serves multiple keys, each key will get
    separate driver instance.

"""

import collections
import inspect


class _replace_with_driver_key:
    """Marker object to be replaced with driver key during instantiation"""


class _replace_with_dp_instance:
    """Marker object to be replaced with driver pack during instantiation"""


class DriverPack(collections.UserDict):
    """Instantiates drivers on demand using pre-injected arguments.

    Args:
            pack (dict):  dictionary of key-driver pairs
            singleton (bool): if True, driver instances are reused

    """
    driver_key = _replace_with_driver_key
    instance = _replace_with_dp_instance

    def __init__(self, pack, singleton=True, autoinject=False):
        super().__init__()
        self.pack = pack
        self.singleton = singleton
        self.autoinject = autoinject
        self.injected = {}

    def driver_set(self, *_, **kwargs):
        """Sets or adds drivers to the pach.

        Args:
            **kwargs: Keywords and driver classes/ callables.

        Returns:
            ``self``, useful for method chaining.

        """
        self.pack.update(kwargs)
        return self

    def driver_pop(self, key):
        """Removes driver.

        Args:
            key: driver key

        Returns:
            ``self``, useful for method chaining.

        """
        self.pack.pop(key)
        return self

    def arg_set(self, *_, **kwargs):
        """Accepts arguments for future use during driver instantiation.

        Args:
            **kwargs: Arguments to be used for driver instantiation.

        Returns:
            ``self``, useful for method chaining.

        """
        self.injected.update(kwargs)
        return self

    def arg_pop(self, key):
        """Removes previously injected argument.

        Args:
            key: argument key

        Returns:
            ``self``, useful for method chaining.

        """
        self.injected.pop(key)
        return self

    def instantiate(self, key):
        """Instantiates driver given its key.

        Returns:
            driver instance or None, if no driver is set to serve this key

        """
        if key not in self.pack:
            return None
        driver = self.pack[key]
        dynamic_args = {}
        sig = inspect.signature(driver)
        for arg, param in sig.parameters.items():
            if arg in self.injected:
                dynamic_args[arg] = self.injected[arg]
            elif param.default is _replace_with_driver_key:
                dynamic_args[arg] = key
            elif param.default is _replace_with_dp_instance:
                dynamic_args[arg] = self
            elif (self.autoinject and
                  param.default is param.empty and
                  arg in self.pack):  # ok, try autoinject
                dynamic_args[arg] = self.get(arg)
        return driver(**dynamic_args)

    def __missing__(self, key):
        inst = self.instantiate(key)
        if self.singleton and inst is not None:
            self.data[key] = inst
        return inst


class DriverExample:
    def __init__(self,
                 driver_pack=DriverPack.instance,
                 driver_key=DriverPack.driver_key):
        self._env = {'driver_pack': driver_pack, 'driver_key': driver_key}

    @property
    def env(self):
        return self._env

    def __call__(self, **kwargs):
        self._env.update(kwargs)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
