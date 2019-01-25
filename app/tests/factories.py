import factory

from idis.jobs.models import WadoServer


class WadoSourceFactory(factory.DjangoModelFactory):
    class Meta:
        model = WadoServer

    name = factory.Sequence(lambda n: f"Wado Source {n:02}")
    hostname = f"http:\\\\{name}"
    username = 'testuser'
    password = 'password'
    port = 5000
