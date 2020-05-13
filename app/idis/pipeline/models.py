from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
# IncomingFile
# Person
# PushStudyCallbackException
# Stage
# Stream
# Study


class Stream(models.Model):
    """A single route that incoming data goes through.
    Determines anonymization type and destination.

    Notes
    -----
    Responsibilities: A stream is a passive data structure. It should not know about
    where the data it contains is exactly. This is the responsibility of each Stage
    that a stream is in

    """

    name = models.CharField(
        blank=False, null=True, default=None, max_length=265
    )
    output_folder = models.CharField(
        blank=False, null=True, default=None, max_length=512
    )
    idis_profile = models.ForeignKey(
        to="jobs.Profile",
        null=True,
        default=None,
        on_delete=models.SET_DEFAULT,
    )
    pims_key = models.CharField(
        blank=False, null=True, default=None, max_length=128
    )
    contact = models.ForeignKey(
        to=get_user_model(),
        null=True,
        default=None,
        on_delete=models.SET_DEFAULT,
    )

    @property
    def idis_profile_name(self) -> str:
        """IDIS profile as string.  For use as key in IDIS"""
        return str(self.idis_profile.title)
