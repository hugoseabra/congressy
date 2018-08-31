# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-30 18:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_subscription', '0014_subscription_event_count'),
        ('gatheros_event', '0024_auto_20180816_1212'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceCategoryFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'ordering': ['attendance_service'],
                'verbose_name': 'Filtro para lista de Check-In/Out por Categoria de Lote',
            },
        ),
        migrations.CreateModel(
            name='AttendanceService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_services', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Lista de Check-in/out',
                'verbose_name_plural': 'Lista de Check-ins/outs',
            },
        ),
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True, verbose_name='imprimiu a etiqueta em')),
                ('created_by', models.CharField(max_length=255, verbose_name='criado por')),
                ('printed_on', models.DateTimeField(blank=True, null=True, verbose_name='imprimiu a etiqueta em')),
                ('attendance_service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkins', to='attendance.AttendanceService', verbose_name='Lista de Check-in/out')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkins', to='gatheros_subscription.Subscription', verbose_name='Inscrito')),
            ],
            options={
                'ordering': ['created_on'],
                'abstract': False,
                'verbose_name': 'entrada',
                'verbose_name_plural': 'entradas',
            },
        ),
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True, verbose_name='imprimiu a etiqueta em')),
                ('created_by', models.CharField(max_length=255, verbose_name='criado por')),
                ('checkin', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='checkout', to='attendance.Checkin', verbose_name='Check-in')),
            ],
            options={
                'ordering': ['created_on'],
                'abstract': False,
                'verbose_name': 'saída',
                'verbose_name_plural': 'saídas',
            },
        ),
        migrations.AddField(
            model_name='attendancecategoryfilter',
            name='attendance_service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lot_category_filters', to='attendance.AttendanceService', verbose_name='Lista de Check-in/out'),
        ),
        migrations.AddField(
            model_name='attendancecategoryfilter',
            name='lot_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lot_category_filters', to='gatheros_subscription.LotCategory', verbose_name='Categoria'),
        ),
        migrations.AddIndex(
            model_name='checkout',
            index=models.Index(fields=['created_by'], name='attendance__created_a1d65f_idx'),
        ),
        migrations.AddIndex(
            model_name='checkin',
            index=models.Index(fields=['created_by'], name='attendance__created_7c7d84_idx'),
        ),
    ]
