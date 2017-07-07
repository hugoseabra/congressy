# pylint: disable=W5101
"""
Campo de formulário, responsável pela versatilidade de buscar informações
dos participantes de eventos através de suas inscrições.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from core.util import model_field_slugify
from gatheros_event.models import Organization
from . import AbstractField, Form


class Field(AbstractField):
    """ Modelo de campo de formulário. """

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        verbose_name='organização',
        related_name='fields'
    )
    form_default_field = models.BooleanField(
        default=False,
        verbose_name='campo fixo'
    )
    forms = models.ManyToManyField(
        Form,
        verbose_name='formulário',
        related_name='fields'
    )

    @property
    def orphan(self):
        """
        Campo órfão é o que não está vinculado a qualquer formulário e não
        possui respostas.
        """
        num_forms = self.forms.count()
        num_answers = self.answers.count()
        return num_forms and num_answers

    class Meta:
        verbose_name = 'Campo de Formulário'
        verbose_name_plural = 'Campos de Formulário'
        ordering = ['organization__id', 'order', 'name']
        unique_together = (('organization', 'name'),)

    def save(self, **kwargs):
        is_default = self.form_default_field is True
        if is_default and not self.name or not is_default:
            self.name = model_field_slugify(
                model_class=self.__class__,
                instance=self,
                string=self.label,
                filter_keys={'organization': self.organization},
                slug_field='name'
            )

        return super(Field, self).save(**kwargs)

    def answer(self, subscription):
        """
        Recupera resposta de uma pergunta de acordo com inscrição.

        :param subscription:
        :return: Answer | Mixed
            Pode retornar um valor puro de `Person` ou um objeto Answer
        """

        person = subscription.person
        if self.form_default_field and hasattr(person, self.name):
            return getattr(person, self.name)

        try:
            return self.answers.get(subscription=subscription)

        except ObjectDoesNotExist:
            return None

    def __str__(self):
        required = ''
        if self.required:
            required = '* '

        return required + '{} - {} ({})'.format(
            self.label,
            self.get_field_type_display(),
            self.organization.name
        )
