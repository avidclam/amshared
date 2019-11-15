import pathlib
import time
from ..driverpack import DriverPack
from ..helpers import safe_numeric
from .iodrivers import _default_io_pack
from .metadata import MetaData
from .constants import (
    STAGE_METADATA, STAGE_CONTENT, STAGE_META_FORMAT, STAGE_WILD, STAGE_HEAP,
    STAGE_META_SFX, MK_PAYLOAD, MK_RUBRIC, MK_NAME, MK_PART, MK_FORMAT, MK_SFX,
    MK_CTIME, XTRA_CTIME_FORMAT
)


class StageFolder:
    """Base class for a folder-inside-stage object.

    Args:
        path (pathlib.Path): path of the corresponding filesystem folder

    """

    def __init__(self, path):
        self.path = path

    def __truediv__(self, subpath):
        return self.path / subpath

    def lsnames(self, atomic=None):
        """Gets names of stage objects stored in the folder.

        Note:
            name of heap is not included

        Args:
            atomic: only atomic (True), only multipart (False) or both (None)

        Returns:
            list of names

        """
        pg = self.path.glob('*')
        if atomic is None:
            return self.lsnames(True) + self.lsnames(False)
        elif atomic:
            return [p.stem for p in pg if p.is_file()]
        else:
            return [p.name for p in pg if p.is_dir() and p.name != STAGE_HEAP]

    @property
    def parts(self):
        """Returns list of all part numbers in folder."""
        # Note: need to set atomic to True in lsnames to consider files not dirs
        return [safe_numeric(stem, 0) for stem in self.lsnames(True)]


class RubricFolder(StageFolder):
    def __init__(self, stg, rubric):
        self.stg = stg
        self.rubric = rubric
        super().__init__(self.stg.topmeta / self.rubric)

    def last_heap_meta(self):
        hdir = StageFolder(self / STAGE_HEAP)
        last_part = max(hdir.parts, default=0)
        if last_part > 0:
            request = [({MK_RUBRIC: self.rubric, MK_PART: last_part}, False)]
            return self.stg.load(request)
        else:
            return [({}, None)]


class PairOps:
    def __init__(self, stg, meta, content):
        self.stg = stg
        self.meta = meta
        self.content = content
        self.meta_only = content is False
        self.set_paths()

    def set_paths(self):
        self.rdir = RubricFolder(self.stg, self.meta[MK_RUBRIC])
        self.mdir = None
        self.mfile = None
        self.cdir = None
        self.cfile = None

    @property
    def format_is_supported(self):
        return (MK_FORMAT in self.meta
                and self.meta[MK_FORMAT] in self.stg.iodp.driver_keys)

    def read_meta(self):
        metadata = self.stg.iodp[STAGE_META_FORMAT].read(self.mfile)
        self.meta = MetaData(metadata)
        self.set_paths()

    def read(self):
        self.read_meta()
        if not self.meta_only and self.format_is_supported:
            content = self.stg.iodp[self.meta[MK_FORMAT]].read(self.cfile)
        else:
            content = None
        return self.meta.data, content

    def write(self):
        if self.format_is_supported:
            timestamp_string = time.strftime(XTRA_CTIME_FORMAT, time.gmtime())
            self.meta.update({MK_CTIME: timestamp_string})
            self.mfile.parent.mkdir(parents=True, exist_ok=True)
            self.cfile.parent.mkdir(parents=True, exist_ok=True)
            content_driver = self.stg.iodp[self.meta[MK_FORMAT]]
            content_driver.write(self.content, self.cfile)
            metadata_driver = self.stg.iodp[STAGE_META_FORMAT]
            metadata_driver.write(self.meta.data, self.mfile)
            return self.meta.data, None
        else:
            return {}, None

    def unlink(self):
        self.read_meta()
        try:
            self.mfile.unlink()
            self.cfile.unlink()
            report = self.meta.data, None
        except OSError:
            report = {}, None
        try:
            self.mfile.parent.rmdir()
            self.cfile.parent.rmdir()
        except OSError:
            pass
        return report


class AtomicOps(PairOps):
    def set_paths(self):
        super().set_paths()
        self.mdir = self.rdir
        self.mfile = self.mdir / f"{self.meta[MK_NAME]}{STAGE_META_SFX}"
        self.cdir = StageFolder(self.stg.topcontent / self.meta[MK_RUBRIC])
        self.cfile = self.cdir / f"{self.meta[MK_NAME]}{self.meta[MK_SFX]}"


class PartOps(PairOps):
    def set_paths(self):
        super().set_paths()
        self.mdir = StageFolder(self.rdir / self.meta[MK_NAME])
        self.cdir = StageFolder(self.stg.topcontent /
                                self.meta[MK_RUBRIC] /
                                self.meta[MK_NAME])
        if MK_PART in self.meta:
            self.mfile = self.mdir / f"{self.meta[MK_PART]}{STAGE_META_SFX}"
            self.cfile = self.cdir / f"{self.meta[MK_PART]}{self.meta[MK_SFX]}"

    def reset_part(self, part):
        self.meta[MK_PART] = part
        self.set_paths()

    @property
    def all_parts(self):
        return self.mdir.parts

    def append(self):
        max_part_num = max(self.all_parts, default=0)
        self.reset_part(max_part_num + 1)
        return self.write()


class Stage:
    """Core class that implements all stage operations.

    Args:
        path: path to the topmost stage folder
        io_pack: instance of DriverPack with classes implementing read/write
            operations for the formats of files storing data flow content
        xtrameta_pack: instance of DriverPack with classes providing
            additional metadata, e.g. timestamps

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
            raise FileNotFoundError(f'Not a directory: {self.topmost}')
        self.topmost.mkdir(parents=True, exist_ok=True)
        self.topcontent = self.topmost / STAGE_CONTENT
        self.topmeta = self.topmost / STAGE_METADATA

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
                    else:
                        for part in pairops.all_parts:
                            pairops.reset_part(part)
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

    def lsnames(self, rubric, atomic=None):
        rdir = RubricFolder(self, rubric)
        return rdir.lsnames(atomic)

    def last_heap_meta(self, rubric):
        rdir = RubricFolder(self, rubric)
        return rdir.last_heap_meta()
