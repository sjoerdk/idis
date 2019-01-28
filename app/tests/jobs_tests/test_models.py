import pytest

from tests.factories import WadoServerFactory, FileOnDiskFactory
from idis.jobs.models import WadoServer, FileOnDisk


@pytest.mark.django_db
def test_encrypted_char_field():
    """Check the saving encrypted password """
    source = WadoServerFactory(name='a_source', password='a_plain_password')
    source.save()

    # retrieve the object from database again, password should be the same
    source_from_db = WadoServer.objects.filter(name='a_source').get()
    assert source_from_db.password == 'a_plain_password'


@pytest.mark.django_db
def test_retrieve_file_from_disk():
    file_info: FileOnDisk = FileOnDiskFactory(path="/a_folder/a_file.dcm")

    test = 1
    file = file_info.get_file()
