import pytest

from distutils import dir_util
from pathlib import Path

from idis.jobs.filehandling import (
    JobFolder,
    SafeFolder,
    JobFile,
    copy_job_file,
)
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
    temp_dir = tmpdir_factory.mktemp("resources")
    dir_util.copy_tree(str(template_folder), str(temp_dir))
    return temp_dir


@pytest.fixture()
def job_file(resources_folder):
    """A copy of a file associated with a single job"""
    return JobFile(
        job_id=3, path=resources_folder / "test_filehandling" / "test_file.dcm"
    )


@pytest.fixture(scope="function")
def empty_folder(tmpdir_factory):
    """One-time empty folder

    Returns
    -------
    str
        path to folder

    """
    return tmpdir_factory.mktemp(basename="empty")


@pytest.fixture()
def job_folder(empty_folder):
    """An empty folder that you can store job files in"""
    return JobFolder(path=empty_folder)


def test_job_folder(job_file, job_folder):
    """A job folder should sort job files per jobs """
    # copy one jobfile to the folder
    copy_job_file(job_file, job_folder)

    # the folder should now know this id
    assert job_folder.get_job_ids() == [job_file.job_id]

    # and have one file for this id
    assert len(job_folder.get_files(job_file.job_id)) == 1


def test_job_folder_do_not_overwrite(job_file, job_folder):
    """Files with the same name will not overwrite existing ones"""

    # copy the same file twice
    copy_job_file(job_file, job_folder)
    copy_job_file(job_file, job_folder)

    # now there should be two files, because JobFolders never overwrite files
    assert len(job_folder.get_files(job_file.job_id)) == 2


def test_safe_folder_do_not_overwrite(job_file, empty_folder):
    """Safe folders should not overwrite files, but rather rename if needed"""
    safe_folder = SafeFolder(path=empty_folder)

    copy_job_file(job_file, safe_folder)
    copy_job_file(job_file, safe_folder)

    assert len([x for x in safe_folder.path.glob("*") if x.is_file()]) == 2


def test_job_folder_unparsable_folder(job_file, job_folder):
    """Internally a job folder has sub folders for each job id. Handle unparsable job ids gracefully"""
    copy_job_file(job_file, job_folder)

    # introduce a folder that should be ignored because it cannot be linked to a job id
    (job_folder.path / "non_int_folder").mkdir()

    # This should still yield only 1 job id, ignoring the weird folder
    assert job_folder.get_job_ids() == [job_file.job_id]


def test_job_folder_missing_job_id(job_file, job_folder):
    """job files with missing id should be saved in a special 'unknown' category"""

    job_file.job_id = None
    copy_job_file(job_file, job_folder)

    assert job_folder.get_job_ids() == []
    assert len(job_folder.get_unknown_job_files()) == 1
