import pytest
from amshared.driverpack import DriverExample

@pytest.fixture()
def drvpack():
    def fun_driver(x, a):
        def call():
            return f"'{a}' is {x}"

        return call

    class cls_driver:
        def __init__(self, y, b):
            self.y = y
            self.b = b

        def __call__(self):
            return f"'{self.b}' means {self.y}"

    return {'fun': fun_driver, 'cls': cls_driver, 'example': DriverExample}


@pytest.fixture()
def secret():
    class Secret:
        def __init__(self):
            self.word = 'secret'

        def reveal(self, out):
            if out:
                print(self.word)
            return self.word

    return Secret()


class Concealed:
    # this is to check serialization
    def __init__(self, content=None):
        if content is not None:
            self.content = content
        else:
            self.content = 'Our content\nIs our best having.'

    def reveal(self):
        return self.content


@pytest.fixture()
def dataflow():
    # Dataflow is an iterable of (metadata, content) tuples
    # in which metadata is a dict, and content is arbitrary
    return [
        ({'rubric': 'post/mail', 'format': 'txt'}, 'From US'),
        ({'rubric': 'post/mail'}, 'From Canada'),
        ({'rubric': 'post/mail', 'format': 'json'}, 'From Russia'),
        ({'rubric': 'post/mail', 'name': 'unique', 'format': 'txt'},
         'From Mars'),
        ({'rubric': 'post/mail', 'name': 'chain', 'part': 1, 'format': 'json'},
         dict(message='Part one')),
        ({'rubric': 'post/mail', 'name': 'chain', 'part': 10, 'format': 'json'},
         dict(message='Part ten')),
        ({'rubric': 'post/parcel', 'name': 'secret', 'format': 'pickle'},
         Concealed())
    ]
