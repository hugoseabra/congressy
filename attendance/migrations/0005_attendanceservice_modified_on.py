# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-01 13:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0004_auto_20190328_1638'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendanceservice',
            name='modified_on',
            field=models.DateTimeField(auto_now=True, verbose_name='modificado em'),
        ),
    ]