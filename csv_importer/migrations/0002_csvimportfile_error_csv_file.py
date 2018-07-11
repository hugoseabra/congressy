# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-11 07:06
from __future__ import unicode_literals

import csv_importer.models.csv_import_file
import csv_importer.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csv_importer', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='csvimportfile',
            name='error_csv_file',
            field=models.FileField(default='err_file', upload_to=csv_importer.models.csv_import_file.get_err_file_path, validators=[csv_importer.validators.validate_csv_only_file]),
            preserve_default=False,
        ),
    ]
