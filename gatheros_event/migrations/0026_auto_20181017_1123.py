# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-17 11:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0025_auto_20180918_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='address_international',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='endereço'),
        ),
        migrations.AddField(
            model_name='person',
            name='international_doc_type',
            field=models.CharField(blank=True, choices=[('ID', 'ID'), ('Passport', 'Passaport')], default='Passport', help_text='Informe o tipo de documento.', max_length=11, verbose_name='tipo de documento'),
        ),
        migrations.AlterField(
            model_name='person',
            name='international_doc',
            field=models.CharField(blank=True, help_text='Número de documento utilizado fora do Brasil.', max_length=11, null=True, verbose_name='Núm. Documento'),
        ),
    ]
