from collections.abc import Mapping, Iterable, Sequence


class TagLoV:
    """Ordered Dictionary of Lists of Values

    Args:
            source: input in various forms (see below)
            to_list: function that converts string (or non-sequences) to lists
                of values (default: class method _split_strip)
            **kwargs: keyword arguments to the ``to_list``

    Initialization takes sources in various forms, e.g.:

    .. code-block:: python

        {'ONE': ['1', 'one'], 'TWO': ['2', 'two']}
        (('ONE', ['1', 'one']), ('TWO', ['2', 'two']))
        (('ONE', '1', 'one'), ('TWO', '2', 'two'))
        [{'ONE': '1, one'}, {'TWO': ['2', 'two']}]  # requires sep=','
        [{'ONE': ['1', 'one']}, {'TWO': {'2': 'numeric', 'two': 'string'}}]

    In all cases above resulting ``data`` equals
    ``{'ONE': ['1', 'one'], 'TWO': ['2', 'two']}``.

    In addition, in the last case ``misc`` member equals
    ``{'TWO': {'2': 'numeric', 'two': 'string'}}``.

    ``kwargs`` used as split arguments.

    """
    @staticmethod
    def _split_strip(string, **kwargs):
        return map(str.strip, str.split(string, **kwargs))

    def __init__(self, source, to_list=None, **kwargs):
        """

        Args:
            source:
            get_list:
            **kwargs:
        """
        self.to_list = self._split_strip if to_list is None else to_list
        self.data = {}
        self.misc = {}
        if isinstance(source, TagLoV):
            self.data = source.data.copy()
            self.misc = source.misc.copy()
            return
        if isinstance(source, str):
            self.data[source] = []
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
                                self.misc[name] = lov
                        else:
                            try:
                                real_lov = [v for v in
                                            self.to_list(lov, **kwargs)]
                            except TypeError:
                                real_lov = []
                        self.data[name] = real_lov

    def export(self, sep=None):
        """Reconstructs canonical form of input.

        Args:
            sep: ``sep`` is given, LoVs are joined into strings

        Returns:
            List of dictionaries of list of values.

        """
        if sep:
            return [{nm: str(sep).join(lov)} for nm, lov in self.data.items()]
        else:
            return [{nm: lov} for nm, lov in self.data.items()]

    def __contains__(self, item):
        return self.data.__contains__(item)

    def keys(self):
        """All tags in a form of dictionary keys."""
        return self.data.keys()

    @property
    def lovs(self):
        """Generator: all Lists-of-Values without tags."""
        return (lov for _, lov in self.data.items())

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
        return ((name, v) for name, lov in self.data.items() for v in lov)

    def map(self, func):
        """Applies function to each lov using ``misc`` as kwargs if present.

        Args:
            func: callable to apply to LoVs

        Returns:
            dictionary of function results with tags as keys

        """
        mapped = {}
        for tag, lov in self.data.items():
            result = func(lov, **self.misc.get(tag, {}))
            mapped.update({tag: result})
        return mapped
