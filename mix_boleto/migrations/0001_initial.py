# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-08 18:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MixBoleto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mix_boleto_id', models.PositiveSmallIntegerField(db_index=True, verbose_name='ID do Boleto (MixEvents)')),
                ('cgsy_subscription_id', models.UUIDField(db_index=True, verbose_name='UUID de Inscrição (Congressy)')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='valor')),
                ('installments', models.PositiveSmallIntegerField(default=1, verbose_name='parcelas')),
                ('installment_part', models.PositiveSmallIntegerField(default=1, verbose_name='número da parcela')),
                ('cancelled', models.BooleanField(default=False, verbose_name='Cancelado')),
                ('paid', models.BooleanField(default=False, verbose_name='Pago')),
                ('mix_created', models.DateTimeField(verbose_name='Data de criação (MixEvents)')),
                ('mix_updated', models.DateTimeField(verbose_name='Data de atualização (MixEvents)')),
            ],
            options={
                'verbose_name_plural': 'Mix Boletos',
                'verbose_name': 'Mix Boleto',
            },
        ),
        migrations.CreateModel(
            name='SyncBoleto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cgsy_transaction_id', models.UUIDField(db_index=True, verbose_name='UUID de Transação (Congressy)')),
                ('mix_boleto', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mix_boleto.MixBoleto', verbose_name='ID MixBoleto')),
            ],
            options={
                'verbose_name_plural': 'Sync Boletos',
                'verbose_name': 'Sync Boleto',
            },
        ),
        migrations.CreateModel(
            name='SyncCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mix_category_id', models.PositiveSmallIntegerField(db_index=True, verbose_name='ID da Categoria (MixEvents)')),
                ('cgsy_category_id', models.PositiveSmallIntegerField(db_index=True, verbose_name='ID da Categoria (Congressy)')),
                ('mix_created', models.DateTimeField(verbose_name='Data de criação (MixEvents)')),
                ('mix_updated', models.DateTimeField(verbose_name='Data de atualização (MixEvents)')),
            ],
            options={
                'verbose_name_plural': 'Sync Categorias',
                'verbose_name': 'Sync Categoria',
            },
        ),
        migrations.CreateModel(
            name='SyncResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(db_index=True, help_text='Nome único a ser utilizado para busca de credenciais.', max_length=15, unique=True, verbose_name='nome único')),
                ('host', models.TextField(verbose_name='DB Host')),
                ('user', models.CharField(max_length=80, verbose_name='DB User')),
                ('password', models.CharField(max_length=80, verbose_name='DB Pass')),
                ('db_name', models.CharField(max_length=80, verbose_name='DB Name')),
            ],
            options={
                'verbose_name_plural': 'Conexões DB (MixEvents)',
                'verbose_name': 'Conexão DB (MixEvents)',
            },
        ),
        migrations.CreateModel(
            name='SyncSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mix_subscription_id', models.SmallIntegerField(db_index=True, verbose_name='ID de Inscrição (MixEvents)')),
                ('cgsy_subscription_id', models.UUIDField(db_index=True, verbose_name='UUID de Inscrição (Congressy)')),
                ('mix_created', models.DateTimeField(verbose_name='Data de criação (MixEvents)')),
                ('mix_updated', models.DateTimeField(verbose_name='Data de atualização (MixEvents)')),
                ('sync_resource', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mix_boleto.SyncResource', verbose_name='Conexão de DB')),
            ],
            options={
                'verbose_name_plural': 'Sync Inscrições',
                'verbose_name': 'Sync Inscrição',
            },
        ),
        migrations.AddField(
            model_name='synccategory',
            name='sync_resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mix_boleto.SyncResource', verbose_name='Conexão de DB'),
        ),
        migrations.AddField(
            model_name='mixboleto',
            name='sync_resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mix_boleto.SyncResource', verbose_name='Conexão de DB'),
        ),
        migrations.AlterUniqueTogether(
            name='syncsubscription',
            unique_together=set([('sync_resource', 'mix_subscription_id', 'cgsy_subscription_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='synccategory',
            unique_together=set([('sync_resource', 'mix_category_id', 'cgsy_category_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='syncboleto',
            unique_together=set([('mix_boleto', 'cgsy_transaction_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='mixboleto',
            unique_together=set([('sync_resource', 'mix_boleto_id', 'cgsy_subscription_id')]),
        ),
    ]
