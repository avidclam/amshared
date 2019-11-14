"""
Pipe is a quick-and-dirty implementation of sequential functions invocation.

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
        function that performs the required action in pipe

    """
    return lambda _: x


def tee(f, *args, **kwargs):
    """When used in pipe, calls function but does not use the return value.

    For example, for logging or printing.

    Pipe argument is passed first, before args and kwargs, similar to pipe.call.
    Resulting value is not used, pipe argument is passed along further instead.

    Note:
        Tee'ing a generator is not supported. May precede with ``list``.

    Args:
        f: function to call
        *args: other positional arguments to the function
        **kwargs: keyword arguments to the function

    Returns:
        function that performs the required action in pipe

    """

    def g(x):
        pargs = (x,) + args
        f(*pargs, **kwargs)
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
        function that performs the required action in pipe

    """

    def g(x):
        f = getattr(x, name, None)
        return f(*args, **kwargs)

    return g


def tee_method(name, *args, **kwargs):
    """When used in pipe, calls stated method but does not use the return value.

    Calls stated method of current pipe argument,
    but passes pipe argument on untouched.

    Args:
        name: name of the method to call
        *args: positional arguments to the method
        **kwargs: key arguments to the method

    Returns:
        function that performs the required action in pipe

    """

    def g(x):
        f = getattr(x, name, None)
        f(*args, **kwargs)
        return x

    return g


def call(f, *args, **kwargs):
    """When used in pipe, calls given function.

    Calls given function, passing pipe argument first, before args and kwargs.
    Hence function should be (re)designed to handle this.
    Resulting value is then used as pipe argument and passed along further.

    Note:
        kwargs will overwrite pipe argument ``if xarg in kwarg``.

    Args:
        f: function to call
        *args: other positional arguments to the function
        **kwargs: keyword arguments to the function

    Returns:
        function that performs the required action in pipe

    """

    def g(x):
        pargs = (x,) + args
        return f(*pargs, **kwargs)

    return g
