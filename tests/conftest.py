import pytest
from amshared.driverpack import DriverExample


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


class Concealed:
    def __init__(self, content=None):
        if content is not None:
            self.content = content
        else:
            self.content = 'Our content\nIs our best having.'

    def reveal(self, out=False):
        if out:
            print(self.content)
        return self.content


dataflow = (
    # Dataflow is an iterable of (metadata, content) tuples
    # in which metadata is a dict, and content is arbitrary
    ({'rubric': 'post/mail', 'format': 'txt'}, 'From US'),  # heap part
    ({'rubric': 'post/mail'}, 'From Canada'),  # heap part
    ({'rubric': 'post/mail', 'format': 'json'}, 'From Russia'),  # heap part
    ({'rubric': 'post/mail', 'name': 'unique', 'format': 'txt'},
     'From Mars'),  # atomic
    ({'rubric': 'post/mail', 'name': 'chain', 'part': 1, 'format': 'json'},
     dict(message='Part one')),  # part of a multipart content
    ({'rubric': 'post/mail', 'name': 'chain', 'part': 10, 'format': 'json'},
     dict(message='Part ten')),  # part of a multipart content
    ({'rubric': 'post/parcel', 'name': 'secret', 'format': 'pickle'},
     Concealed())  # atomic
)

@pytest.fixture()
def drvpack():
    return {'fun': fun_driver, 'cls': cls_driver, 'example': DriverExample}

@pytest.fixture()
def secret():
    return Concealed('secret')

@pytest.fixture(name='dataflow')
def dataflow_fixture():
    return dataflow
