import logging
from io import BytesIO

from PIL import Image
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.management import BaseCommand
from userena.models import UserenaSignup

logger = logging.getLogger(__name__)


def get_temporary_image():
    io = BytesIO()
    size = (200, 200)
    color = (255, 0, 0)
    image = Image.new("RGB", size, color)
    image.save(io, format="JPEG")
    image_file = InMemoryUploadedFile(
        io, None, "foo.jpg", "jpeg", image.size, None
    )
    image_file.seek(0)
    return image_file


class Command(BaseCommand):
    users = None

    def handle(self, *args, **options):
        """Creates test users and objects."""
        if not settings.DEBUG:
            raise RuntimeError(
                "Skipping this command, server is not in DEBUG mode."
            )

        # Set the default domain that is used in RequestFactory
        site = Site.objects.get(pk=settings.SITE_ID)
        if site.domain == "idis.localhost":
            # Already initialised
            return

        site.domain = "idis.localhost"
        site.name = "IDIS"
        site.save()

        default_users = ["demo", "user", "admin"]
        self.users = self._create_users(usernames=default_users)
        self._set_user_permissions()

    @staticmethod
    def _create_users(usernames):
        users = {}

        for username in usernames:
            print(f'adding user "{username}"')
            users[username] = UserenaSignup.objects.create_user(
                username=username,
                email=f"{username}@example.com",
                password=username,
                active=True,
            )

        return users

    def _set_user_permissions(self):
        self.users["admin"].is_staff = True
        self.users["admin"].is_superuser = True
        self.users["admin"].save()
