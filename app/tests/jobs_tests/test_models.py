import pytest

from tests.factories import WadoSourceFactory
from idis.jobs.models import WadoServer


@pytest.mark.django_db
def test_encrypted_char_field():
    """Check the saving encrypted password """
    source = WadoSourceFactory(name='a_source', password='a_plain_password')
    source.save()

    # retrieve the object from database again, password should be the same
    source_from_db = WadoServer.objects.filter(name='a_source').get()
    assert source_from_db.password == 'a_plain_password'
