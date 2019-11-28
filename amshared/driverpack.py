"""
DriverPack implements simple dependency injection.

Drivers are callables with keyword arguments --- usually classes
or function-generating functions.
Each driver is identified by a key.
Dictionary of key-driver pairs is pack of drivers.

DriverPack is a factory that instantiates drivers on demand using as arguments
any data assigned with ``update`` or drivers instantiated earlier
(``singleton`` needs to be True for the latter).
Only arguments found in a driver's signature are used.

If ``autoinject`` is set, drivers with the same keys as missing arguments
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

It is possible to access key values as attributes. List all keys that need to be
accessed as attributes in ``keys_as_attributes`` parameter.
If ``keys_as_attributes`` is None, all ``data`` keys will be accessible
as attributes.

Calling ``close`` on driver instance is attempted on every ``__delitem__``.

When instantiated driver is deleted with ``cascade_delete``, also deleted are
instances of drivers that have given key in their signature.

All instances are deleted (with ``close`` attempted) on ``__exit__``.

"""

import collections
import inspect


class DRIVER_KEY:
    """Marker object to be replaced with driver key during instantiation"""


class DP_INSTANCE:
    """Marker object to be replaced with driver pack during instantiation"""


class DriverPack(collections.UserDict):
    """Instantiates drivers on demand using pre-injected arguments.

    Args:
            pack (dict):  dictionary of key-driver pairs
            singleton (bool): if True, driver instances are reused

    """

    def __init__(self, pack, singleton=True, autoinject=False,
                 keys_as_attributes=()):
        super().__init__()
        self.pack = pack
        self._singleton = singleton
        self._autoinject = autoinject
        self._keys_as_attributes = keys_as_attributes

    def __getattr__(self, item):
        kaa = self._keys_as_attributes
        if (
                (item in self.data or item in self.pack) and
                (kaa is None or item in kaa)
        ):
            return self[item]
        else:
            return None

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
            popped driver

        """
        return self.pack.pop(key)

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
            if arg in self.data:
                dynamic_args[arg] = self.data[arg]
            elif param.default is DRIVER_KEY:
                dynamic_args[arg] = key
            elif param.default is DP_INSTANCE:
                dynamic_args[arg] = self
            elif (
                    self._autoinject and
                    param.default is param.empty and
                    arg in self.pack and
                    not key == arg  # avoid self-dependency
            ):  # ok, try autoinject
                dynamic_args[arg] = self.get(arg)  # __missing__ will fire
        return driver(**dynamic_args)

    def __missing__(self, key):
        inst = self.instantiate(key)
        if self._singleton and inst is not None:
            self.data[key] = inst
        return inst

    def __delitem__(self, key):
        if key in self.data:
            try:
                self.data[key].close()
            except AttributeError:
                pass
            super().__delitem__(key)

    def cascade_delete(self, key):
        """Removes ``self[key]`` and all keys that have this key as argument.

        Args:
            key: key to remove

        Returns:
            self

        """
        if key in self.data:
            # remove everyone who depends on me
            targets = set(self.data.keys()) - {key}
            targets = targets.intersection(set(self.pack.keys()))
            for target in targets:
                sig = inspect.signature(self.pack.get(target))
                if key in sig.parameters:
                    self.cascade_delete(target)
            del self[key]
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        alive = list(self.data.keys())
        for key in alive:
            del self[key]


class DriverExample:
    def __init__(self,
                 driver_pack=DP_INSTANCE,
                 driver_key=DRIVER_KEY):
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
