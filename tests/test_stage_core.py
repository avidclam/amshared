import json
import pickle
from datetime import datetime
from amshared import stage
from amshared.stage.constants import MK_CTIME, XTRA_CTIME_FORMAT


def test_stage_init(tmp_path, dataflow):
    stage_folder = tmp_path / 'stage'
    stg = stage.Stage(stage_folder)
    assert stage_folder.exists()
    assert stg.topmost == stage_folder


def test_stage_save(tmp_path, dataflow):
    stage_folder = tmp_path / 'stage'
    stg = stage.Stage(stage_folder)
    stg.save(dataflow)
    level_content = stage_folder / 'content'
    level_metadata = stage_folder / 'metadata'
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
    stage_folder = tmp_path / 'stage'
    stg = stage.Stage(stage_folder)
    stg.save(dataflow)
    meta_path = stage_folder / 'metadata/post/parcel/secret.meta'
    with open(meta_path, 'r') as file:
        metadata = json.load(file)
    # Check timestamp
    tolerance = 3  # sec
    date_time = datetime.strptime(metadata[MK_CTIME], XTRA_CTIME_FORMAT)
    delta = datetime.utcnow() - date_time
    assert delta.total_seconds() < tolerance
    # Check other metadata
    assert metadata['rubric'] == 'post/parcel'
    assert metadata['name'] == 'secret'
    assert metadata['format'] == 'pickle'
    assert 'part' not in metadata


def test_stage_content(tmp_path, dataflow):
    stage_folder = tmp_path / 'stage'
    stg = stage.Stage(stage_folder)
    stg.save(dataflow)
    txt_path = stage_folder / 'content/post/mail/unique.txt'
    with open(txt_path, 'r') as file:
        content = file.read()
    assert content == 'From Mars'
    json_path = stage_folder / 'content/post/mail/chain/10.json'
    with open(json_path, 'r') as file:
        content = json.load(file)
    assert 'message' in content
    assert content['message'] == 'Part ten'
    pickle_path = stage_folder / 'content/post/parcel/secret.pickle'
    with open(pickle_path, 'rb') as file:
        content = pickle.load(file)
    assert callable(content.reveal)
    nlines = len(content.reveal().splitlines())
    assert nlines == 2


def test_stage_rubric_folder(tmp_path, dataflow):
    stage_folder = tmp_path / 'stage'
    stg = stage.Stage(stage_folder)
    stg.save(dataflow)
    atomic_names = stg.lsnames('post/mail', atomic=True)
    assert atomic_names == ['unique']
    multipart_names = stg.lsnames('post/mail', atomic=False)
    assert multipart_names == ['chain']
    lhm = stg.last_heap_meta('post/mail')
    metadata = lhm[0][0]
    assert metadata['part'] == 3


def test_stage_delete(tmp_path, dataflow):
    stage_folder = tmp_path / 'stage'
    stg = stage.Stage(stage_folder)
    stg.save(dataflow)
    meta_path = stage_folder / 'metadata/post/parcel/secret.meta'
    content_path = stage_folder / 'content/post/parcel/secret.pickle'
    rubric_path = stage_folder / 'content/post/parcel'
    assert meta_path.exists()
    assert content_path.exists()
    assert rubric_path.exists()
    stg.delete([({'rubric': 'post/parcel', 'name': 'secret'}, None)])
    assert not meta_path.exists()
    assert not content_path.exists()
    assert not rubric_path.exists()
