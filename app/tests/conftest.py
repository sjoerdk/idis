import pytest
from django.conf import settings
from django.test import RequestFactory

from idis.jobs.filehandling import JobFolder

from tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> settings.AUTH_USER_MODEL:
    return UserFactory()


@pytest.fixture
def request_factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture(autouse=True)
def pre_fetching_folder(settings, tmpdir):
    """The folder that IDIS fetches all incoming data into by default"""
    settings.IDIS_PRE_FETCHING_FOLDER = tmpdir.strpath
    return JobFolder(tmpdir.strpath)
