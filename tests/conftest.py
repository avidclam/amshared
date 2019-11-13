import pytest

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

    return {'fun': fun_driver, 'cls': cls_driver}
