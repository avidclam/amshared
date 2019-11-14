"""
Stage is a way to serialize data flows (sequences of metadata-content pairs).

Metadata is a key-value dictionary with some keys required:
``rubric``, ``name``, ``part``, `format``,and ``payload``.

Content is useful application data (payload) or miscellaneous information.

Data flow elements can come in one of the three forms:

:Atomic: like a filesystem files, element has directory (rubric), name, format,
    and content, one per name
:Multipart: under a single name, content is divided into numbered parts, "pages"
:Heap: a bunch of unrelated parts in no particular order

"""

from .iodrivers import _default_io_pack
from .xtrameta import _default_xtrameta_pack
from .metadata import MetaData
#from .core import Stage
