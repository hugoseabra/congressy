# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-15 16:36
from __future__ import unicode_literals

import certificate.models
from django.db import migrations
import stdimage.models
import stdimage.validators


class Migration(migrations.Migration):

    dependencies = [
        ('certificate', '0004_certificate_only_attending_participantes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='certificate',
            name='background_image',
            field=stdimage.models.StdImageField(blank=True, help_text="Imagem de fundo300 do certificado, mínimo de: 1402px largura x 991px altura.(png/jpg) <a  target='_blank'href='http://via.placeholder.com/1402x991'>Exemplo</a>", null=True, upload_to=certificate.models.get_image_path, validators=[stdimage.validators.MinSizeValidator(1402, 991)], verbose_name='imagem de fundo do certificado do evento'),
        ),
    ]
