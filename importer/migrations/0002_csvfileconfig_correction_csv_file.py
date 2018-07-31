# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-31 17:55
from __future__ import unicode_literals

from django.db import migrations, models
import importer.models.csv_file_config
import importer.models.storage
import importer.validators


class Migration(migrations.Migration):

    dependencies = [
        ('importer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='csvfileconfig',
            name='correction_csv_file',
            field=models.FileField(null=True, storage=importer.models.storage.OverwriteStorage(), upload_to=importer.models.csv_file_config.get_correction_file_path, validators=[importer.validators.validate_csv_only_file]),
        ),
    ]
