# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-15 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scientific_work', '0002_auto_20180515_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='work',
            name='published',
            field=models.BooleanField(default=False, verbose_name='publicado'),
        ),
    ]
