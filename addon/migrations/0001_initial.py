# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-10 16:08
from __future__ import unicode_literals

import base.models
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import gatheros_event.models.mixins.gatheros_model_mixin


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_event', '0013_auto_20180510_1608'),
        ('gatheros_subscription', '0011_auto_20180510_1608'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionalProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
            ],
            options={
                'verbose_name': 'tipo de opcional de produto',
                'verbose_name_plural': 'tipos de opcional de produto',
                'ordering': ('name',),
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OptionalServiceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
            ],
            options={
                'verbose_name': 'tipo de opcional de serviço',
                'verbose_name_plural': 'tipos de opcional de serviço',
                'ordering': ('name',),
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_end_sub', models.DateTimeField(help_text='Data e hora limite para se aceitar inscrições para este opcional.', verbose_name='Inscrição - data/hora limite')),
                ('published', models.BooleanField(default=True, verbose_name='publicado')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modificado')),
                ('created_by', models.CharField(blank=True, max_length=255, verbose_name='criado por')),
                ('modified_by', models.CharField(blank=True, max_length=255, verbose_name='modificado por')),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=10, verbose_name='preço')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('quantity', models.PositiveIntegerField(blank=True, help_text='Limite máximo permitido.', null=True, verbose_name='quantidade')),
                ('release_days', models.PositiveIntegerField(blank=True, default=7, help_text='Número de dias em que serão liberadas as vagas de opcionais caso a inscrição esteja como pendente.', null=True, verbose_name='dias de liberação de opcionais')),
                ('name', models.CharField(max_length=255, verbose_name='nome do produto')),
                ('lot_category', models.ForeignKey(help_text='Para qual categoria de participante se destina.', on_delete=django.db.models.deletion.PROTECT, related_name='product_optionals', to='gatheros_subscription.LotCategory', verbose_name='categoria')),
                ('optional_type', models.ForeignKey(help_text='Exemplo: palestra, workshop, curso, hospedagem', on_delete=django.db.models.deletion.PROTECT, related_name='product_type_optionals', to='addon.OptionalProductType', verbose_name='tipo')),
            ],
            options={
                'verbose_name': 'opcional de produto',
                'verbose_name_plural': 'opcionais de produto',
                'ordering': ('name',),
                'abstract': False,
            },
            bases=(gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin, base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_end_sub', models.DateTimeField(help_text='Data e hora limite para se aceitar inscrições para este opcional.', verbose_name='Inscrição - data/hora limite')),
                ('published', models.BooleanField(default=True, verbose_name='publicado')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='modificado')),
                ('created_by', models.CharField(blank=True, max_length=255, verbose_name='criado por')),
                ('modified_by', models.CharField(blank=True, max_length=255, verbose_name='modificado por')),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=10, verbose_name='preço')),
                ('description', models.TextField(blank=True, null=True, verbose_name='descrição')),
                ('quantity', models.PositiveIntegerField(blank=True, help_text='Limite máximo permitido.', null=True, verbose_name='quantidade')),
                ('release_days', models.PositiveIntegerField(blank=True, default=7, help_text='Número de dias em que serão liberadas as vagas de opcionais caso a inscrição esteja como pendente.', null=True, verbose_name='dias de liberação de opcionais')),
                ('name', models.CharField(max_length=255, verbose_name='nome da atividade')),
                ('schedule_start', models.DateTimeField(help_text='Data e hora inicial da programação no dia do evento.', verbose_name='programação - início')),
                ('schedule_end', models.DateTimeField(help_text='Data e hora final da programação no dia do evento.', verbose_name='programação - fim')),
                ('place', models.CharField(blank=True, help_text='Local onde a atividade irá acontecer no dia do evento.', max_length=255, null=True, verbose_name='local')),
                ('restrict_unique', models.BooleanField(default=False, help_text='Se marcado, os participantes inscritos nesta atividade não poderão se inscrever em outras atividades que estejam em conflito de horário com esta.', verbose_name='Restringir horário')),
                ('lot_category', models.ForeignKey(help_text='Para qual categoria de participante se destina.', on_delete=django.db.models.deletion.PROTECT, related_name='service_optionals', to='gatheros_subscription.LotCategory', verbose_name='categoria')),
                ('optional_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='service_type_optionals', to='addon.OptionalServiceType', verbose_name='tipo')),
            ],
            options={
                'verbose_name': 'opcional de serviço',
                'verbose_name_plural': 'opcionais de serviço',
                'ordering': ('name',),
                'abstract': False,
            },
            bases=(gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin, base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubscriptionProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data de criação')),
                ('optional_price', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('optional_liquid_price', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('optional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_products', to='addon.Product', verbose_name='opcional de produto')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptionproduct', to='gatheros_subscription.Subscription', verbose_name='inscrição')),
            ],
            options={
                'verbose_name': 'inscrição de opcional de produto',
                'verbose_name_plural': 'inscrições de opcional de produto',
                'ordering': ('subscription__event',),
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SubscriptionService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data de criação')),
                ('optional_price', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('optional_liquid_price', models.DecimalField(blank=True, decimal_places=2, max_digits=11, null=True)),
                ('optional', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='subscription_services', to='addon.Service', verbose_name='opcional de serviço')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptionservice', to='gatheros_subscription.Subscription', verbose_name='inscrição')),
            ],
            options={
                'verbose_name': 'inscrição de opcional de serviço',
                'verbose_name_plural': 'inscrições de opcional de serviço',
                'ordering': ('subscription__event',),
                'abstract': False,
            },
            bases=(base.models.EntityMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('limit', models.PositiveIntegerField(blank=True, help_text='Limitar número de inscrições de um mesmo participante em um mesmo tema.', null=True, verbose_name='limitar quantidade')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='themes', to='gatheros_event.Event', verbose_name='eventos')),
            ],
            options={
                'verbose_name': 'grupo',
                'verbose_name_plural': 'grupos',
                'ordering': ('event', 'name'),
            },
            bases=(gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin, base.models.EntityMixin, models.Model),
        ),
        migrations.AddField(
            model_name='service',
            name='theme',
            field=models.ForeignKey(help_text='Agrupar atividades por área temática.', on_delete=django.db.models.deletion.PROTECT, related_name='services', to='addon.Theme', verbose_name='grupo temático'),
        ),
    ]
