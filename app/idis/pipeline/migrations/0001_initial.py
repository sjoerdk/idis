# Generated by Django 3.0.5 on 2020-04-22 10:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("jobs", "0003_auto_20200421_1117"),
    ]

    operations = [
        migrations.CreateModel(
            name="Stream",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(default=None, max_length=265, null=True),
                ),
                (
                    "output_folder",
                    models.CharField(default=None, max_length=512, null=True),
                ),
                (
                    "pims_key",
                    models.CharField(default=None, max_length=128, null=True),
                ),
                (
                    "contact",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "idis_profile",
                    models.ForeignKey(
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_DEFAULT,
                        to="jobs.Profile",
                    ),
                ),
            ],
        ),
    ]
