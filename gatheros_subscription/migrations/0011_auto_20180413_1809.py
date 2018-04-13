# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-13 18:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0011_event_rsvp_type'),
        ('gatheros_subscription', '0010_lot_rsvp_restrict'),
    ]

    operations = [
        migrations.CreateModel(
            name='LotCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lot_categories', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name_plural': 'Categorias de Lote',
                'verbose_name': 'Categoria de Lote',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='lot',
            name='category',
            field=models.ForeignKey(blank=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lots', to='gatheros_subscription.LotCategory', verbose_name='categoria'),
        ),
    ]
