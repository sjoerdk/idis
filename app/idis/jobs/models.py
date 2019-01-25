from pathlib import Path

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
        help_text="The files that are processed in this job"
    )


class Destination(models.Model):
    """Something that you can send files to

    """

    class Meta:
        abstract = True

    def send_file(self, job_file):
        """Send the given file to the destination

        Parameters
        ----------
        job_file: JobFile

        """
        raise (
            NotImplementedError("This is an abstract base class. Call a child class")
        )


class Source(models.Model):
    """Contains all information needed to fetch a batch of files

    """

    class Meta:
        abstract = True

    def get_file(self, file_info):
        """Get the file described in file_info from this source

        Parameters
        ----------
        file_info: FileInfo
            information uniquely defining a single file

        Returns
        -------
        InputFiles
            The file

        """
        raise (
            NotImplementedError("This is an abstract base class. Call a child class")
        )


class FileInfo(models.Model):
    """"Describes a single file and how to get it.

    """

    class Meta:
        abstract = True

    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The job this file is associated with",
    )
    source_server = models.ForeignKey(
        Source,
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
    path = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="Location of this file on disk",
    )

    def get_file(self):
        """Return a file object for this file. Retrieve from external source if needed.

        Returns
        -------
        JobFile
        """
        path = Path(self.path)
        if path.exists():
            return JobFile(job=self.job, path=path)
        else:
            self.path = self.source_server.get_file(self)
        return File(self.path)


class JobFile:
    """ A file in IDIS. Always belongs to a job """

    def __init__(self, job, path):
        """

        Parameters
        ----------
        job: Job
            The job that this file belongs to
        path: Path
            location of this file on disk
        """

        self.job = job
        self.path = path


class WadoServer(Source):
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

    def get_file(self, file_info):
        """Get file described in file_info

        Parameters
        ----------
        file_info: WADOFile
            information to download a single file from WADO

        Returns
        -------
        JobFile
            The file

        """
        # create wado connection, actually download
        pass


class NetworkShare(Source, Destination):
    """A hardisk or share

    """

    name = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="Short description of this server, max 1024 characters.",
    )

    hostname = models.CharField(max_length=256, help_text="hostname or ip of the server computer")
    sharename = models.CharField(max_length=256, help_text="name of the share")
    username = models.CharField(
        max_length=128,
        default=None,
        blank=True,
        help_text="Connect with this user name",
    )
    password = EncryptedCharField(
        max_length=128, default=None, blank=True, help_text="Connect with this password"
    )

    def get_file(self, file_info):
        """Get file described in file_info

        Parameters
        ----------
        file_info: FileOnDisk
            information to download a single file from WADO

        Returns
        -------
        JobFile
            The file

        """
        # copy file to local
        pass

    def send_file(self, job_file, destination):
        """Send the given file to the destination

        Parameters
        ----------
        job_file: JobFile
            send this file

        destination: JobDestination
            To this destination

        """


class WADOFile(FileInfo):
    """A single file coming from a WADO source"""

    source_server = models.ForeignKey(
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


class FileOnDisk(FileInfo):
    """A single file coming from a share somewhere """

    path = models.CharField(
        max_length=1024, default="", help_text="Full path of this file"
    )

    source_server = models.ForeignKey(
        NetworkShare,
        on_delete=models.SET_NULL,
        null=True,
        help_text="Where this data is coming from",
        )


class Location(models.Model):
    """A fully specified location to send files"""

    class Meta:
        abstract = True

    destination = models.ForeignKey(
        Destination,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The server that this location is on",
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


class Folder(Location):
    """A folder on a share"""

    destination = models.ForeignKey(
        NetworkShare,
        on_delete=models.SET_NULL,
        null=True,
        help_text="The share that this folder is on",
        )

    path = models.CharField(
        max_length=1024,
        default="",
        blank=True,
        help_text="The path to this folder, without hostname and sharename",
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
        # copy this file!
        pass
