"""
Pipes is a naive implementation of sequential functions invocation.

Functions should be designed the way that a result returned by
preceding function (pipe argument) could be used as the first argument
to the next function, and so on.

"""


def run(*args, initial=None):
    """Creates and runs the pipe calling functions in given sequence.

    Args:
        *args: functions to call in sequence
        initial: argument to the first function (pipe argument)

    Returns:
        result of the last function called

    """
    data = initial
    for fun in args:
        data = fun(data)
    return data


def load(x):
    """When used in pipe, replaces pipe argument.

    Note:
        Value returned by preceding function call, if any, is lost.

    Args:
        x: argument to the next function (pipe argument)

    Returns:
        function that performs the required action

    """
    return lambda: x


def tee(f):
    """When used in pipe, calls argument function for its side effects.

    For exmaple, for logging, but passes pipe argument on.

    Note:
        1. Value returned by argument function, if any, is not used.
        2. Tee'ing a generator is not supported. May precede with ``list``.

    Args:
        f: function to call

    Returns:
        function that performs the required action

    """

    def g(x):
        f(x)
        return x

    return g


def method(name, *args, **kwargs):
    """When used in pipe, calls stated method of current pipe argument.

    Provided args and kwargs are used as method arguments.

    Args:
        name: name of the method to call
        *args: positional arguments to the method
        **kwargs: key arguments to the method

    Returns:
        function that performs the required action

    """

    def g(x):
        f = getattr(x, name, None)
        if f is callable(f):
            return f(*args, **kwargs)
        else:
            return x

    return g


def tee_method(name, *args, **kwargs):
    """When used in pipe, calls stated method for its side effect.

    Calls stated method of current pipe argument,
    but passes pipe argument on untouched.

    Args:
        name: name of the method to call
        *args: positional arguments to the method
        **kwargs: key arguments to the method

    Returns:
        function that performs the required action

    """

    def g(x):
        f = getattr(x, name, None)
        if f is not None and callable(f):
            f(*args, **kwargs)
        return x

    return g


def call(f, xarg, *args, **kwargs):
    """When used in pipe, calls given function.

    Calls given function, passing pipe argument by the name given as ``xarg``
    along with all other arguments. Resulting value is then used
    as pipe argument and passed along further.

    Note:
        kwargs will overwrite pipe argument ``if xarg in kwarg``.

    Args:
        f: function to call
        xarg: name of the function argument to pass pipe argument
        *args: positional arguments to the function
        **kwargs: keyword arguments to the function

    Returns:

    """

    def g(x):
        kw = {xarg: x}
        kw.update(**kwargs)
        return f(*args, **kw)

    return g
