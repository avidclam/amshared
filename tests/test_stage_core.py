import pytest
import json
import pickle
from datetime import datetime
from amshared import stage


def test_stage_bad_start(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stage_folder_path.touch()
    with pytest.raises(FileNotFoundError, match='directory'):
        stg = stage.Stage(stage_folder_path)


def test_stage_init(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stg = stage.Stage(stage_folder_path)
    assert stage_folder_path.exists()
    assert stg.topmost == stage_folder_path


def test_stage_save(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stg = stage.Stage(stage_folder_path)
    dataflow_saved = stg.save(dataflow)
    assert len(dataflow_saved) == len(dataflow)
    assert all([m['name'] == '__heap__' for m, c in dataflow_saved[:3]])
    assert all([c is None for m, c in dataflow_saved])
    level_content = stage_folder_path / 'content'
    level_metadata = stage_folder_path / 'metadata'
    for stage_object in (
            'post',
            'post/mail',
            'post/mail/__heap__',
            'post/mail/chain',
            'post/parcel'
    ):
        assert (level_content / stage_object).exists()
        assert (level_metadata / stage_object).exists()


def test_stage_meta(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stg = stage.Stage(stage_folder_path)
    stg.save(dataflow)
    meta_path = stage_folder_path / 'metadata/post/parcel/secret.meta'
    with open(meta_path, 'r') as file:
        metadata = json.load(file)
    # Check other metadata
    assert metadata['rubric'] == 'post/parcel'
    assert metadata['name'] == 'secret'
    assert metadata['format'] == 'pickle'
    assert 'part' not in metadata


def test_stage_content(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stg = stage.Stage(stage_folder_path)
    stg.save(dataflow)
    txt_path = stage_folder_path / 'content/post/mail/unique.txt'
    with open(txt_path, 'r') as file:
        content = file.read()
    assert content == 'From Mars'
    json_path = stage_folder_path / 'content/post/mail/chain/10.json'
    with open(json_path, 'r') as file:
        content = json.load(file)
    assert 'message' in content
    assert content['message'] == 'Part ten'
    pickle_path = stage_folder_path / 'content/post/parcel/secret.pickle'
    with open(pickle_path, 'rb') as file:
        content = pickle.load(file)
    assert callable(content.reveal)
    nlines = len(content.reveal().splitlines())
    assert nlines == 2


def test_stage_load(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stg = stage.Stage(stage_folder_path)
    stg.save(dataflow)
    request = {'rubric': 'post/mail'}, True
    for metadata, content in stg.load((request,)):
        assert metadata['name'] == '__heap__'
        assert isinstance(content, str)
    request = {'rubric': 'post/mail'}, False
    for metadata, content in stg.load((request,)):
        assert metadata['name'] == '__heap__'
        assert content is None
    request = {'rubric': 'post/mail', 'name': 'chain', 'part': '*'}, True
    for metadata, content in stg.load((request,)):
        assert metadata['part'] in (1, 10)
        assert 'message' in content


def test_stage_rubric(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stg = stage.Stage(stage_folder_path)
    stg.save(dataflow)
    rbc = stage.Rubric(stg, 'post/mail')
    assert rbc.atomic_names == ['unique']
    assert rbc.multipart_names == ['chain']
    assert sum(rbc.get_name_parts('chain')) == 11
    assert sum(rbc.heap_parts) == 6


def test_stage_delete(tmp_path, dataflow):
    stage_folder_path = tmp_path / 'stage'
    stg = stage.Stage(stage_folder_path)
    stg.save(dataflow)
    meta_path = stage_folder_path / 'metadata/post/parcel/secret.meta'
    content_path = stage_folder_path / 'content/post/parcel/secret.pickle'
    rubric_path = stage_folder_path / 'content/post/parcel'
    assert meta_path.exists()
    assert content_path.exists()
    assert rubric_path.exists()
    stg.delete([({'rubric': 'post/parcel', 'name': 'secret'}, None)])
    assert not meta_path.exists()
    assert not content_path.exists()
    assert not rubric_path.exists()
