# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-10 15:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import gatheros_event.models.mixins.gatheros_model_mixin
import jsonfield.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gatheros_event', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', jsonfield.fields.JSONField(blank=True, null=True, verbose_name='valor')),
            ],
            options={
                'verbose_name': 'resposta',
                'ordering': ['field'],
                'verbose_name_plural': 'respostas',
            },
        ),
        migrations.CreateModel(
            name='DefaultField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='nome')),
                ('label', models.CharField(max_length=255, verbose_name='rótulo')),
                ('field_type', models.CharField(choices=[('input-text', 'Texto (255 caracteres)'), ('input-number', 'Número'), ('input-date', 'Data'), ('input-datetime-local', 'Data e hora'), ('input-email', 'E-mail'), ('input-phone', 'Telefone'), ('textarea', 'Texto longo'), ('boolean', 'SIM/NÃO'), ('select', 'Lista simples'), ('checkbox-group', 'Múltipla escolha'), ('radio-group', 'Escolha única')], default='input-text', max_length=20, verbose_name='tipo')),
                ('required', models.BooleanField(default=False, verbose_name='obrigatório')),
                ('select_intro', models.BooleanField(default=False, help_text='Acrescenta `- Selecione -` na primeira opção da lista simples', verbose_name='Mostrar primeiro em branco')),
                ('instruction', models.TextField(blank=True, null=True, verbose_name='instrução')),
                ('placeholder', models.CharField(blank=True, max_length=100, null=True, verbose_name='placeholder')),
                ('default_value', models.TextField(blank=True, null=True, verbose_name='valor padrão')),
                ('with_options', models.BooleanField(default=False, verbose_name='possui opções')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('order', models.PositiveIntegerField(blank=True, null=True, verbose_name='ordem')),
            ],
            options={
                'verbose_name': 'Campo Padrão',
                'ordering': ['order'],
                'verbose_name_plural': 'Campos Padrão',
            },
            bases=(models.Model, gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin),
        ),
        migrations.CreateModel(
            name='DefaultFieldOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='rótulo')),
                ('value', models.CharField(blank=True, max_length=255, null=True, verbose_name='valor')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='gatheros_subscription.DefaultField', verbose_name='campo')),
            ],
            options={
                'verbose_name': 'Opção de Campo Padrão',
                'ordering': ['field__id', 'name'],
                'verbose_name_plural': 'Opções de Campo Padrão',
            },
            bases=(models.Model, gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin),
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='nome')),
                ('label', models.CharField(max_length=255, verbose_name='rótulo')),
                ('field_type', models.CharField(choices=[('input-text', 'Texto (255 caracteres)'), ('input-number', 'Número'), ('input-date', 'Data'), ('input-datetime-local', 'Data e hora'), ('input-email', 'E-mail'), ('input-phone', 'Telefone'), ('textarea', 'Texto longo'), ('boolean', 'SIM/NÃO'), ('select', 'Lista simples'), ('checkbox-group', 'Múltipla escolha'), ('radio-group', 'Escolha única')], default='input-text', max_length=20, verbose_name='tipo')),
                ('required', models.BooleanField(default=False, verbose_name='obrigatório')),
                ('select_intro', models.BooleanField(default=False, help_text='Acrescenta `- Selecione -` na primeira opção da lista simples', verbose_name='Mostrar primeiro em branco')),
                ('instruction', models.TextField(blank=True, null=True, verbose_name='instrução')),
                ('placeholder', models.CharField(blank=True, max_length=100, null=True, verbose_name='placeholder')),
                ('default_value', models.TextField(blank=True, null=True, verbose_name='valor padrão')),
                ('with_options', models.BooleanField(default=False, verbose_name='possui opções')),
                ('active', models.BooleanField(default=True, verbose_name='ativo')),
                ('form_default_field', models.BooleanField(default=False, verbose_name='campo fixo')),
            ],
            options={
                'verbose_name': 'Campo de Formulário',
                'ordering': ['organization__id', 'name'],
                'verbose_name_plural': 'Campos de Formulário',
            },
            bases=(models.Model, gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin),
        ),
        migrations.CreateModel(
            name='FieldOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='rótulo')),
                ('value', models.CharField(blank=True, max_length=255, null=True, verbose_name='valor')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='options', to='gatheros_subscription.Field', verbose_name='campo')),
            ],
            options={
                'verbose_name': 'Opção de Campo',
                'ordering': ['field__id', 'name'],
                'verbose_name_plural': 'Opções de Campo',
            },
            bases=(models.Model, gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin),
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('required_configuration', jsonfield.fields.JSONField(blank=True, help_text='CUIDADO: Configuração de camops cujas obrigatoriedades foram alteradas do campo original.', null=True, verbose_name='Config. de Obrigatoriedade')),
                ('inactive_fields', models.TextField(blank=True, help_text='CUIDADO: Campos que estão inativos especificamente para este formulário.', null=True, verbose_name='campos inativos')),
                ('order', models.TextField(blank=True, help_text='CUIDADO: Nome dos campos do formulário separados por víngula.', null=True, verbose_name='ordem')),
                ('event', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='form', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name': 'formulário de evento',
                'permissions': (('can_add_field', 'Can add field'),),
                'ordering': ['event'],
                'verbose_name_plural': 'formulários de eventos',
            },
        ),
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='nome')),
                ('date_start', models.DateTimeField(verbose_name='data inicial')),
                ('date_end', models.DateTimeField(blank=True, null=True, verbose_name='data final')),
                ('limit', models.PositiveIntegerField(blank=True, null=True, verbose_name='vaga(s)')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='preço')),
                ('tax', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='taxa')),
                ('discount_type', models.CharField(blank=True, choices=[('percent', '%'), ('money', 'R$')], default='percent', max_length=15, null=True, verbose_name='tipo de desconto')),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True, verbose_name='desconto')),
                ('promo_code', models.CharField(blank=True, max_length=15, null=True, verbose_name='código promocional')),
                ('transfer_tax', models.BooleanField(default=False, verbose_name='repassar taxa')),
                ('private', models.BooleanField(default=False, help_text='Não estará explícito para o participante no site do evento', verbose_name='privado')),
                ('internal', models.BooleanField(default=False, verbose_name='interno')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('exhibition_code', models.CharField(blank=True, max_length=15, null=True, verbose_name='código de exibição')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lots', to='gatheros_event.Event', verbose_name='evento')),
            ],
            options={
                'verbose_name': 'lote',
                'ordering': ['date_start', 'date_end', 'pk', 'name'],
                'verbose_name_plural': 'lotes',
            },
            bases=(models.Model, gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('origin', models.CharField(choices=[('hotsite', 'Hotsite do evento'), ('manage', 'Manage')], default='hotsite', max_length=15, verbose_name='origem')),
                ('created_by', models.PositiveIntegerField(verbose_name='criado por')),
                ('attended', models.BooleanField(default=False, verbose_name='compareceu')),
                ('code', models.CharField(blank=True, max_length=15, verbose_name='código')),
                ('count', models.IntegerField(blank=True, default=None, verbose_name='num. inscrição')),
                ('attended_on', models.DateTimeField(blank=True, null=True, verbose_name='confirmado em')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('modified', models.DateTimeField(auto_now_add=True, verbose_name='modificado em')),
                ('synchronized', models.BooleanField(default=False)),
                ('event', models.ForeignKey(blank=True, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='gatheros_event.Event', verbose_name='evento')),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='gatheros_subscription.Lot', verbose_name='lote')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='gatheros_event.Person', verbose_name='pessoa')),
            ],
            options={
                'verbose_name': 'Inscrição',
                'ordering': ['person', 'created', 'event'],
                'verbose_name_plural': 'Inscrições',
            },
            bases=(models.Model, gatheros_event.models.mixins.gatheros_model_mixin.GatherosModelMixin),
        ),
        migrations.AddField(
            model_name='field',
            name='forms',
            field=models.ManyToManyField(related_name='fields', to='gatheros_subscription.Form', verbose_name='formulário'),
        ),
        migrations.AddField(
            model_name='field',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='gatheros_event.Organization', verbose_name='organização'),
        ),
        migrations.AddField(
            model_name='answer',
            name='field',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='gatheros_subscription.Field', verbose_name='campo'),
        ),
        migrations.AddField(
            model_name='answer',
            name='subscription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='gatheros_subscription.Subscription', verbose_name='inscrição'),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('lot', 'count'), ('person', 'event'), ('event', 'code')]),
        ),
        migrations.AlterUniqueTogether(
            name='lot',
            unique_together=set([('name', 'event')]),
        ),
        migrations.AlterUniqueTogether(
            name='fieldoption',
            unique_together=set([('field', 'value')]),
        ),
        migrations.AlterUniqueTogether(
            name='field',
            unique_together=set([('organization', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='defaultfieldoption',
            unique_together=set([('field', 'value')]),
        ),
        migrations.AlterUniqueTogether(
            name='answer',
            unique_together=set([('subscription', 'field')]),
        ),
    ]
