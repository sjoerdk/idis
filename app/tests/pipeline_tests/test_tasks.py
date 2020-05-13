from pathlib import Path
from shutil import copyfile
from unittest.mock import Mock

import pytest
from anonapi.testresources import MockAnonClientTool
from idissend.pipeline import DefaultPipeline

from idis.pipeline.tasks import run_pipeline_once, init_pipeline, settings
from tests.factories import StreamFactory
from tests.pipeline_tests import RESOURCE_PATH


@pytest.fixture
def a_default_pipeline(
    monkeypatch, tmpdir, mock_anon_client_tool
) -> DefaultPipeline:
    """A default modality import pipeline for testing:
    * stores data in tmp dir
    * two streams
    * communication with IDIS web API is mocked
    """
    _ = StreamFactory()
    _ = StreamFactory()

    monkeypatch.setattr(settings, "PIPELINE_BASE_PATH", Path(tmpdir))
    pipeline = init_pipeline()
    pipeline.pending.idis_connection.client_tool = mock_anon_client_tool
    return pipeline


@pytest.fixture
def mock_anon_client_tool():
    """An anonymization API client tool that does not hit the server but returns
    some example responses instead. Also records calls"""

    # mock wrapper to be able to record responses
    return Mock(wraps=MockAnonClientTool())


@pytest.mark.django_db
def test_run_pipeline_once():
    """Minimal test for pipeline run. Complete tests are in idissend module."""

    # init two streams for pipeline to work with
    _ = StreamFactory()
    _ = StreamFactory()

    # this should not fail
    _ = run_pipeline_once()


@pytest.mark.django_db
def test_run_pipeline_with_django_objects(
    a_default_pipeline, mock_anon_client_tool
):
    """Pipeline replaces some standard idissend objects with django ORM equivalents.
    Verify that this works """
    pipeline = a_default_pipeline
    pipeline.incoming.assert_all_paths()  # make sure the incoming folders exist

    # run pipeline empty, for good measure
    pipeline.run_once()

    # now insert a single file in one of the streams of in the incoming stage
    a_stream = pipeline.incoming.streams[0]
    incoming_path = pipeline.incoming.get_path_for_stream(a_stream)
    copyfile(RESOURCE_PATH / "a_dicom_file", incoming_path / "a_dicom_file")

    # and run again
    pipeline.run_once()

    # this should have created a job with IDIS via the api client tool
    mock_client_tool = pipeline.pending.idis_connection.client_tool
    assert mock_client_tool.create_path_job.called

    # recreates a bug with converting idis_profile object to string
    call_args = mock_client_tool.create_path_job.call_args.kwargs
    assert call_args["project_name"] == a_stream.idis_profile.title
