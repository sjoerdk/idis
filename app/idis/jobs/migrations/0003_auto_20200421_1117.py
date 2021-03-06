# Generated by Django 3.0.5 on 2020-04-21 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobs", "0002_auto_20190204_1411"),
    ]

    operations = [
        migrations.AlterField(
            model_name="folder",
            name="relative_path",
            field=models.CharField(
                blank=True,
                default="",
                help_text="The path to this folder without hostname or sharename",
                max_length=1024,
            ),
        ),
    ]
