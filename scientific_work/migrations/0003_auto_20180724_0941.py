# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-24 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scientific_work', '0002_auto_20180528_1427'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='areacategory',
            options={'verbose_name': 'Categoria de Área', 'verbose_name_plural': 'Categorias de Àreas'},
        ),
        migrations.AlterModelOptions(
            name='work',
            options={'verbose_name': 'Trabalho', 'verbose_name_plural': 'Trabalhos'},
        ),
        migrations.AlterModelOptions(
            name='workconfig',
            options={'verbose_name': 'Configuração de Submissão', 'verbose_name_plural': 'Configurações de Submissões'},
        ),
        migrations.AlterField(
            model_name='areacategory',
            name='name',
            field=models.CharField(max_length=255, verbose_name='área temática'),
        ),
    ]
