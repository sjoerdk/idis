from distutils import dir_util
from pathlib import Path
import pytest

from tests.factories import WadoServerFactory, FileOnDiskFactory
from idis.jobs.models import WadoServer, FileOnDisk
from tests.jobs_tests import RESOURCE_PATH


@pytest.fixture
def resources_folder(tmpdir_factory):
    """A one-time copy of the test resources folder

    Returns
    -------
    str
        path to folder

    """
    template_folder = Path(RESOURCE_PATH)
    temp_dir = tmpdir_factory.mktemp('resources')
    dir_util.copy_tree(str(template_folder), str(temp_dir))
    return temp_dir


@pytest.mark.django_db
def test_encrypted_char_field():
    """Check the saving encrypted password """
    source = WadoServerFactory(name='a_source', password='a_plain_password')
    source.save()

    # retrieve the object from database again, password should be the same
    source_from_db = WadoServer.objects.filter(name='a_source').get()
    assert source_from_db.password == 'a_plain_password'


@pytest.mark.django_db
def test_retrieve_file_from_disk(pre_fetching_folder, resources_folder):
    """Basic retrieval of files from a disk location"""
    # at the start the pre-fetching folder is empty
    assert len(list(pre_fetching_folder.path.glob('*'))) == 0

    # Create a file info describing where a the file is and how to get it
    file_info: FileOnDisk = FileOnDiskFactory(path=resources_folder / 'retrieve_file_from_disk' / 'file.dcm')
    # Then get it
    file = file_info.get_file(pre_fetching_folder=pre_fetching_folder)

    # it should have been downloaded as job 1
    assert pre_fetching_folder.get_job_ids() == [1]
    # and contain one file
    assert len(pre_fetching_folder.get_files(1)) == 1

