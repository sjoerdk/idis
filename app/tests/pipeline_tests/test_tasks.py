import pytest

from idis.pipeline.tasks import run_pipeline_once
from tests.factories import StreamFactory


@pytest.mark.django_db
def test_run_pipeline_once():
    """Minimal test for pipeline run. Complete tests are in idissend module."""

    # init two streams for pipeline to work with
    _ = StreamFactory()
    _ = StreamFactory()

    # this should not fail
    _ = run_pipeline_once()
