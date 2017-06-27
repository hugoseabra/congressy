# pylint: disable=W5101
"""
Campo de formulário, responsável pela versatilidade de buscar informações
dos participantes de eventos através de suas inscrições.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from core.util import model_field_slugify
from . import AbstractField, Form


class FieldManager(models.Manager):
    """ Gerenciador de campo - manager """

    # noinspection PyMethodMayBeStatic
    def append_field(self, field):
        last_field = Field.objects.filter(form=field.form) \
            .order_by('-order') \
            .first()
        if last_field:
            return int(last_field.order) + 1
        else:
            return 1


class Field(AbstractField):
    """ Modelo de campo de formulário. """

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        verbose_name='formulário',
        related_name='fields'
    )
    form_default_field = models.BooleanField(
        default=False,
        verbose_name='campo fixo'
    )

    objects = FieldManager()

    class Meta:
        verbose_name = 'Campo de Formulário'
        verbose_name_plural = 'Campos de Formulário'
        ordering = ['form__id', 'order', 'name']
        unique_together = (('form', 'name'),)

    def save(self, **kwargs):
        if self._state.adding and not self.order:
            self.order = Field.objects.append_field(self)

        if self.form_default_field:
            to_slug = self.label if not self.name else self.name
        else:
            to_slug = self.label

        self.name = model_field_slugify(
            model_class=self.__class__,
            instance=self,
            string=to_slug,
            filter_keys={'form': self.form},
            slug_field='name'
        )

        return super(Field, self).save(**kwargs)

    def answer(self, subscription):
        """ Recupera resposta de uma pergunta de acordo com inscrição. """

        if self.form_default_field:
            return getattr(subscription.person, self.name)

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
            self.form
        )
