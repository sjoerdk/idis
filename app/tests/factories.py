import factory

from factory.django import DjangoModelFactory
from django.conf import settings
from idis.jobs.models import WadoServer, FileOnDisk, NetworkShare, Job, Profile
from idis.pipeline.models import Stream


UNBEATABLE_TEST_PASSWORD = "testpasswd"


class WadoServerFactory(DjangoModelFactory):
    class Meta:
        model = WadoServer

    name = factory.Sequence(lambda n: f"Wado Source {n:02}")
    hostname = f"http:\\\\{name}"
    username = "testuser"
    password = "password"
    port = 5000


class NetworkShareFactory(DjangoModelFactory):
    class Meta:
        model = NetworkShare

    hostname = factory.Sequence(lambda n: f"http:\\\\hostname{n:02}")
    sharename = "share"
    username = "testuser"
    password = "testpassword"


class UserFactory(DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: f"test_user_{n:04}")
    email = factory.LazyAttribute(lambda u: "%s@test.com" % u.username)
    password = factory.PostGenerationMethodCall(
        "set_password", UNBEATABLE_TEST_PASSWORD
    )
    is_active = True
    is_staff = False
    is_superuser = False


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    title = factory.Sequence(lambda n: f"test profile {n:02}")


class JobFactory(DjangoModelFactory):
    class Meta:
        model = Job

    creator = factory.SubFactory(UserFactory)
    profile = factory.SubFactory(ProfileFactory)
    description = factory.Sequence(lambda n: f"Test job number {n:05}")


class FileOnDiskFactory(DjangoModelFactory):
    class Meta:
        model = FileOnDisk

    path = "/testpath/a_file.dcm"
    source = factory.SubFactory(NetworkShareFactory)
    job = factory.SubFactory(JobFactory)
    batch = None


class StreamFactory(DjangoModelFactory):
    class Meta:
        model = Stream

    name = factory.Sequence(lambda n: f"stream_{n}")
    output_folder = factory.Sequence(
        lambda n: r"\\someshare\ouput_stream_" + str(n)
    )
    idis_profile = factory.SubFactory(ProfileFactory)
    pims_key = "123"
    contact = factory.SubFactory(UserFactory)
