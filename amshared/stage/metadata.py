import collections
from .constants import (
    STAGE_HEAP, STAGE_WILD, STAGE_RUBRIC_EMPTY,
    MK_PAYLOAD, MK_RUBRIC, MK_NAME, MK_PART, MK_FORMAT, MK_SFX
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
        for key in _default_replacements:
            replace_value(self.data, key, *_default_replacements[key])

    def __missing__(self, key):
        return self.sfx if key == MK_SFX else None

    @property
    def sfx(self):
        fmt = self.get(MK_FORMAT)
        return f".{fmt}" if fmt else ''

    @property
    def is_atomic(self):
        # Rule: atomic if name is specific (not heap) and no part present
        name = self.get(MK_NAME)
        part = self.get(MK_PART)
        return name != STAGE_HEAP and part is None
