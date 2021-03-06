import collections
from .constants import (
    STAGE_HEAP, STAGE_WILD, STAGE_RUBRIC_EMPTY,
    MK_PAYLOAD, MK_RUBRIC, MK_NAME, MK_PART, MK_FORMAT
)


def replace_value(data, key, empty, true, false, none):
    """Replace value in ``data`` dictionary under the given ``key``
    in case current value is '' (empty), None, True or False.

    Key is removed in case replacement value is None

    Args:
        data: dictionary to change
        key: data key
        empty: value to assign if current value is ''
        true: value to set if current value is True
        false: value to set if current value is False
        none: value to set if current value is None

    """

    value = data.get(key)
    if value is None:
        data[key] = none
    elif value is False:
        data[key] = false
    elif value is True:
        data[key] = true
    elif str(value).strip() == '':
        data[key] = empty
    if data[key] is None:
        data.pop(key)


_default_replacements = {  # empty, true, false, none
    MK_PAYLOAD: (True, True, False, True),
    MK_RUBRIC: (STAGE_RUBRIC_EMPTY,) * 4,
    MK_NAME: (STAGE_HEAP,) * 4,
    MK_PART: (None, STAGE_WILD, None, None),
    MK_FORMAT: ('',) * 4
}


class MetaData(collections.UserDict):
    """
    Adds 'business logic' to the metadata, provides key-dependent defaults
    """
    def __init__(self, data):
        super().__init__(data)
        name = self.data.get(MK_NAME)
        part = self.data.get(MK_PART)
        # Allow for wildcard atomic operations
        if part is False and name is None:
            self.data[MK_NAME] = STAGE_WILD
        for key in _default_replacements:
            replace_value(self.data, key, *_default_replacements[key])
        self._sfx = None

    def __missing__(self, key):
        # Protect from KeyError
        return None

    @property
    def sfx(self):
        fmt = self.get(MK_FORMAT)
        if self._sfx is not None:
            return self._sfx
        else:
            return f".{fmt}" if fmt else ''

    @sfx.setter
    def sfx(self, value):
        self._sfx = value

    @property
    def is_atomic(self):
        # Rule: atomic if name is specific (not heap) and no part present
        name = self.get(MK_NAME)
        part = self.get(MK_PART)
        return name != STAGE_HEAP and part is None
