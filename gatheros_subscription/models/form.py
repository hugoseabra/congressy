# pylint: disable=W5101
"""
Formulário de evento, utilizado para captação de informações de pessoas
através de suas inscrições.
"""
import re
from django.db import models
from jsonfield import JSONField

from gatheros_event.models import Event
from .rules import form as rule


# Lista ordenada em JSONField - Reference:
# https://github.com/dmkoch/django-jsonfield#advanced-usage


class Form(models.Model):
    """ Modelo de Formulário de evento. """

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='form'
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name='criado em')
    required_configuration = JSONField(
        verbose_name='Config. de Obrigatoriedade',
        null=True,
        blank=True,
        help_text='CUIDADO: Configuração de camops cujas obrigatoriedades'
                  ' foram alteradas do campo original.'
    )
    inactive_fields = models.TextField(
        verbose_name='campos inativos',
        null=True,
        blank=True,
        help_text='CUIDADO: Campos que estão inativos especificamente para'
                  ' este formulário.'
    )
    order = models.TextField(
        verbose_name='ordem',
        null=True,
        blank=True,
        help_text='CUIDADO: Nome dos campos do formulário separados por'
                  ' víngula.'
    )

    class Meta:
        verbose_name = 'formulário de evento'
        verbose_name_plural = 'formulários de eventos'
        ordering = ['event']

        permissions = (
            ("can_add_field", "Can add field"),
        )

    def save(self, *args, **kwargs):
        """ Salva entidade. """
        self.check_rules()
        super(Form, self).save(*args, **kwargs)

    def __str__(self):
        return self.event.name

    def check_rules(self):
        """ Verifica regras de negócio. """

        rule.rule_1_form_em_event_inscricao_desativada(self)

    @property
    def get_additional_fields(self):
        """ Recupera os campos que são adicionais. """

        return self.fields.filter(form_default_field=False)

    @property
    def has_additional_fields(self):
        """ Verifica se há campos adicionais. """

        return self.get_additional_fields.count() > 0

    def is_required(self, field):
        """
        Resgata valor de `required` customizado para o formulário.
        :type field: Field
        :rtype: bool
        """
        config = self.required_configuration
        custom_required = config.get(field.name) if config else None
        if custom_required is None:
            return field.required

        return custom_required is True

    def get_order_list(self):
        """
        Resgata lista de ordem de campos.
        :rtype: list
        """
        order_list = re.split('[;,\r\n]', self.order) if self.order else []
        return list(filter(None, order_list))

    def set_order_list(self, fields_list):
        """
        Seta valor em `order` de forma padronizada.
        :param fields_list: Lista de `name` dos campos.
        :type fields_list: list
        """
        fields_list = list(filter(None, fields_list))
        self.order = "\n".join(fields_list)

    def add_to_order(self, field):
        """
        Adiciona campo à ordem de campos do formulário
        :param field: Field
        """
        order_list = self.get_order_list()
        order_list.append(field.name)
        self.set_order_list(order_list)

    def get_inactive_fields_list(self):
        """
        Resgata lista de ordem de campos.
        :rtype: list
        """
        if not self.inactive_fields:
            return []

        order_list = re.split('[;,\r\n]', self.inactive_fields)
        return list(filter(None, order_list))

    def set_inactive_fields_list(self, fields_list):
        """
        Seta valor em `inactive_fields` de forma padronizada.
        :param fields_list: Lista de `name` dos campos.
        :type fields_list: list
        """
        fields_list = list(filter(None, fields_list))
        self.inactive_fields = "\n".join(fields_list)

    def is_active(self, field):
        """
         Verifica se `Field` está desativado para este formulário.
        :param field: Field
        :rtype: bool
        """
        config = self.inactive_fields
        inactive_list = re.split('[;,\r\n]', config) if config else []

        return field.name in inactive_list if config else True

    def get_inactive_field_list(self):
        """
        Resgata lista de campos inativos para este formulário.
        :rtype: list
        """
        config = self.inactive_fields
        inactive_list = re.split('[;,\r\n]', config) if config else []
        return list(filter(None, inactive_list))

    def activate_field(self, field):
        """
        Ativa campo no formulário removendo-o da lista de campos inativos.
        :param field: Field
        """
        config = self.inactive_fields if self.inactive_fields else []

        inactive_list = re.split('[;,\r\n]', config) if config else []
        updated_list = []
        for field_name in inactive_list:
            if field_name == field.name:
                continue

            updated_list.append(field_name)

        self.inactive_fields = "\n".join(updated_list)

    def deactivate_field(self, field):
        """
        Desativa campo no formulário incluindo-o da lista de campos inativos.
        :param field: Field
        """
        config = self.inactive_fields if self.inactive_fields else []

        inactive_list = re.split('[;,\r\n]', config) if config else []
        if field.name in inactive_list:
            return

        inactive_list.append(field.name)
        self.inactive_fields = "\n".join(inactive_list)
