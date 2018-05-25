# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-25 10:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import gatheros_event.models.mixins.gatheros_model_mixin


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0014_auto_20180525_1051'),
        ('gatheros_subscription', '0009_auto_20180329_1611'),
    ]

    operations = [
        migrations.CreateModel(
            name='LotCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='nome')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lot_categories', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name': 'Categoria de Lote',
                'verbose_name_plural': 'Categorias de Lote',
                'ordering': ['name'],
            },
            bases=(models.Model, gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin),
        ),
        migrations.AddField(
            model_name='lot',
            name='active',
            field=models.BooleanField(default=True, verbose_name='ativo'),
        ),
        migrations.AddField(
            model_name='lot',
            name='rsvp_restrict',
            field=models.BooleanField(default=False, help_text='Somente associados podem se inscrever neste lote.', verbose_name='restrito a associados'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='completed',
            field=models.BooleanField(default=False, editable=False, help_text='Inscrições que passaram por todo o fluxo de inscrições.', verbose_name='completa'),
        ),
        migrations.AlterUniqueTogether(
            name='lot',
            unique_together=set([]),
        ),
        migrations.AddField(
            model_name='lot',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='lots', to='gatheros_subscription.LotCategory', verbose_name='categoria'),
        ),
    ]
