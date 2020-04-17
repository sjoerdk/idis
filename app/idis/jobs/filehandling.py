""" Classes for working with files that are associated to job_ids

"""
import os
import uuid
from pathlib import Path
from shutil import copyfile


class JobFile:
    """ A local file in IDIS. Always has a job id.

    Intended to be lightweight object for abstracting away association between file and job id"""

    def __init__(self, job_id, path):
        """

        Parameters
        ----------
        job_id: int
            The id of the job that this file belongs to
        path: Path
            location of this file on disk
        """

        self.job_id = job_id
        self.path = Path(path)

    def __str__(self):
        return f"file for job {self.job_id} at '{self.path}'"

    @property
    def exists(self):
        return self.path.exists()

    @property
    def name(self):
        """File name of this job file"""
        return self.path.name


class SafeFolder:
    """A safe folder that will will rename files to prevent name clashes

    """

    def __init__(self, path):
        """A folder that you can ask for available names so you can avoid name clashes

        Parameters
        ----------
        path: str
            path to folder
        """
        self.path = Path(path)

    def get_available_path(self, job_file: JobFile):
        """Get a path to save the given file to. Add random string to filename to avoid clashes

        Parameters
        ----------
        job_file: JobFile
            Try to get the filename of this job file if possible.

        Returns
        -------
        Path
            full path including name where this file info might be saved

        """
        potential_path = Path(self.path) / job_file.name
        return self._get_available_name_for_path(potential_path)

    @staticmethod
    def _get_available_name_for_path(path: Path):
        """ Make sure path does not exist. Return different filename if needed """
        while path.exists():
            path = path.parent / str(uuid.uuid4())
        return path


class JobFolder(SafeFolder):
    """ A folder in which each file is associated with a job id

    """

    UNKNOWN_JOB_FOLDER_NAME = "UNKNOWN"

    def __init__(self, path):
        """ A folder storing job files.

        Parameters
        ----------
        path: Path or str
            full path to this folder
        """
        self.path = Path(path)

    def get_available_path(self, job_file: JobFile):
        """Get a path to save the given file to. Add random string to filename to avoid clashes

        Parameters
        ----------
        job_file: JobFile
            get a path to save the given job file in this folder

        Returns
        -------
        Path
            full path including name where this file info might be saved

        """

        folder = self._get_path_for_job(job_file.job_id)
        return self._get_available_name_for_path(folder / job_file.name)

    def _get_path_for_job(self, job_id):
        """Get the path in which files for the given job_id are kept

        Parameters
        ----------
        job_id: str
            id for job

        Returns
        -------
        Path
            path in which files for the given job_id are kept. Might not exist
        """
        if job_id:
            return self.path / str(job_id)
        else:
            return self.path / self.UNKNOWN_JOB_FOLDER_NAME

    def get_job_ids(self):
        """ Returns job id of each job that has files in this folder

        Notes
        -----
        Will silently discard any non-int job ids found in folder

        Returns
        -------
        List[str]
            ids of all jobs in this folder

        """
        if not self.path.exists():
            return []
        dir_names = [x.name for x in self.path.iterdir() if x.is_dir()]
        job_ids = []
        for dir_name in dir_names:
            try:
                job_ids.append(int(dir_name))
            except ValueError:
                next
        return job_ids

    def remove_empty_job_id(self, job_id):
        """Remove all records of job id from this folder. It will not show up in get_job_ids() anymore

        Parameters
        ----------
        job_id: int
            id of job to remove

        Raises
        ------
        JobFolderException:
            When there are still files associated with this job id in this folder or when this job id does not exist

        """
        path = self._get_path_for_job(job_id)
        try:
            os.rmdir(path)
        except FileNotFoundError:
            raise JobFolderException(
                f"Job id {job_id} is not known in this folder"
            )
        except OSError:
            raise JobFolderException(
                f"Cannot remove job id {job_id}, there are still files associated with this id"
            )

    def get_unknown_job_files(self):
        """Get files from this folder that could not be associated with any job

        Returns
        -------
        List[JobFile]
            full path to each file in this folder that is not associated with any job
            JobFile.job_id will be None

        """

        unknown_job_dir = self.path / self.UNKNOWN_JOB_FOLDER_NAME
        if not unknown_job_dir.exists():
            return []
        unknown_job_files = [
            JobFile(path=x, job_id=None)
            for x in unknown_job_dir.iterdir()
            if x.is_file()
        ]
        return unknown_job_files

    def get_files(self, job_id: int):
        """ get paths to all files belonging to the given job

        Returns
        -------
        List<JobFile>
            list with each file belonging to the given job

        Notes
        -----
        Will return empty list if job_id is not known

        """
        job_path = self._get_path_for_job(job_id)
        if not job_path.exists():
            return []
        else:
            return [
                JobFile(job_id=job_id, path=x)
                for x in job_path.iterdir()
                if x.is_file()
            ]

    def get_file_count(self, job_id: int):
        """get number of files in this folder for job with id

        Notes
        -----
        will return 0 for unknown jobs

        Returns
        -------
        int
           number of files


        """
        job_path = self._get_path_for_job(job_id)
        if not job_path.exists():
            return 0
        else:
            return len([x for x in job_path.iterdir() if x.is_file()])


def move_job_file(job_file: JobFile, destination: SafeFolder):
    """Move file to folder, creates folder path if needed

    Parameters
    ----------
    job_file: JobFile
        Copy this file
    destination: SafeFolder
        To this folder

    """
    source_path, destination_path = prepare_job_file_operation(
        job_file, destination
    )
    source_path.rename(destination_path)


def copy_job_file(job_file: JobFile, destination: SafeFolder):
    """Copy file to folder, creates folder path if needed

    Parameters
    ----------
    job_file: JobFile
        Copy this file
    destination: SafeFolder
        To this folder

    """
    source_path, destination_path = prepare_job_file_operation(
        job_file, destination
    )
    copyfile(str(source_path), str(destination_path))


def prepare_job_file_operation(job_file: JobFile, destination: SafeFolder):
    """Figure out name and path to send this job file to. Make sure the destination exists

    Parameters
    ----------
    job_file: JobFile
        The file to move or copy
    destination: SafeFolder
        The destination to send the file to

    Returns
    -------
    (Path, Path)
        source_path, destination_path. Destination path exists
    """

    source_path = job_file.path
    destination_path = destination.get_available_path(job_file)
    # assert destination path
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    return source_path, destination_path


def move_job_data(job_id: int, source: JobFolder, destination: SafeFolder):
    """Move all files associated with given job id from source to destination

    Parameters
    ----------
    job_id: str
        Move all files associated with this job
    source: JobFolder
        From this folder
    destination: SafeFolder
        to this folder

    Notes
    -----
    Will do nothing if job_id is not known. No exceptions are raised
    """

    files = source.get_files(job_id)
    if not files:
        return
    else:
        for file in files:
            move_job_file(file, destination)
        source.remove_empty_job_id(job_id)


class IDISServer:
    """Representation of the important

    """

    def __init__(
        self,
        pre_fetching_path,
        CTP_input_path,
        CTP_output_path,
        quarantine_path,
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
        quarantine_path: str
            full path to quarantine directory
        """

        self.pre_fetching_folder = JobFolder(pre_fetching_path)
        # self.CTP_server =


class JobFolderException(Exception):
    pass
