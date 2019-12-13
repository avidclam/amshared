from collections.abc import Mapping, Iterable
import pathlib
from ..driverpack import DriverPack
from .iodrivers import _default_io_pack
from .metadata import MetaData
from .constants import (
    STAGE_METADATA, STAGE_CONTENT, STAGE_WILD, STAGE_HEAP,
    MK_PAYLOAD, MK_RUBRIC, MK_NAME, MK_PART, MK_ERROR
)
from .internals import AtomicOps, PartOps, StageFolder


def gen_dataflow(x):
    """Generates dataflow from x, depending on the type of x

    Args:
        x: any object

    Returns:
        generator

    """
    if (
            isinstance(x, tuple) and
            len(x) == 2 and
            isinstance(x[0], Mapping)
    ):
        yield x
    elif isinstance(x, Mapping):
        yield x, None
    elif isinstance(x, str):
        yield {}, x
    elif isinstance(x, Iterable):
        for chunk in x:
            yield from gen_dataflow(chunk)
    else:
        yield {}, x


def call_method(method, meta):
    """Calls methods that returns one dataflow piece and catches exceptions.

    If case exception is caught, metadata becomes informational
    with ``{'payload': False}`` and 'error' info provided.

    Args:
        method: callable to call
        meta: MetaData to return modified in case of error

    Returns:
        dataflow

    """
    try:
        return method()
    except (OSError, NotImplementedError) as e:
        ometa = meta.copy()
        ometa[MK_PAYLOAD] = False
        ometa[MK_ERROR] = type(e).__name__
        return ometa.data, None


class Rubric:
    """Rubric is an interface to names and parts of objects in a rubric."""

    def __init__(self, stg, rubric):
        self.stg = stg
        self.name = rubric
        self.folder = StageFolder(self.stg.topmetadata / rubric)

    def exists(self):
        return self.folder.path.exists()

    @property
    def atomic_names(self):
        return self.folder.lsnames(files_only=True)

    @property
    def multipart_names(self):
        return self.folder.lsnames(files_only=False)

    def get_name_parts(self, name):
        return StageFolder(self.folder / name).parts

    @property
    def heap_parts(self):
        return self.get_name_parts(STAGE_HEAP)


class Stage:
    """Core class that implements all stage operations.

    Args:
        path: path to the topmost stage folder
        io_pack: instance of DriverPack with classes implementing read/write
            operations for the formats of files storing data flow content

        Operations are load, save and delete.
        Methods return (or yield, if method's rubric starts with 'g') metadata of
        all objects on which operation was performed.

    """

    def __init__(self, path, io_pack=None):
        if io_pack is None:
            io_pack = _default_io_pack
        self.iodp = DriverPack(io_pack)
        if isinstance(path, pathlib.Path):
            self.topmost = path
        else:
            self.topmost = pathlib.Path(path)
        if self.topmost.exists() and not self.topmost.is_dir():
            raise FileNotFoundError(f"Not a directory: '{self.topmost}'")
        self.topmost.mkdir(parents=True, exist_ok=True)
        self.topcontent = self.topmost / STAGE_CONTENT
        self.topmetadata = self.topmost / STAGE_METADATA

    def _dispatch(self, dataflow, action):
        for metadata, content in gen_dataflow(dataflow):
            meta = MetaData(metadata)
            if not meta[MK_PAYLOAD]:
                continue
            if meta[MK_NAME] == STAGE_WILD and action in ('read', 'unlink'):
                rbc = Rubric(self, meta.get(MK_RUBRIC, ''))
                if meta.is_atomic:
                    all_names = rbc.atomic_names
                else:
                    all_names = rbc.multipart_names
                for name in all_names:
                    meta['name'] = name
                    yield from self._subdispatch(meta, content, action)
            else:
                yield from self._subdispatch(meta, content, action)

    def _subdispatch(self, meta, content, action):
        if meta.is_atomic:
            pairops = AtomicOps(self, meta, content)
            method = getattr(pairops, action)
            if meta[MK_NAME] == STAGE_WILD and action in ('read', 'unlink'):
                all_names = pairops.rdir.lsnames(files_only=True)
                for name in all_names:
                    pairops.meta[MK_NAME] = name
                    pairops.set_paths()
                    yield call_method(method, pairops.meta)
            else:
                yield call_method(method, meta)  # single content
        else:
            pairops = PartOps(self, meta, content)
            method = getattr(pairops, action)
            if MK_PART not in meta or meta[MK_PART] == STAGE_WILD:
                # not part id or multiple part operations
                if action == 'write':
                    yield call_method(pairops.append, pairops.meta)
                else:
                    all_parts = pairops.mdir.parts
                    # if all_parts == []:
                    # Insert code here if there's a need to return
                    # meaningful information rather than an empty list.
                    for part in all_parts:
                        pairops.meta[MK_PART] = part
                        pairops.set_paths()
                        yield call_method(method, pairops.meta)
            else:
                yield call_method(method, pairops.meta)  # single part

    def gsave(self, dataflow):
        yield from self._dispatch(dataflow, 'write')

    def save(self, dataflow):
        return [*self.gsave(dataflow)]

    def gload(self, dataflow):
        yield from self._dispatch(dataflow, 'read')

    def load(self, dataflow):
        return [*self.gload(dataflow)]

    def gdelete(self, dataflow):
        yield from self._dispatch(dataflow, 'unlink')

    def delete(self, dataflow):
        return [*self.gdelete(dataflow)]
