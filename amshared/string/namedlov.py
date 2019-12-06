from collections.abc import Mapping, Iterable, Sequence
from .split import split


class NamedLoV:
    """Ordered Dictionary of Lists of Values

    Initialization takes sources in various forms, e.g.:

    .. code-block:: python

        {'ONE': ['1', 'one'], 'TWO': ['2', 'two']}
        (('ONE', ['1', 'one']), ('TWO', ['2', 'two']))
        (('ONE', '1', 'one'), ('TWO', '2', 'two'))
        [{'ONE': '1, one'}, {'TWO': ['2', 'two']}]  # requires sep=','
        [{'ONE': ['1', 'one']}, {'TWO': {'2': 'numeric', 'two': 'string'}}]

    In all cases ``data`` member equals
    ``{'ONE': ['1', 'one'], 'TWO': ['2', 'two']}``.

    In addition, in the last case ``other`` member equals
    ``{'TWO': {'2': 'numeric', 'two': 'string'}}``.

    ``kwargs`` used as split arguments.

    """
    def __init__(self, source, **kwargs):
        self.data = {}
        self.other = {}
        self.sep = kwargs.get('sep', None)
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
                            real_lov = split(lov, **kwargs)
                        elif isinstance(lov, Iterable):
                            real_lov = [v for v in lov]
                            if isinstance(lov, Mapping):
                                self.other[name] = lov
                        else:
                            real_lov = []
                        self.data[name] = real_lov

    def export(self, **kwargs):
        """Reconstructs canonical form of input.

        Args:
            kwargs: if ``sep`` is given, LoVs are joined into strings

        Returns:
            List of dictionaries of list of values.

        """
        if 'sep' in kwargs:  # convert LoVs into strings
            sep = kwargs.get('sep')
            if not isinstance(sep, str):
                sep = ' '
            return [{name: sep.join(lov)} for name, lov in self.data.items()]
        else:
            return [{name: lov} for name, lov in self.data.items()]

    @property
    def zip(self):
        """Generator of (name, value) tuples for all values

        Returns:
            generator

        Examples::

            >>> nlv = NamedLoV({'ONE': ['1', 'one'], 'TWO': ['2', 'two']})
            >>> print(*nlv.zip)
            ('ONE', '1') ('ONE', 'one') ('TWO', '2') ('TWO', 'two')

        """
        return ((name, v) for name, lov in self.data.items() for v in lov)
