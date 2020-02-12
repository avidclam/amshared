"""
Ready-to-use "driver pack" wrappers to write-read text, json and binary
(pickle) content.
"""
import pickle
import json

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


class JsonDriver:
    def read(self, path):
        with open(path, 'r', encoding='utf-8') as file:
            content = json.load(file)
        return content

    def write(self, content, path):
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(content, file, ensure_ascii=False)


_default_io_pack = {
    '': PickleDriver,
    'pickle': PickleDriver,
    'txt': TextDriver,
    'html': TextDriver,
    'json': JsonDriver
}
