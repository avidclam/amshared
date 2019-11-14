from amshared import pipe


def test_pipe_run():
    assert 1001 == pipe.run(
        lambda x: x + 1,
        initial=1000
    )


def test_pipe_load():
    assert 1001 == pipe.run(
        lambda x: x + 1,
        pipe.load(1001),
        initial=-1
    )


def test_pipe_call_positional():
    def xn(x, n):
        return x * n

    assert 2 == pipe.run(
        pipe.call(xn, 2),
        initial=1
    )


def test_pipe_call_keyword():
    def xn(prefix, x, n):
        return prefix + str(x * n)

    # Requires helper function, specific to xn, to change argument order
    def xn_x_first(x, prefix, n):
        return xn(prefix=prefix, x=x, n=n)

    assert 'x=2' == pipe.run(
        pipe.call(xn_x_first, 'x=', 2),
        initial=1
    )

    assert 'x=2' == pipe.run(
        pipe.call(xn_x_first, n=2, prefix='x='),
        initial=1
    )


def test_pipe_tee(capsys):
    assert 1000 == pipe.run(
        pipe.load(1000),
        pipe.tee(lambda x: print(f'x={x}'))
    )
    captured = capsys.readouterr()
    assert captured.out == "x=1000\n"


def test_pipe_method(secret):
    assert 'secret' == pipe.run(
        pipe.load(secret),
        pipe.method('reveal', False)
    )


def test_pipe_tee_method(secret, capsys):
    assert 'secret' == pipe.run(
        pipe.load(secret),
        pipe.method('reveal', out=True)
    )
    captured = capsys.readouterr()
    assert captured.out == "secret\n"
