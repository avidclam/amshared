"""
Implements sample provider of extra metadata: ctime.
Additional providers need to inherit ``XtraMetaBase`` and implement
``get_metadata`` method.
"""

import time
from .constants import MK_CTIME, XTRA_CTIME_FORMAT


class XtraMetaBase:
    def get_metadata(self):
        return {}

    def __call__(self, *args, **kwargs):
        return self.get_metadata()

    @property
    def metadata(self):
        return self.get_metadata()


class CTime(XtraMetaBase):
    def get_metadata(self):
        return {MK_CTIME: time.strftime(XTRA_CTIME_FORMAT, time.gmtime())}


_default_xtrameta_pack = {
    MK_CTIME: CTime
}

