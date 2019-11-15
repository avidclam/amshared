from amshared.stage.metadata import MetaData
from amshared.stage.constants import (
    STAGE_HEAP, STAGE_WILD, STAGE_RUBRIC_EMPTY,
    MK_PAYLOAD, MK_RUBRIC, MK_NAME, MK_PART, MK_FORMAT
)

def test_stage_metadata_defaults():
    meta = MetaData({})
    assert meta[MK_PAYLOAD] is True
    assert meta[MK_RUBRIC] == STAGE_RUBRIC_EMPTY
    assert meta[MK_NAME] == STAGE_HEAP
    assert meta[MK_FORMAT] == ''
    assert MK_PART not in meta
    assert meta['some missing key'] is None


def test_stage_metadata_payload():
    meta = MetaData({MK_PAYLOAD: False})
    assert meta[MK_PAYLOAD] is False


def test_stage_metadata_rubric():
    # rubric is boolean
    meta = MetaData({MK_RUBRIC: False})
    assert meta[MK_RUBRIC] == STAGE_RUBRIC_EMPTY
    meta = MetaData({MK_RUBRIC: True})
    assert meta[MK_RUBRIC] == STAGE_RUBRIC_EMPTY
    # rubric is empty
    meta = MetaData({MK_RUBRIC: '    '})
    assert meta[MK_RUBRIC] == STAGE_RUBRIC_EMPTY
    # rubric is set
    meta = MetaData({MK_RUBRIC: 'main'})
    assert meta[MK_RUBRIC] == 'main'

def test_stage_metadata_name():
    meta = MetaData({})
    assert meta[MK_NAME] == STAGE_HEAP
    assert meta.is_atomic is False
    meta = MetaData({MK_NAME: 'main'})
    assert meta[MK_NAME] == 'main'
    assert meta.is_atomic is True
    meta = MetaData({MK_NAME: 0})
    assert meta[MK_NAME] == 0
    assert meta.is_atomic is True

def test_stage_metadata_part():
    meta = MetaData({MK_PART: ''})
    assert MK_PART not in meta
    assert meta.is_atomic is False
    meta = MetaData({MK_NAME: 0, MK_PART: ''})
    assert MK_PART not in meta
    assert meta.is_atomic is True
    meta = MetaData({MK_NAME: 0, MK_PART: 0})
    assert meta[MK_PART] == 0
    assert meta.is_atomic is False
    meta = MetaData({MK_NAME: 0, MK_PART: True})
    assert meta[MK_PART] == STAGE_WILD
    assert meta.is_atomic is False

def test_stage_metadata_format_sfx():
    for fmt in ('   ', True, False):
        meta = MetaData({MK_FORMAT: fmt})
        assert meta[MK_FORMAT] == ''
        assert meta.sfx == ''
    meta = MetaData({MK_FORMAT: 'html'})
    assert meta[MK_FORMAT] == 'html'
    assert meta.sfx == '.html'
    meta.sfx = '.txt'
    assert meta.sfx == '.txt'
    meta.sfx = None
    assert meta.sfx == '.html'

