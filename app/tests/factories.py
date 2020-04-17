import factory

from django.conf import settings
from idis.jobs.models import WadoServer, FileOnDisk, NetworkShare, Job, Profile


class WadoServerFactory(factory.DjangoModelFactory):
    class Meta:
        model = WadoServer

    name = factory.Sequence(lambda n: f"Wado Source {n:02}")
    hostname = f"http:\\\\{name}"
    username = "testuser"
    password = "password"
    port = 5000


class NetworkShareFactory(factory.DjangoModelFactory):
    class Meta:
        model = NetworkShare

    hostname = factory.Sequence(lambda n: f"http:\\\\hostname{n:02}")
    sharename = "share"
    username = "testuser"
    password = "testpassword"


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL


class ProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = Profile

    title = factory.Sequence(lambda n: f"test profile {n:02}")


class JobFactory(factory.DjangoModelFactory):
    class Meta:
        model = Job

    creator = factory.SubFactory(UserFactory)
    profile = factory.SubFactory(ProfileFactory)
    description = factory.Sequence(lambda n: f"Test job number {n:05}")


class FileOnDiskFactory(factory.DjangoModelFactory):
    class Meta:
        model = FileOnDisk

    path = "/testpath/a_file.dcm"
    source = factory.SubFactory(NetworkShareFactory)
    job = factory.SubFactory(JobFactory)
    batch = None
