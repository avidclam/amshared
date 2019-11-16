import pathlib
import time
from ..helpers import safe_numeric
from .metadata import MetaData
from .constants import (
    STAGE_META_FORMAT, STAGE_HEAP,
    STAGE_META_SFX, MK_RUBRIC, MK_NAME, MK_PART, MK_FORMAT,
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

    def lsnames(self, files_only=None):
        """Gets names of stage objects stored in the folder.

        Atomic objects are stored in files.
        Heap and multipart objects are stored in folders with each part stored
        in a separate file.

        Note:
            name of Heap is not included in return value

        Args:
            files_only: names of files (True), dirs (False) or both (None)

        Returns:
            list of names

        """
        pg = self.path.glob('*')
        if files_only is None:
            return self.lsnames(True) + self.lsnames(False)
        elif files_only:
            return [p.stem for p in pg if p.is_file()]
        else:
            return [p.name for p in pg if p.is_dir() and p.name != STAGE_HEAP]

    @property
    def parts(self):
        """Returns list of all part **numbers** in folder."""
        return [safe_numeric(stem, 0) for stem in self.lsnames(files_only=True)]


class PairOps:
    """Pared read/write/delete operations on metadata and content files.

    """
    def __init__(self, stg, meta, content):
        self.stg = stg
        self.meta = meta
        self.content = content
        self.meta_only = content is False
        self.set_paths()

    def set_paths(self):
        self.rdir = StageFolder(self.stg.topmetadata / self.meta[MK_RUBRIC])
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
        self.cfile = self.cdir / f"{self.meta[MK_NAME]}{self.meta.sfx}"


class PartOps(PairOps):
    def set_paths(self):
        super().set_paths()
        self.mdir = StageFolder(self.rdir / self.meta[MK_NAME])
        self.cdir = StageFolder(self.stg.topcontent /
                                self.meta[MK_RUBRIC] /
                                self.meta[MK_NAME])
        if MK_PART in self.meta:
            self.mfile = self.mdir / f"{self.meta[MK_PART]}{STAGE_META_SFX}"
            self.cfile = self.cdir / f"{self.meta[MK_PART]}{self.meta.sfx}"

    def append(self):
        max_part_num = max(self.mdir.parts, default=0)
        self.meta[MK_PART] = max_part_num + 1
        self.set_paths()
        return self.write()
