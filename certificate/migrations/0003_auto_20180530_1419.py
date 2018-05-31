# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-30 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0002_certificate_background_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='date_content',
            field=models.TextField(blank=True, help_text='Texto de data do certificado.', null=True, verbose_name='texto'),
        ),
        migrations.AlterField(
            model_name='certificate',
            name='text_content',
            field=models.TextField(default='Certificamos que {{NOME}} participou do evento {{EVENTO}}', help_text='Texto principal do certificado.', verbose_name='texto'),
        ),
    ]
