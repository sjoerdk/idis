from distutils import dir_util
from pathlib import Path
import pytest

from tests.factories import WadoServerFactory, FileOnDiskFactory
from idis.jobs.models import WadoServer, FileOnDisk, JobFolder, SafeFolder
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


@pytest.fixture()
def file_on_disk(resources_folder):
    file_info: FileOnDisk = FileOnDiskFactory(path=resources_folder / 'retrieve_file_from_disk' / 'file.dcm')
    return file_info


@pytest.fixture(scope='function')
def empty_folder(tmpdir_factory):
    """One-time empty folder

    Returns
    -------
    str
        path to folder

    """
    return tmpdir_factory.mktemp(basename='empty')


@pytest.mark.django_db
def test_encrypted_char_field():
    """Check the saving encrypted password """
    source = WadoServerFactory(name='a_source', password='a_plain_password')
    source.save()

    # retrieve the object from database again, password should be the same
    source_from_db = WadoServer.objects.filter(name='a_source').get()
    assert source_from_db.password == 'a_plain_password'


@pytest.mark.django_db
def test_retrieve_file_from_disk(pre_fetching_folder, file_on_disk):
    """Basic retrieval of files from a disk location"""
    # at the start the pre-fetching folder is empty
    assert len(list(pre_fetching_folder.path.glob('*'))) == 0

    # Get the file described in FileInfo file_on_disk
    file_on_disk.download(to_folder=pre_fetching_folder)

    # it should have been downloaded as job 1
    assert pre_fetching_folder.get_job_ids() == [1]
    # and contain one file
    assert len(pre_fetching_folder.get_files(1)) == 1


@pytest.mark.django_db
def test_job_folder(file_on_disk, empty_folder):
    # start with an empty folder
    job_folder = JobFolder(path=empty_folder)
    assert job_folder.get_job_ids() == []

    # download file
    file_on_disk.download(job_folder)

    # should now have one job
    assert job_folder.get_job_ids() == [file_on_disk.id]
    # and that job should have one file
    assert len(job_folder.get_files(file_on_disk.id)) == 1


@pytest.mark.django_db
def test_job_folder_do_not_overwrite(file_on_disk, empty_folder):
    job_folder = JobFolder(path=empty_folder)

    # download the same file twice
    file_on_disk.download(job_folder)
    file_on_disk.download(job_folder)

    # now there should be two files, because JobFolders never overwrite files
    assert len(job_folder.get_files(file_on_disk.id)) == 2


@pytest.mark.django_db
def test_job_folder_non_int_job_id(file_on_disk, empty_folder):
    job_folder = JobFolder(path=empty_folder)

    # download a file for two different job ids. In a JobFolder these are saved to separate folders
    file_on_disk.job.id = 1
    file_on_disk.download(job_folder)
    file_on_disk.job.id = 2
    file_on_disk.download(job_folder)

    # introduce a folder that should be ignored because it cannot be linked to a job id
    (job_folder.path / "non_int_folder").mkdir()
    # This should still yield only 2 job ids, and not crash
    assert job_folder.get_job_ids() == [1, 2]


@pytest.mark.django_db
def test_safe_folder_do_not_overwrite(file_on_disk, empty_folder):
    safe_folder = SafeFolder(path=empty_folder)

    # download the same file twice
    file_on_disk.download(safe_folder)
    file_on_disk.download(safe_folder)

    # now there should be two files, because SafeFolders never overwrite files
    assert len([x for x in safe_folder.path.glob('*') if x.is_file()]) == 2
