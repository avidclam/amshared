"""
Stage is a way to serialize data flows.

Data Flow is a sequence (list, generator) of (metadata, content) tuples.

Metadata is a key-value dictionary with several key names reserved:
``rubric``, ``name``, ``part``, `format``, and ``payload``.

Content is useful application data (payload) or miscellaneous information
in arbitrary format.

Elements of data flows are logically organized in one of the three forms:

:Atomic: like a filesystem files, element has directory (rubric), name, format,
    and content, one per name
:Multipart: under a single name, content is divided into numbered parts, "pages"
:Heap: a bunch of unrelated parts in no particular order

"""

from .stagecore import Stage, Rubric
