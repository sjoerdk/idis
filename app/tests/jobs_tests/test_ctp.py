from distutils import dir_util
from pathlib import Path

import pytest

from idis.jobs.ctp import CTPQuarantineFolder, IDISCTPQuarantine
from tests.jobs_tests import RESOURCE_PATH


@pytest.fixture
def test_resources_folder(tmpdir):
    """An example of a CTP quarantine base folder with several stages, some job files and some invalid files

    Returns
    -------
    str
        path to folder

    """
    template_folder = Path(RESOURCE_PATH) / "test_ctp" / "ctp_q"
    dir_util.copy_tree(str(template_folder), str(tmpdir))
    return tmpdir


@pytest.fixture
def empty_folder(tmpdir_factory):
    """One-time empty folder

    Returns
    -------
    str
        path to folder

    """
    return tmpdir_factory.mktemp(basename="empty")


@pytest.fixture()
def idis_ctp_quarantine(test_resources_folder, empty_folder):
    """ An idis quarantine folder linked to some test ctp folders with some files"""

    q_folders = [
        CTPQuarantineFolder(
            test_resources_folder / "DicomAnonymizerFullDates",
            description="Something went wrong with settings dates",
        ),
        CTPQuarantineFolder(
            test_resources_folder / "DicomAnonymizerKeepSafePrivateTags",
            description="Some unsupported private tags might be in your data",
        ),
        CTPQuarantineFolder(test_resources_folder / "DicomAnonymizerModifiedDates"),
        CTPQuarantineFolder(
            test_resources_folder / "DicomAnonymizerFaultyFiles",
            description="Things went really wrong",
        ),
    ]
    return IDISCTPQuarantine(
        base_folder=Path(empty_folder), ctp_quarantine_folders=q_folders
    )


def test_ctp_quarantine(test_resources_folder):
    """Check getting all files from quarantine folder"""
    qf = CTPQuarantineFolder(test_resources_folder / "DicomAnonymizerFullDates")
    files = qf.get_files()
    assert set(x.name for x in files) == set(["file1", "file2"])


def test_ctp_quarantine_job_files(test_resources_folder):
    """Check getting all files from quarantine folder, but also figure out which job they belong to"""
    qf = CTPQuarantineFolder(test_resources_folder / "DicomAnonymizerFullDates")
    job_files = qf.get_job_files()
    assert set(x.name for x in job_files) == {"file1", "file2"}
    assert set(x.job_id for x in job_files) == {1, 2}



@pytest.mark.parametrize(
    "file_name", ["file8_no_dicom", "file7_no_private_creator", "file6_no_job_id"]
)
def test_idis_dicom_dataset_messy_input(test_resources_folder, file_name):
    """Ensuring responses for messy files. Should return JobFile with None for job id"""
    qf = CTPQuarantineFolder(test_resources_folder / "DicomAnonymizerFaultyFiles")
    files = {file.name: file for file in qf.get_files()}
    job_file = qf.path_to_job_file(files[file_name])
    assert job_file.job_id is None


def test_ctp_quarantine_job_files_messy_input(test_resources_folder):
    """Try to sort quarantine folder with files that have problems.. missing tags, not dicom files etc."""
    qf = CTPQuarantineFolder(test_resources_folder / "DicomAnonymizerFaultyFiles")

    # folder with 1 OK, 3 faulty files should not cause exceptions but instead yield some jobs with job_id = None
    job_files = qf.get_job_files()
    assert len(job_files) == 4
    assert [x.job_id for x in job_files] == [1, None, None, None]


def test_idis_ctp_quarantine_scraping(idis_ctp_quarantine):
    """Take all files from CTP quarantine folders and sort them by job"""

    # IDIS quarantine should be empty to start
    assert len(list(idis_ctp_quarantine.base_folder.glob("*"))) == 0
    assert idis_ctp_quarantine.get_job_ids() == []

    # move all files from CTP quarantine to IDIS quarantine and check
    idis_ctp_quarantine.scrape()

    assert idis_ctp_quarantine.get_job_ids() == [1, 2, 3]
    assert len(idis_ctp_quarantine.get_files(job_id=1)) == 2
    assert len(idis_ctp_quarantine.get_files(job_id=2)) == 2
    assert len(idis_ctp_quarantine.get_files(job_id=3)) == 1
    assert len(idis_ctp_quarantine.get_unknown_job_files()) == 3

    # unknown jobs should not raise exceptions
    assert idis_ctp_quarantine.get_files(job_id=100) == []


def test_idis_ctp_archiving(idis_ctp_quarantine):
    """You can archive all files for a job, moving them out of the way or regular processing, but not deleting"""
    # make sure there are some files in IDIS quarantine
    idis_ctp_quarantine.scrape()
    assert idis_ctp_quarantine.get_job_ids() == [1, 2, 3]

    # check how many files are in active quarantine for job 2
    files_for_job = idis_ctp_quarantine.get_files(job_id=2)

    # now archive the files for this job
    idis_ctp_quarantine.archive(job_id=2)

    # now this job should no longer appear
    assert idis_ctp_quarantine.get_job_ids() == [1, 3]
    # and have no files active
    assert idis_ctp_quarantine.get_files(job_id=2) == []

    # and the two files should have been moved to archive
    assert len([x for x in idis_ctp_quarantine.archived_base_folder.rglob('*') if x.is_file()]) == len(files_for_job)


