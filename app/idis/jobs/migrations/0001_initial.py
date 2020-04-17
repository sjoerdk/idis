# Generated by Django 2.1.5 on 2019-02-04 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FileBatch",
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
                    "description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Short description of this batch, max 1024 characters.",
                        max_length=1024,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FileOnDisk",
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
                    "path",
                    models.CharField(
                        default="",
                        help_text="Full path of this file",
                        max_length=1024,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Folder",
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
                    "relative_path",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The path to this folder without hostname, sharename or drive letter",
                        max_length=1024,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Job",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("modified", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("CANCELLED", "Cancelled"),
                            ("PENDING", "Pending"),
                            ("DOWNLOADING", "Downloading"),
                            ("PROCESSING", "Processing"),
                            ("ERROR", "Error"),
                            ("DONE", "Done"),
                        ],
                        default="PENDING",
                        max_length=32,
                    ),
                ),
                (
                    "error",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Error message, if any",
                        max_length=1024,
                    ),
                ),
                (
                    "files_downloaded",
                    models.IntegerField(blank=True, default=0),
                ),
                (
                    "files_processed",
                    models.IntegerField(blank=True, default=0),
                ),
                (
                    "files_quarantined",
                    models.IntegerField(blank=True, default=0),
                ),
                (
                    "number_of_retries",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        help_text="Number of times processing has been retried",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Optional text to describe this job",
                        max_length=1024,
                    ),
                ),
                (
                    "priority",
                    models.IntegerField(
                        blank=True,
                        default=10,
                        help_text="Higher values means higher priority for processing this job",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NetworkShare",
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
                    "hostname",
                    models.CharField(
                        help_text="hostname or ip of the server computer",
                        max_length=256,
                    ),
                ),
                (
                    "sharename",
                    models.CharField(
                        help_text="name of the share", max_length=256
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="Optional. Connect using this user name",
                        max_length=128,
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        blank=True,
                        default=None,
                        help_text="Optional. Connect with this password",
                        max_length=128,
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="Profile",
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
                    "title",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Short title for this profile",
                        max_length=64,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Short description of this profile, max 1024 characters.",
                        max_length=1024,
                    ),
                ),
                (
                    "Basic",
                    models.BooleanField(
                        default=True,
                        help_text="Basic confidentiality profile. DICOM standard anonymisation",
                    ),
                ),
                (
                    "CleanPixelData",
                    models.BooleanField(
                        default=True,
                        help_text="Try to remove any burned in annotations",
                    ),
                ),
                (
                    "CleanVisualFeatures",
                    models.BooleanField(
                        default=True,
                        help_text="Try to remove or scramble face if this is present in the data ",
                    ),
                ),
                (
                    "CleanGraphics",
                    models.BooleanField(
                        default=True,
                        help_text="Remove graphics, text annotations or overlays. Does not include structured reports",
                    ),
                ),
                (
                    "CleanStructuredContent",
                    models.BooleanField(
                        default=True,
                        help_text="Clean information encoded in SR Content Items or Acquisition Context or Specimen Preparation Sequence Items ",
                    ),
                ),
                (
                    "CleanDescriptors",
                    models.BooleanField(
                        default=True,
                        help_text="Clean free text fields like study description",
                    ),
                ),
                (
                    "RetainFullDates",
                    models.BooleanField(
                        default=True,
                        help_text="Keep date and time information",
                    ),
                ),
                (
                    "RetainModifiedDates",
                    models.BooleanField(
                        default=True,
                        help_text="Add a certain increment to date and time information",
                    ),
                ),
                (
                    "RetainPatientCharacteristics",
                    models.BooleanField(
                        default=True,
                        help_text="Keep information like age, sex, height and weight",
                    ),
                ),
                (
                    "RetainDeviceIdentity",
                    models.BooleanField(
                        default=True,
                        help_text="Keep information about the device the scan was made on",
                    ),
                ),
                (
                    "RetainUIDs",
                    models.BooleanField(
                        default=True,
                        help_text="Keep IDs such as study UID, patient ID etc.",
                    ),
                ),
                (
                    "RetainSafePrivate",
                    models.BooleanField(
                        default=True,
                        help_text="Keep private tags that are explicitly marked as not containing any patient information",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="WADOFile",
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
                    "study_uid",
                    models.CharField(
                        default="",
                        help_text="UID of the study this file belongs to",
                        max_length=512,
                    ),
                ),
                (
                    "object_uid",
                    models.CharField(
                        default="",
                        help_text="Object Unique Identifier for this file",
                        max_length=512,
                    ),
                ),
                (
                    "batch",
                    models.ForeignKey(
                        blank=True,
                        help_text="Optional collection of files that this file belongs to",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="jobs.FileBatch",
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        help_text="The job this file is associated with",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="jobs.Job",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.CreateModel(
            name="WadoServer",
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
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Short description of this server, max 1024 characters.",
                        max_length=1024,
                    ),
                ),
                (
                    "hostname",
                    models.CharField(
                        help_text="Hostname or IP of WADO server",
                        max_length=128,
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Connect with this user name", max_length=128
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        help_text="Connect with this password", max_length=128
                    ),
                ),
                (
                    "port",
                    models.IntegerField(
                        help_text="Port to use for connecting"
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
        migrations.AddField(
            model_name="wadofile",
            name="source",
            field=models.ForeignKey(
                help_text="Where this data is coming from",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="jobs.WadoServer",
            ),
        ),
    ]
