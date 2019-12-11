import string
from collections.abc import Mapping, Iterable, Sequence


class TagLoV:
    """List of Tagged Lists of Values: [(tag, [v0, v1...]), ...]

    Args:
            source: input in various forms (see below)
            getlist: function that converts string (or non-sequences) to lists
                of values (default: class method _split_strip)
            **kwargs: keyword arguments to the ``getlist``

    Initialization takes sources in various forms, e.g.:

    .. code-block:: python

        x0 = [('ONE', ['1', 'one']), ('TWO', ['2', 'two'])]  # canonical form
        x1 = (('ONE', '1', 'one'), ('TWO', '2', 'two'))
        x2 = {'ONE': ['1', 'one'], 'TWO': ['2', 'two']}
        x3 = [{'ONE': '1, one'}, {'TWO': ['2', 'two']}]
        x4 = [('ONE', ['1', 'one']), ('TWO', {'2': 'numeric', 'two': 'string'})]
        x5 = (('ONE', ['1', 'one']), ('ONE', ['1.1', 'one.one']))  # same tags

    In cases x0 -  x3 above .lovs method will show
    ``(['1', 'one'], ['2', 'two'])``


    In case x4, ``data`` member equals
    ``[('ONE', ['1', 'one']), ('TWO', {'2': 'numeric', 'two': 'string'})]``.

    ``kwargs`` used as split arguments.

    Notes:
        It's easy to use untagged LoVs, e.g.::

            list_of_lovs = [[1, 2, 3], [10, 100]]
            taglov = TagLoV(enumerate(list_of_lovs))

    """

    def __init__(self, source, getlist=None, **kwargs):
        self.data = []
        self.getlist = self._split_strip if getlist is None else getlist
        if isinstance(source, TagLoV):
            self.data = source.data.copy()
            return
        if isinstance(source, str):
            self.data.append((source, []))
            return
        if isinstance(source, Mapping):
            source = (source,)
        if isinstance(source, Iterable):
            for entry in source:
                if isinstance(entry, Mapping):
                    items = entry.items()
                elif isinstance(entry, str):
                    items = ((entry, []),)
                elif isinstance(entry, Sequence) and len(entry) > 0:
                    if len(entry) == 1:
                        items = ((entry, []),)
                    elif len(entry) == 2:
                        items = (entry,)
                    else:
                        items = ((entry[0], entry[1:]),)
                else:
                    items = None
                if items is not None:
                    for name, lov in items:
                        if isinstance(lov, str):
                            real_lov = [v for v in self.getlist(lov, **kwargs)]
                        elif isinstance(lov, Mapping):
                            real_lov = lov
                        elif isinstance(lov, Iterable):
                            lov_as_list = [v for v in lov]
                            if any(isinstance(v, Mapping) for v in lov_as_list):
                                real_lov = lov
                            else:
                                real_lov = lov_as_list
                        else:
                            try:
                                real_lov = [v for v in
                                            self.getlist(lov, **kwargs)]
                            except (TypeError, AttributeError):
                                real_lov = []
                        self.data.append((name, real_lov))

    def __repr__(self):
        return f"TagLoV({repr(self.data)})"

    def __contains__(self, item):
        return any(item == tag for tag in self.tags)

    @property
    def tags(self):
        """Generator: all tags in order."""
        return (tag for tag, _ in self.data)

    @property
    def lovs(self):
        """Generator: all Lists-of-Values without tags."""
        return ([*self._gval(lov)] for _, lov in self.data)

    @property
    def zip(self):
        """Generator: (tag, lov) tuples."""
        return ((tag, [*self._gval(lov)]) for tag, lov in self.data)

    @property
    def roll(self):
        """Generator of (name, value) tuples for all values.

        Returns:
            generator

        Examples::

            >>> nlv = TagLoV({'ONE': ['1', 'one'], 'TWO': ['2', 'two']})
            >>> print(*nlv.roll)
            ('ONE', '1') ('ONE', 'one') ('TWO', '2') ('TWO', 'two')

        """
        return ((tag, v) for tag, lov in self.data for v in self._gval(lov))

    @staticmethod
    def _split_strip(string_, **kwargs):
        sep = kwargs.get('sep', None)
        if sep is not None:
            separators = sep
            if isinstance(separators, str):
                separators = [separators]
        else:
            separators = (',', ';', *string.whitespace)
        words = [string_]
        for sep in separators:
            words = [part for word in words for part in word.split(sep)]
        return [word for word in words if word]

    @staticmethod
    def _gval(lov):
        for v in lov:
            if isinstance(v, Mapping):
                for key in v:
                    yield key
            else:
                yield v
