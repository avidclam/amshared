"""
DriverPack implements simple explicit dependency injection.

Drivers are callables with keyword arguments.
Each driver is identified by a key.
Dictionary of key-driver pairs is an iopack of drivers.

DriverPack is a factory that instantiates drivers on demand
using arguments obtained though ``arginject`` method.
Only arguments found in a driver's signature are used.

Exceptions of ``TypeError`` resulting from missing arguments are not caught.

Note:
    If DriverPack's ``singleton`` parameter is True (default),
    driver instances are cached and reused in subsequent calls.
    However, in case the same driver serves multiple keys, each key will get
    separate driver instance.

"""

import collections
import inspect


class DriverPack(collections.UserDict):
    """Instantiates drivers on demand using pre-injected arguments.

    Args:
            pack (dict):  dictionary of key-driver pairs
            singleton (bool): if True, driver instances are reused

    """
    def __init__(self, pack, singleton=True):
        super().__init__()
        self.pack = pack
        self.singleton = singleton
        self.injarg = {}

    @property
    def driverkeys(self):
        return self.pack.keys()

    def arginject(self, *_, **kwarg):
        """Accepts arguments for future use in driver instantiation.

        Args:
            **kwarg: Arguments to be used for driver instantiation.

        Returns:
            ``self``, useful for method chaining.

        """
        self.injarg.update(kwarg)
        return self

    def argpop(self, argkey):
        """Removes previously injected argument.

        Args:
            argkey: argument key

        Returns:
            ``self``, useful for method chaining.

        """
        self.injarg.pop(argkey)
        return self

    def instantiate(self, key):
        """Instantiates driver given its key.

        Returns:
            driver instance or None, if no driver is set to serve this key

        """
        if key not in self.pack:
            return None
        factory = self.pack[key]
        sig = inspect.signature(factory)
        args = {k: v for k, v in self.injarg.items() if k in sig.parameters}
        return factory(**args)

    def __missing__(self, key):
        inst = self.instantiate(key)
        if self.singleton:
            self.data[key] = inst
        return inst
