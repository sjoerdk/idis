import factory

from idis.jobs.models import WadoServer, FileOnDisk, NetworkShare


class WadoServerFactory(factory.DjangoModelFactory):
    class Meta:
        model = WadoServer

    name = factory.Sequence(lambda n: f"Wado Source {n:02}")
    hostname = f"http:\\\\{name}"
    username = 'testuser'
    password = 'password'
    port = 5000


class NetworkShareFactory(factory.DjangoModelFactory):
    class Meta:
        model = NetworkShare

    name = factory.Sequence(lambda n: f"Network share {n:02}")
    hostname = f"http:\\\\{name}"
    sharename = 'share'
    username = 'testuser'
    password = 'testpassword'


class FileOnDiskFactory(factory.DjangoModelFactory):
    class Meta:
        model = FileOnDisk

    path = "/testpath/a_file.dcm"
    source = factory.SubFactory(NetworkShareFactory)
