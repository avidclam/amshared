from amshared import pipe


def test_pipe_run():
    y = pipe.run(
        lambda x: x + 1,
        initial=1000
    )
    assert y > 1000


def test_pipe_load():
    y = pipe.run(
        lambda x: x + 1,
        pipe.load(1001),
        initial=-1
    )
    assert y > 1000

def test_pipe_call_positional():
    def xn(x, n):
        return x*n

    y = pipe.run(
        pipe.call(xn, 2),
        initial=1
    )
    assert y == 2

def test_pipe_call_keyword():
    def xn(prefix, x, n):
        return prefix + str(x*n)

    # Requires helper function, specific to xn
    def xn_x_first(x, prefix, n):
        return xn(prefix=prefix, x=x, n=n)

    y = pipe.run(
        pipe.call(xn_x_first, 'x=', 2),
        initial=1
    )
    assert y == 'x=2'

    y2 = pipe.run(
        pipe.call(xn_x_first, n=2, prefix='x='),
        initial=1
    )
    assert y == y2
