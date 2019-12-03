import pathlib
from ..driverpack import DriverPack
from .iodrivers import _default_io_pack
from .metadata import MetaData
from .constants import (
    STAGE_METADATA, STAGE_CONTENT, STAGE_WILD, STAGE_HEAP, MK_PAYLOAD, MK_PART,
    MK_ERROR
)
from .internals import AtomicOps, PartOps, StageFolder


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
    except (FileNotFoundError, OSError, NotImplementedError) as e:
        ometa = meta.copy()
        ometa[MK_PAYLOAD] = False
        ometa[MK_ERROR] = type(e).__name__
        return ometa.data, None


class Rubric:
    """Rubric is an interface to names and parts of objects in a rubric."""

    def __init__(self, stg, name):
        self.stg = stg
        self.name = name
        self.folder = StageFolder(self.stg.topmetadata / name)

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
        Methods return (or yield, if method's name starts with 'g') metadata of
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
        for chunk in dataflow:
            if isinstance(chunk, tuple):
                meta = MetaData(chunk[0])
                content = chunk[1] if len(chunk) > 1 else None
            else:
                meta = MetaData(chunk)
                content = None
            if not meta[MK_PAYLOAD]:
                continue
            if meta.is_atomic:
                pairops = AtomicOps(self, meta, content)
                method = getattr(pairops, action)
                yield call_method(method, meta)
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
