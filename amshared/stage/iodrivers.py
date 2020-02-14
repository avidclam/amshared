"""
Ready-to-use "driver pack" wrappers to write-read text, json and binary
(pickle) content.
"""

import pickle
import json
from ..islike import like_int, like_float, is_gen, is_array


class TextDriver:
    def read(self, path):
        with open(path, 'r') as file:
            content = file.read()
        return content

    def write(self, content, path):
        if content is None:
            content = ''
        with open(path, 'w') as file:
            file.write(content)


class PickleDriver:
    def read(self, path):
        with open(path, 'rb') as file:
            content = pickle.load(file)
        return content

    def write(self, content, path):
        with open(path, 'wb') as file:
            pickle.dump(content, file)


class StageEncoder(json.JSONEncoder):
    """JSON Encoder helps json survive exotic data types, e.g. numpy."""
    def default(self, x):
        if like_int(x):
            return int(x)
        elif like_float(x):
            return float(x)
        elif is_gen(x):
            return list(x)
        elif is_array(x):
            return list(x)
        else:
            try:
                return super().default(x)
            except TypeError:
                return None


class JsonDriver:
    def read(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            content = json.load(file)
        return content

    def write(self, content, path):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(content, file, cls=StageEncoder, ensure_ascii=False)


_default_io_pack = {
    '': PickleDriver,
    'pickle': PickleDriver,
    'txt': TextDriver,
    'html': TextDriver,
    'json': JsonDriver
}
