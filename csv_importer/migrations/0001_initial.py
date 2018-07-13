# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-13 14:47
from __future__ import unicode_literals

import csv_importer.models.csv_import_file
import csv_importer.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_subscription', '0013_subscription_test_subscription'),
        ('gatheros_event', '0022_event_allow_importing'),
    ]

    operations = [
        migrations.CreateModel(
            name='CSVImportFile',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('csv_file', models.FileField(upload_to=csv_importer.models.csv_import_file.get_file_path, validators=[csv_importer.validators.validate_csv_only_file])),
                ('error_csv_file', models.FileField(upload_to=csv_importer.models.csv_import_file.get_err_file_path, validators=[csv_importer.validators.validate_csv_only_file])),
                ('created', models.DateTimeField(editable=False, verbose_name='criado em')),
                ('modified', models.DateTimeField(verbose_name='modificado em')),
                ('separator', models.CharField(default='"', max_length=1, verbose_name='separador')),
                ('delimiter', models.CharField(default=',', max_length=1, verbose_name='delimitador')),
                ('encoding', models.CharField(choices=[('utf-8', 'UTF-8'), ('iso-8859-1', 'ISO 8859-1(Latim)')], default='utf-8', max_length=10, verbose_name='tipo de codificação')),
                ('processed', models.BooleanField(default=False, verbose_name='arquivo já foi processado')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='csv_file', to='gatheros_event.Event', verbose_name='evento')),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='csv_file', to='gatheros_subscription.Lot', verbose_name='lot')),
            ],
        ),
    ]
