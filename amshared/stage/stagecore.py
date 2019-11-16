import pathlib
from ..driverpack import DriverPack
from .iodrivers import _default_io_pack
from .metadata import MetaData
from .constants import (
    STAGE_METADATA, STAGE_CONTENT, STAGE_WILD, STAGE_HEAP, MK_PAYLOAD, MK_PART
)
from .internals import AtomicOps, PartOps, StageFolder


class Rubric:
    def __init__(self, stg, name):
        self.stg = stg
        self.name = name
        self.folder = StageFolder(self.stg.topmetadata / name)

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
                yield method()
            else:
                pairops = PartOps(self, meta, content)
                method = getattr(pairops, action)
                if MK_PART not in meta or meta[MK_PART] == STAGE_WILD:
                    # not part id or multiple part operations
                    if action == 'write':
                        yield pairops.append()
                    else:  # TODO: check that this code is tested
                        all_parts = pairops.mdir.parts
                        for part in all_parts:
                            pairops.meta[MK_PART] = part
                            pairops.set_paths()
                            yield method()
                else:
                    yield method()  # single part operation

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

    def get_rubric(self, rubric):
        return Rubric(self, rubric)
