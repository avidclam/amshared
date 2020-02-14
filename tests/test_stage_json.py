from amshared import stage
from amshared.helpers import iter_equal
from pathlib import Path


def test_json_driver(tmp_path, json_samples):
    stage_folder_path = Path(tmp_path / 'stage')
    stg = stage.Stage(stage_folder_path)
    metadata = {'rubric': 'json', 'name': 'samples', 'format': 'json'}
    stg.save([(metadata, json_samples)])
    samples = stg.payload(metadata)  # read back
    assert all(iter_equal(s, samples[i]) for i, s in enumerate(json_samples))
