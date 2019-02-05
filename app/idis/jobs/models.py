import abc
import os
from pathlib import Path
from shutil import copyfile

from django.db import models
from django.conf import settings
from django.core.files import File

from encrypted_model_fields.fields import EncryptedCharField


class Profile(models.Model):
    """Anonymisation profile. Determines how the data is to be anonymised.

    Based on the DICOM standard confidentiality profile
    (http://dicom.nema.org/medical/dicom/current/output/html/part15.html#sect_E.2)

    and the ten application level Confidentiality Options which modify the standard profile

    """

    def __str__(self):
        return f"Profile '{self.title}'"

    title = models.CharField(
        max_length=64, blank=True, default="", help_text="Short title for this profile"
    )

    description = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="Short description of this profile, max 1024 characters.",
    )

    Basic = models.BooleanField(
        default=True,
        help_text="Basic confidentiality profile. DICOM standard anonymisation",
    )

    CleanPixelData = models.BooleanField(
        default=True, help_text="Try to remove any burned in annotations"
    )
    CleanVisualFeatures = models.BooleanField(
        default=True,
        help_text="Try to remove or scramble face if this is present in the data ",
    )
    CleanGraphics = models.BooleanField(
        default=True,
        help_text="Remove graphics, text annotations or overlays. Does not include structured reports",
    )
    CleanStructuredContent = models.BooleanField(
        default=True,
        help_text=(
            "Clean information encoded in SR Content Items or Acquisition Context or Specimen "
            "Preparation Sequence Items "
        ),
    )
    CleanDescriptors = models.BooleanField(
        default=True, help_text="Clean free text fields like study description"
    )

    # Options that retain certain information in that would otherwise be removed by basic profile
    RetainFullDates = models.BooleanField(
        default=True, help_text="Keep date and time information"
    )

    RetainModifiedDates = models.BooleanField(
        default=True, help_text="Add a certain increment to date and time information"
    )
    RetainPatientCharacteristics = models.BooleanField(
        default=True, help_text="Keep information like age, sex, height and weight"
    )
    RetainDeviceIdentity = models.BooleanField(
        default=True, help_text="Keep information about the device the scan was made on"
    )
    RetainUIDs = models.BooleanField(
        default=True, help_text="Keep IDs such as study UID, patient ID etc."
    )
    RetainSafePrivate = models.BooleanField(
        default=True,
        help_text="Keep private tags that are explicitly marked as not containing any patient information",
    )


class FileBatch(models.Model):
    """A collection of files under a single description.


    This allows for both arbitrary collections of files as job input, but also human-readable descriptions like
    for example 'All files for Study xxx'
    """

    description = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="Short description of this batch, max 1024 characters.",
    )


class Job(models.Model):
    """A command to anonymise some data.

    Contains all information to anonymise data. Where is it, how to anonymise, where it should go
    """

    CANCELLED = "CANCELLED"
    PENDING = "PENDING"
    DOWNLOADING = "DOWNLOADING"
    PROCESSING = "PROCESSING"
    ERROR = "ERROR"
    DONE = "DONE"

    JOB_STATUS_CHOICES = (
        (CANCELLED, "Cancelled"),
        (PENDING, "Pending"),
        (DOWNLOADING, "Downloading"),
        (PROCESSING, "Processing"),
        (ERROR, "Error"),
        (DONE, "Done"),
    )

    def __str__(self):
        return f"job {self.id}"

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The user that created this",
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    profile = models.ForeignKey(
        Profile,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The anonymisation profile to be used",
    )
    status = models.CharField(
        choices=JOB_STATUS_CHOICES, default=PENDING, max_length=32
    )
    error = models.CharField(
        max_length=1024, default="", blank=True, help_text="Error message, if any"
    )

    files_downloaded = models.IntegerField(default=0, blank=True)
    files_processed = models.IntegerField(default=0, blank=True)
    files_quarantined = models.IntegerField(default=0, blank=True)
    number_of_retries = models.IntegerField(
        default=0, blank=True, help_text="Number of times processing has been retried"
    )
    description = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="Optional text to describe this job",
    )
    priority = models.IntegerField(
        default=10,
        blank=True,
        help_text="Higher values means higher priority for processing this job",
    )
    input_files = models.ForeignKey(
        FileBatch,
        null=True,
        on_delete=models.SET_NULL,
        help_text="The files that are processed in this job",
    )


class Storage(models.Model):
    """Something you can send files to and/or receive files from

    The built in django storage class django.core.files.storage.Storage is fully based on configuration from the
    settings file. In IDIS we define storage providers in the database. After long study it seems the inbuilt django
    system is designed for different purposes. Extending it would needlessly complicate things.
    """

    class Meta:
        abstract = True

    def send_file(self, job_file):
        """Send the given file to this source

        Parameters
        ----------
        job_file: JobFile

        """
        raise (
            NotImplementedError("This is an abstract base class. Call a child class")
        )

    def download_file_to(self, file_info):
        """Get the file described in file_info from this source. Stores the file locally in
        'settings.IDIS_PRE_FETCHING_FOLDER'

        Parameters
        ----------
        file_info: FileInfo
            information uniquely defining a single file

        Returns
        -------
        JobFile
            The file

        """
        raise (
            NotImplementedError("This is an abstract base class. Call a child class")
        )


class FileInfo(models.Model):
    """"Describes a single remote file and how to get it.

    """

    class Meta:
        abstract = True

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The job this file is associated with",
    )
    source = models.ForeignKey(
        Storage,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Where this data is coming from",
    )
    batch = models.ForeignKey(
        FileBatch,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Optional collection of files that this file belongs to",
    )

    @abc.abstractmethod
    def file_name(self):
        """Returns a the filename under which this file can be saved

        Returns
        -------
        str:
            filename for this file.
        """
        return

    def get_file(self, pre_fetching_folder=settings.IDIS_PRE_FETCHING_FOLDER):
        """Return a file object for this file. Retrieve from external source if needed. Downloads to
        'settings.IDIS_PRE_FETCHING_FOLDER'

        Returns
        -------
        JobFile
            The file described by this info

        Raises
        ------
        FileNotFoundError
            If file cannot be retrieved

        """
        # idis
        return self.source.download_file_to(file_info=self, folder=pre_fetching_folder)


class JobFile:
    """ A file in IDIS. Always belongs to a job """

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
        self.path = path


class SafeFolder:
    """A safe folder that will will rename files to prevent name clashes

    """
    def __init__(self, path):
        """A folder that you can ask for available names so you can avoid name clashes

        Parameters
        ----------
        path: str
            path to folcder
        """
        self.path = Path(path)

    def get_available_name(self, file_info):
        """Get a path to save the given file to. Add numbers to filename to avoid clashes

        Parameters
        ----------
        file_info: FileInfo

        Returns
        -------
        Path
            full path including name where this file info might be saved

        """
        return Path(self.path) / file_info.file_name()


class JobFolder(SafeFolder):
    """ A folder storing job files that will keep files for jobs separated

    """

    def __init__(self, path: str):
        """ A folder storing job files.

        Parameters
        ----------
        path: str
            full path to this folder
        """
        self.path = Path(path)

    def get_available_name(self, file_info):
        """

        Parameters
        ----------
        file_info: FileInfo

        Returns
        -------
        str
            full path including name where this file info might be saved

        """
        folder = self.path / str(file_info.job.id)
        return folder / file_info.file_name()

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
        dir_names = [x.name for x in self.path.iterdir() if x.is_dir()]
        job_ids = []
        for dir_name in dir_names:
            try:
                job_ids.append(int(dir_name))
            except ValueError:
                next
        return job_ids

    def get_files(self, job_id: int):
        """ get paths to all files belonging to the given job

        Returns
        -------
        List<JobFile>
            list with each file belonging to the given job

        Raises
        ------
        FileNotFoundError
            when given job id does not exist in this folder

        """
        job_path = self.path / str(job_id)
        if not job_path.exists():
            raise FileNotFoundError(f"Folder {job_path} for job '{job_id}' could not be found")
        return [JobFile(job_id=job_id, path=x) for x in job_path.iterdir() if x.is_file()]


class IDISServer:
    """The actual computer of VM that this instance of IDIS runs on

    """

    def __init__(
        self, pre_fetching_path, CTP_input_path, CTP_output_path, quarantine_path
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


class WadoServer(Storage):
    """A wado server and credentials

    """

    name = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="Short description of this server, max 1024 characters.",
    )

    hostname = models.CharField(
        max_length=128, help_text="Hostname or IP of WADO server"
    )
    username = models.CharField(max_length=128, help_text="Connect with this user name")
    password = EncryptedCharField(
        max_length=128, help_text="Connect with this password"
    )
    port = models.IntegerField(help_text="Port to use for connecting")

    def download_file_to(self, file_info, folder):
        """Get file described in file_info

        Parameters
        ----------
        file_info: WADOFile
            information to download a single file from WADO
        folder: Folder

        Returns
        -------
        JobFile
            The file

        """
        # create wado connection
        # Download to
        pass

    def send_file(self, job_file, location):
        """Send the given file to the destination

        Parameters
        ----------
        job_file: JobFile
            send this file

        location: Location
            To this destination

        """
        raise NotImplementedError("No files can be sent via WADO")


class NetworkShare(Storage):
    """A shared network resource

    """

    hostname = models.CharField(
        max_length=256, help_text="hostname or ip of the server computer"
    )
    sharename = models.CharField(max_length=256, help_text="name of the share")
    username = models.CharField(
        max_length=128,
        default=None,
        blank=True,
        help_text="Optional. Connect using this user name",
    )
    password = EncryptedCharField(
        max_length=128,
        default=None,
        blank=True,
        help_text="Optional. Connect with this password",
    )

    def __str__(self):
        return self.path

    @property
    def path(self):
        """Full path to this share

        Returns
        -------
        str full path to this share

        """
        sep = os.path.sep
        return f"{sep}{sep}{self.hostname}{self.sharename}{sep}"

    def download_file_to(self, file_info, folder):
        """Get file described in file_info and put it in folder

        Parameters
        ----------
        file_info: FileOnDisk
            information to download a single file from WADO
        folder: SafeFolder
            path to download to

        Returns
        -------
        JobFile
            The file

        """
        source_path = file_info.path
        destination_path = folder.get_available_name(file_info)
        os.makedirs(destination_path.parent, exist_ok=True)
        copyfile(source_path, destination_path)


class FileOnDisk(FileInfo):
    """Information on a single file coming from a share somewhere"""

    path = models.CharField(
        max_length=1024, default="", help_text="Full path of this file"
    )

    source = models.ForeignKey(
        NetworkShare,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Where this data is coming from",
    )

    def file_name(self):
        """Returns a the filename under which this file can be saved

        Returns
        -------
        str:
            filename for this file.
        """
        return Path(self.path).name


class WADOFile(FileInfo):
    """Information on a single file coming from a WADO source"""

    source = models.ForeignKey(
        WadoServer,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Where this data is coming from",
    )

    study_uid = models.CharField(
        max_length=512, default="", help_text="UID of the study this file belongs to"
    )

    object_uid = models.CharField(
        max_length=512, default="", help_text="Object Unique Identifier for this file"
    )

    def file_name(self):
        """Returns a the filename under which this file can be saved

        Returns
        -------
        str:
            filename for this file.
        """
        return self.object_uid


class Location(models.Model):
    """An unambiguous, fully specified location that contains files.

    Where a destination is general, like 'this share', or 'that S3 account', a location is unambiguous, like
    'this folder on this share' or 'this bucket on this s3 account'
    """

    class Meta:
        abstract = True

    storage = models.ForeignKey(
        Storage,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The storage that this location is on",
    )

    def send_file(self, file):
        """Send the given file to this location

        Parameters
        ----------
        file: JobFile
            file to send
        Returns
        -------

        """
        raise (
            NotImplementedError("This is an abstract base class. Call a child class")
        )

    def get_all_files(self):
        """Get all paths to the files at this location

        Returns
        -------
        List<str>
            list of full paths

        """
        pass


class Folder(Location):
    """A folder on a share"""

    storage = models.ForeignKey(
        NetworkShare,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The share that this location is on",
    )

    relative_path = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="The path to this folder without hostname or sharename",
    )

    def send_file(self, file):
        """Send the given file to this location

        Parameters
        ----------
        file: JobFile
            file to send
        Returns
        -------

        """
        self.share.send_file(file, self.relative_path)

    def get_all_files(self):
        """Get all paths to the files at this location

        Returns
        -------
        List<str>
            list of full paths

        """
        pass
