""" Functions and classes for dealing with CTP. CTP is the java-based program that
does the actual anonymization.

"""
from pathlib import Path
from typing import List

import pydicom

from idis.jobs.filehandling import JobFolder, JobFile, move_job_data, move_job_file
from pydicom.datadict import add_private_dict_entries
from pydicom.errors import InvalidDicomError


class CTPQuarantineFolder:
    """A quarantine made by CTP for a single stage"""

    def __init__(self, path, description=None):
        """

        Parameters
        ----------
        path: Path
            full path to this quarantine folder
        description: str, optional
            description of this folder. Used for telling users why file might end
            up in this folder. Defaults to folder
            name
        """
        self.path = Path(path)
        if description:
            self.description = f"Quarantine folder {self.path.name} ({description})"
        else:
            self.description = f"Quarantine folder {self.path.name}"

    def __str__(self):
        return f"CTP quarantine folder at {self.path}"

    def get_files(self):
        """Get paths to all files in this quarantine folder

        Returns
        -------
        List[Path]
            full path to each file in this Quarantine folder

        """
        return list(x for x in self.path.glob("*") if x.is_file())

    def get_job_files(self):
        """

        Returns
        -------
        List[JobFile]
            job for each file in this folder, or None if no job can be found

        """

        paths = self.get_files()
        job_files = []
        for path in paths:
            job_files.append(self.path_to_job_file(path))

        return job_files

    @staticmethod
    def path_to_job_file(path):
        """Return JobFile with associated job for each path

        Parameters
        ----------
        path: Path
            path to a DICOM file that has IDIS private tag for JobID set

        Returns
        -------
        JobFile
            containing file path and associated job. If file cannot be associated
            with job JobFile.job_id will be None

        Notes
        -----
        returned JobFile.job_id can be None if file cannot be associated with a job


        """
        try:
            ds = IDISDICOMDataSet(pydicom.dcmread(str(path)))
        except InvalidDicomError:
            return JobFile(job_id=None, path=path)
        try:
            job_id = ds.get_idis_tag_value("JobID")
            return JobFile(job_id=job_id, path=path)
        except KeyError:
            return JobFile(job_id=None, path=path)


class IDISDICOMDataSet:
    """Holds a pydicom dataset, adds extra functionality for dealing with
    IDIS-specific private tags Alternative to this would be to add to pydicom itself
    and post merge requests, but that is for later.
    """

    PRIVATE_CREATOR = "RADBOUDUMCANONYMIZER"
    IDIS_PRIVATE_TAGS = {
        0x00750027: ("LO", "1", "JobID"),
        0x00750028: ("LO", "1", "SourceInstanceID", "", "SourceInstanceID"),
    }

    def __init__(self, dataset):
        """

        Parameters
        ----------
        dataset: pydicom.dataset.FileDataset
            wrap around this dataset
        """
        self.dataset = dataset
        add_private_dict_entries(self.PRIVATE_CREATOR, self.IDIS_PRIVATE_TAGS)

    def get_idis_tag_value(self, tag_name):
        """Get the dicom value given by the idis private tag tag_name

        Parameters
        ----------
        tag_name: str
            name of the tag

        Raises
        ------
        KeyError:
            when tag is not found in this dataset

        """

        private_tags = [de for de in self.dataset if hasattr(de, "private_creator")]
        idis_tags = {
            tag.name: tag
            for tag in private_tags
            if tag.private_creator == self.PRIVATE_CREATOR
        }
        # pydicom puts square brackets around the names of private tags to
        # differentiate it from standard tags
        return idis_tags[f"[{tag_name}]"].value


class IDISQuarantineFolder(JobFolder):
    """A quarantine folder in which each file is always associated with a job id"""

    def __init__(self, path, description):
        """

        Parameters
        ----------
        path: Path or str
            full path to this folder

        description: str, optional
            description of this folder. Used for telling users why file might
            end up in this folder. Defaults to folder
            name

        description
        """
        super().__init__(path)
        self.description = description

    def __str__(self):
        return f"IDIS quarantine folder at {self.path}"

    def get_files(self, job_id: int):
        """ get paths to all files belonging to the given job, add source
        quarantine folder

        Returns
        -------
        List[QuarantinedJobFile]
            list with each file belonging to the given job

        Raises
        ------
        FileNotFoundError
            when given job id does not exist in this folder
        """
        job_files: JobFile = super().get_files(job_id)
        return [self.to_quarantine_job_file(job_file) for job_file in job_files]

    def to_quarantine_job_file(self, job_file: JobFile):
        """Add link to this quarantine dir to given JobFile

        """

        return QuarantinedJobFile(
            job_id=job_file.job_id, path=job_file.path, quarantine_folder=self
        )


class IDISCTPQuarantine:
    """Scrapes CTP quarantine folders. Answers questions such as 'How many files are quarantined for job X'

    Notes
    -----
    CTP has quarantine folders for each of its stages. It cannot be configured to separate files per
    job. Hence this class that can scrape out all quarantined files and sort them properly.

    IDISCTPQuarantine knows three main sets of folders:

    * CTP quarantine folders:           Folders that CTP fills with quarantined files
    * IDIS active quarantine folders:   Mirrors CTP folders. Base for most IDISCTPQuarantine functions
    * IDIS archived quarantine folders: Files here are mostly ignored, saved for future reference

    """

    def __init__(self, base_folder: Path, ctp_quarantine_folders):
        """Create an IDIS quarantine that scrapes the given CTP quarantine folders to base_folder and
        makes their contents manageable.

        Parameters
        ----------
        base_folder: Path
            Keep all data in this folder

        ctp_quarantine_folders: List[CTPQuarantineFolder]
            list of CTP quarantine folders to mirror

        """
        self.base_folder = Path(base_folder)
        self.active_base_folder = self.base_folder / "active"
        self.archived_base_folder = self.base_folder / "archived"
        self.ctp_folder_mapping = self.create_ctp_folder_mapping(ctp_quarantine_folders)
        self.archive_mapping = self.create_archive_mapping(self.active_quarantine_folders)

    def __str__(self):
        return f"IDIS CTP quarantine at {self.base_folder}"

    @property
    def ctp_folders(self):
        """All CTP folders that this Quarantine mirrors """
        return list(self.ctp_folder_mapping.keys())

    @property
    def active_quarantine_folders(self):
        """All active IDIS quarantine folders """
        return list(self.ctp_folder_mapping.values())

    def create_ctp_folder_mapping(
        self, ctp_quarantine_folders: List[CTPQuarantineFolder]
    ):
        """Return a mapping from each CTP quarantine folder to the active IDIS
        quarantine folder that mirrors it

        Parameters
        ----------
        ctp_quarantine_folders: List[QuarantineFolder]

        Returns
        -------
        Dict[Path: IDISQuarantineFolder]
            mapping from each ctp to idis quarantine folder

        """
        folder_links = {}
        for ctp_folder in ctp_quarantine_folders:
            ctp_folder_name = ctp_folder.path.name
            idis_mirror_folder = IDISQuarantineFolder(
                path=self.active_base_folder / ctp_folder_name,
                description=ctp_folder.description,
            )
            folder_links[ctp_folder] = idis_mirror_folder
        return folder_links

    def scrape(self):
        """Move all files from CTP quarantine to this folder

        Notes
        -----
        Reads DICOM tags from each file to determine job id
        """
        for ctp_folder, idis_folder in self.ctp_folder_mapping.items():
            ctp_folder: CTPQuarantineFolder
            job_files = ctp_folder.get_job_files()
            for job_file in job_files:
                move_job_file(job_file, destination=idis_folder)

    def archive(self, job_id):
        """Move all files for this job from activate to archive

        Parameters
        ----------
        job_id

        """
        for active, archive in self.archive_mapping.items():
            move_job_data(job_id=job_id, source=active, destination=archive)

    def get_files(self, job_id):
        """Get all files belonging to the given job from this quarantine

        Returns
        -------
        List[QuarantinedJobFile]
            All files belonging to this job, linked to the quarantine they were
            found in

        Raises
        ------
        FileNotFoundError
            when given job id does not exist in this folder

        """
        files = []
        for idis_q_folder in self.ctp_folder_mapping.values():
            try:
                files = files + idis_q_folder.get_files(job_id)
            except FileNotFoundError:
                continue
        return files

    def get_file_count(self, job_id):
        """Get number of files that are in quarantine for this job
        
        Parameters
        ----------
        job_id: int
            job id to check
        
        Returns
        -------
        int
            number of files that are in this IDIS quarantine for this job

        Notes
        -----
        Returns 0 if the job id is not in quarantine at all

        """
        count = 0
        for idis_q_folder in self.ctp_folder_mapping.values():
            try:
                count += idis_q_folder.get_file_count(job_id)
            except FileNotFoundError:
                continue
        return count

    def get_unknown_job_files(self):
        """Get all files in the quarantine not mapped to any job

        Returns
        -------
        List of Path
            All files belonging to this job, linked to the quarantine they were
            found in

        Raises
        ------
        FileNotFoundError
            when given job id does not exist in this folder

        """
        files = []
        for idis_folder in self.ctp_folder_mapping.values():
            try:
                job_files = idis_folder.get_unknown_job_files()
                files = files + [
                    idis_folder.to_quarantine_job_file(x) for x in job_files
                ]
            except FileNotFoundError:
                continue

        return files

    def get_job_ids(self):
        """Get ids of all jobs for which there are files in this quarantine

        Returns
        -------
        List of int
            id for each job that has files in this quarantine

        """
        ids = []
        for idis_folder in self.ctp_folder_mapping.values():
            ids = ids + idis_folder.get_job_ids()
        return list(set(ids))

    def create_archive_mapping(self, active_quarantine_folders):
        """Map each active quarantine folder to an archive mirror

        Parameters
        ----------
        active_quarantine_folders: List[IDISQuarantineFolder]

        Returns
        -------
        Dict[IDISQuarantineFolder, IDISQuarantineFolder]
            mapping active folder -> archive folder for each input folder
        """

        mapping = {}
        for active in active_quarantine_folders:
            archived = IDISQuarantineFolder(
                path=self.archived_base_folder / active.path.name,
                description="Archive for " + active.description)
            mapping[active] = archived
        return mapping


class QuarantinedJobFile(JobFile):
    """A JobFile linked to a certain quarantine directory"""

    def __init__(self, *args, quarantine_folder: CTPQuarantineFolder, **kwargs):
        super().__init__(*args, **kwargs)
        self.quarantine_folder = quarantine_folder


class IDISServer:
    """Collection of all locations and functions

    """

    def __init__(
        self, pre_fetching_path, CTP_input_path, CTP_output_path, quarantine_base_path
    ):
        """

        Parameters
        ----------
        pre_fetching_path: str
            full path to folder to put newly downloaded files in
        CTP_input_path: str
            full path to the folder that CTP reads its input files from
        CTP_output_path: str
            full path to CTP output folder
        quarantine_base_path: str
            full path to quarantine directory
        """

        self.pre_fetching_folder = JobFolder(pre_fetching_path)
        # self.CTP_server =

class JobFileParseException(Exception):
    pass
