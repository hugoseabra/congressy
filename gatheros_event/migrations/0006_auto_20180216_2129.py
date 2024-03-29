# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-02-16 21:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('gatheros_event', '0005_auto_20180209_1603'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='place',
        ),
        migrations.RemoveField(
            model_name='place',
            name='organization',
        ),
        migrations.AddField(
            model_name='place',
            name='event',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='place', to='gatheros_event.Event',
                verbose_name='evento'),
        ),
        migrations.AddField(
            model_name='place',
            name='show_address',
            field=models.BooleanField(default=False,
                                      help_text='Exibir informações do local evento.',
                                      verbose_name='mostrar endereço'),
        ),
        migrations.AddField(
            model_name='place',
            name='show_location',
            field=models.BooleanField(default=False,
                                      help_text='Exibir mapa do local onde o evento irá acontecer.',
                                      verbose_name='mostrar localização'),
        ),
        migrations.AlterField(
            model_name='place',
            name='city',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING,
                                    to='kanu_locations.City',
                                    verbose_name='cidade'),
        ),
        migrations.AlterField(
            model_name='place',
            name='lat',
            field=models.DecimalField(blank=True, decimal_places=6,
                                      max_digits=15, null=True,
                                      verbose_name='latitude'),
        ),
        migrations.AlterField(
            model_name='place',
            name='long',
            field=models.DecimalField(blank=True, decimal_places=6,
                                      max_digits=15, null=True,
                                      verbose_name='longitude'),
        ),
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True,
                                   verbose_name='nome'),
        ),
    ]
