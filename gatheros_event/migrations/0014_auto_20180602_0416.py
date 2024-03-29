# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-02 04:16
from __future__ import unicode_literals

from django.db import migrations, models
import gatheros_event.models.event
import gatheros_event.models.info
import stdimage.models
import stdimage.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gatheros_event', '0013_auto_20180521_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='rsvp_type',
            field=models.CharField(blank=True, choices=[('rsvp-disabled', 'Aberto'), ('rsvp-open', 'Convidados associados terão um lote especial.'), ('rsvp-restricted', 'Somente associados poderão se inscrever.')], default='rsvp-disabled', help_text='Se há associados vinculados à organização, o evento poderá exibir um lote especial para eles, com um valor especial.', max_length=20, null=True, verbose_name='Distribuição de Público'),
        ),
        migrations.AlterField(
            model_name='event',
            name='image_main',
            field=stdimage.models.StdImageField(blank=True, help_text="Imagem única da descrição do evento: 480px x 638px. <a  target='_blank' href='http://via.placeholder.com/480x638'>Exemplo </a>", null=True, upload_to=gatheros_event.models.event.get_image_path, validators=[stdimage.validators.MinSizeValidator(480, 638), stdimage.validators.MaxSizeValidator(1400, 1400)], verbose_name='imagem principal'),
        ),
        migrations.AlterField(
            model_name='info',
            name='image_main',
            field=stdimage.models.StdImageField(blank=True, help_text="Banner do evento, mínimo de: 480px largura x 640px altura.(png/jpg) <a target='_blank' href='http://via.placeholder.com/480x638'>Exemplo </a>", null=True, upload_to=gatheros_event.models.info.get_image_path, validators=[stdimage.validators.MinSizeValidator(480, 638), stdimage.validators.MaxSizeValidator(1400, 1861)], verbose_name='imagem principal'),
        ),
    ]
