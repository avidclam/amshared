from collections.abc import Mapping, Iterable, Sequence
from collections import UserDict


class TagLoV:
    """List of Tagged Lists of Values (LoV), i.e. [(tag, [v0, v1...])]

    Args:
            source: input in various forms (see below)
            to_list: function that converts string (or non-sequences) to lists
                of values (default: class method _split_strip)
            **kwargs: keyword arguments to the ``to_list``

    Initialization takes sources in various forms, e.g.:

    .. code-block:: python

        x0 = [('ONE', ['1', 'one']), ('TWO', ['2', 'two'])]  # canonical form
        x1 = (('ONE', '1', 'one'), ('TWO', '2', 'two'))
        x2 = {'ONE': ['1', 'one'], 'TWO': ['2', 'two']}
        x3 = [{'ONE': '1, one'}, {'TWO': ['2', 'two']}]  # requires sep=','
        x4 = [('ONE', ['1', 'one']), ('TWO', {'2': 'numeric', 'two': 'string'})]
        x5 = (('ONE', ['1', 'one']), ('ONE', ['1.1', 'one.one']))  # same tags
        x6 = 'just string'

    In all cases above resulting ``data`` equals
    ``[('ONE', ['1', 'one']), ('TWO', ['2', 'two'])]``.

    In addition, in the last case ``misc`` member equals
    ``[None, {'2': 'numeric', 'two': 'string'}]``.

    ``kwargs`` used as split arguments.

    Notes:
        It's easy to use untagged LoVs, e.g.::

            list_of_lovs = [[1, 2, 3], [10, 100]]
            taglov = TagLoV(enumerate(list_of_lovs))


    """
    @staticmethod
    def _split_strip(string, **kwargs):
        return map(str.strip, str.split(string, **kwargs))

    def __init__(self, source, to_list=None, **kwargs):
        self.data = []
        self.misc = []
        self.to_list = self._split_strip if to_list is None else to_list
        if isinstance(source, TagLoV):
            self.data = source.data.copy()
            self.misc = source.misc.copy()
            return
        if isinstance(source, str):
            self.data.append((source, []))
            self.misc.append(None)
            return
        if isinstance(source, Mapping):
            source = (source, )
        if isinstance(source, Iterable):
            for entry in source:
                if isinstance(entry, Mapping):
                    items = entry.items()
                elif isinstance(entry, str):
                    items = ((entry, []), )
                elif isinstance(entry, Sequence) and len(entry) > 0:
                    if len(entry) == 1:
                        items = ((entry, []), )
                    elif len(entry) == 2:
                        items = (entry, )
                    else:
                        items = ((entry[0], entry[1:]), )
                else:
                    items = None
                if items is not None:
                    for name, lov in items:
                        if isinstance(lov, str):
                            real_lov = [v for v in self.to_list(lov, **kwargs)]
                        elif isinstance(lov, Iterable):
                            real_lov = [v for v in lov]
                            if isinstance(lov, Mapping):
                                self.misc.append(lov)
                            else:
                                self.misc.append(None)
                        else:
                            try:
                                real_lov = [v for v in
                                            self.to_list(lov, **kwargs)]
                            except TypeError:
                                real_lov = []
                        self.data.append((name, real_lov))

    def __repr__(self):
        return f"TagLoV({self.canonical})"

    def __contains__(self, item):
        return any(item == tag for tag in self.tags)

    @property
    def canonical(self):
        """Recreate input data that would initialize equivalent instance"""
        if self.data:
            return [(tag, misc if misc else lov)
                    for (tag, lov), misc in zip(self.data, self.misc)]
        else:
            return self.data

    @property
    def tags(self):
        """Generator: all tags in order."""
        return (tag for tag, _ in self.data)

    @property
    def lovs(self):
        """Generator: all Lists-of-Values without tags."""
        return (lov for _, lov in self.data)

    @property
    def zip(self):
        """Generator of (name, value) tuples for all values.

        Returns:
            generator

        Examples::

            >>> nlv = TagLoV({'ONE': ['1', 'one'], 'TWO': ['2', 'two']})
            >>> print(*nlv.zip)
            ('ONE', '1') ('ONE', 'one') ('TWO', '2') ('TWO', 'two')

        """
        return ((tag, v) for tag, lov in self.data for v in lov)

    def map(self, func):
        """Applies function to each lov using ``misc`` as kwargs if present.

        Args:
            func: callable to apply to LoVs

        Returns:
            dictionary of function results with tags as keys

        """
        def _func(tpl):
            (tag, lov), kw = tpl
            if not kw:
                return tag, func(lov)
            else:
                return tag, func(lov, **kw)

        return map(_func, zip(self.data, self.misc))
