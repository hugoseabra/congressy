# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-29 16:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
        ('gatheros_event', '0010_event_congressy_percent'),
        ('gatheros_subscription', '0008_subscription_congressy_percent'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventSurvey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='surveys', to='gatheros_event.Event', verbose_name='evento')),
                ('survey', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='event', to='survey.Survey', verbose_name='formulario')),
            ],
        ),
        migrations.AddField(
            model_name='subscription',
            name='author',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='subscription', to='survey.Author', verbose_name='autor de resposta'),
        ),
        migrations.AddField(
            model_name='lot',
            name='event_survey',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='lots', to='gatheros_subscription.EventSurvey', verbose_name='formulario'),
        ),
    ]