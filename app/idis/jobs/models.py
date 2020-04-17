import abc
import os
from pathlib import Path

from django.db import models
from django.conf import settings

from idis.jobs.filehandling import JobFile, SafeFolder, copy_job_file


class Profile(models.Model):
    """Anonymisation profile. Determines how the data is to be anonymised.

    Based on the DICOM standard confidentiality profile
    (http://dicom.nema.org/medical/dicom/current/output/html/part15.html#sect_E.2)

    and the ten application level Confidentiality Options which modify the standard profile

    """

    def __str__(self):
        return f"Profile '{self.title}'"

    title = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Short title for this profile",
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
        default=True,
        help_text="Add a certain increment to date and time information",
    )
    RetainPatientCharacteristics = models.BooleanField(
        default=True,
        help_text="Keep information like age, sex, height and weight",
    )
    RetainDeviceIdentity = models.BooleanField(
        default=True,
        help_text="Keep information about the device the scan was made on",
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
        max_length=1024,
        default="",
        blank=True,
        help_text="Error message, if any",
    )

    files_downloaded = models.IntegerField(default=0, blank=True)
    files_processed = models.IntegerField(default=0, blank=True)
    files_quarantined = models.IntegerField(default=0, blank=True)
    number_of_retries = models.IntegerField(
        default=0,
        blank=True,
        help_text="Number of times processing has been retried",
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
        job_file: idis.jobs.filehandling.JobFile

        """
        raise (
            NotImplementedError(
                "This is an abstract base class. Call a child class"
            )
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
        idis.jobs.filehandling.JobFile
            The file

        """
        raise (
            NotImplementedError(
                "This is an abstract base class. Call a child class"
            )
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
        """Returns a filename under which this file can be saved

        Returns
        -------
        str:
            filename for this file.
        """
        return

    def download(self, to_folder=settings.IDIS_PRE_FETCHING_FOLDER):
        """Download the file indicated by this file info. Return a file object for the downloaded file.

        Parameters
        ----------
        to_folder: SafeFolder, Optional
            Folder to download to. Defaults to 'settings.IDIS_PRE_FETCHING_FOLDER'

        Returns
        -------
        idis.jobs.filehandling.JobFile
            The file that has been downloaded

        Raises
        ------
        FileNotFoundError
            If file cannot be retrieved

        """

        return self.source.download_file_to(file_info=self, folder=to_folder)


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
    username = models.CharField(
        max_length=128, help_text="Connect with this user name"
    )
    password = models.CharField(
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
        idis.jobs.filehandling.JobFile
            The file

        """
        # create wado connection
        # Download to
        pass

    def send_file(self, job_file, location):
        """Send the given file to the destination

        Parameters
        ----------
        job_file: idis.jobs.filehandling.JobFile
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
    password = models.CharField(
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

    def download_file_to(self, file_info: FileInfo, folder: SafeFolder):
        """Get file described in file_info and put it in folder

        Parameters
        ----------
        file_info: FileInfo
            information specifying a single DICOM file
        folder: SafeFolder
            path to download to

        Returns
        -------
        idis.jobs.filehandling.JobFile
            The file

        """

        job_file = JobFile(job_id=file_info.job.id, path=file_info.path)
        copy_job_file(job_file, destination=folder)


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
        """Returns a filename under which this file can be saved

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
        max_length=512,
        default="",
        help_text="UID of the study this file belongs to",
    )

    object_uid = models.CharField(
        max_length=512,
        default="",
        help_text="Object Unique Identifier for this file",
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
            NotImplementedError(
                "This is an abstract base class. Call a child class"
            )
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
