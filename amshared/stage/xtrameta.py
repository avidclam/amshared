"""
Implements sample provider of extra metadata: ctime.
Additional providers need to inherit ``XtraMetaBase`` and implement
``get_metadata`` method.
"""

import time
from .constants import MK_CTIME, XTRA_CTIME_FORMAT


class XtraMetaBase:
    def __init__(self):
        self._xtra_kwargs = {}

    def get_metadata(self):
        return {}

    def __call__(self, *_, **kwargs):
        self._xtra_kwargs.update(kwargs)
        return self

    @property
    def metadata(self):
        return self.get_metadata()


class CTime(XtraMetaBase):
    def get_metadata(self):
        return {MK_CTIME: time.strftime(XTRA_CTIME_FORMAT, time.gmtime())}


_default_xtrameta_pack = {
    MK_CTIME: CTime
}

