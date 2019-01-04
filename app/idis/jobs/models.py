from django.db import models

from django.conf import settings


class Profile(models.Model):
    """Anonymization profile. Determines how the data is to be anonymized.

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
        help_text="Basic confidentiality profile. DICOM standard anonymization",
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


class Job(models.Model):
    """A command to anonymize some data.

    Contains all information to anonymize data. Where is it, how to anonymize, where it should go
    """

    def __str__(self):
        return f"job {self.id}"

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    profile = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)
