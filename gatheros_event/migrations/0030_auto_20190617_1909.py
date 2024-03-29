# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-06-17 19:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0029_auto_20190615_1925'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='info',
            name='stream_page_button',
        ),
        migrations.AlterField(
            model_name='info',
            name='stream_page_title',
            field=models.CharField(blank=True, default='Transmissão ao vivo', max_length=80, verbose_name='Título da Página de Vídeo'),
        ),
        migrations.AlterField(
            model_name='info',
            name='stream_youtube_code',
            field=models.CharField(blank=True, help_text='https://www.youtube.com/watch?v=<strong>CÓDIGO</strong>', max_length=15, null=True, verbose_name='Código do Vídeo (Youtube)'),
        ),
    ]
