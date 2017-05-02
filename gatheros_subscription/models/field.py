from django.db import models

from . import AbstractField, Form


class FieldManager(models.Manager):
    def append_field( self, field ):
        last_field = Field.objects.filter(form=field.form).order_by('-order').first()
        if last_field:
            return int(last_field.order) + 1
        else:
            return 1


class Field(AbstractField):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, verbose_name='formulário', related_name='fields')
    form_default_field = models.BooleanField(default=False, verbose_name='campo fixo')
    active = models.BooleanField(default=True, verbose_name='ativo')
    with_options = models.BooleanField(default=False, verbose_name='possui opções')

    objects = FieldManager()

    class Meta:
        verbose_name = 'Campo de Formulário'
        verbose_name_plural = 'Campos de Formulário'
        ordering = ['form__id', 'order', 'name']
        unique_together = (('form', 'name'), ('form', 'label'),)

    def save( self, **kwargs ):
        if self._state.adding and not self.order:
            self.order = Field.objects.append_field(self)

        self._accepts_options()

        return super(Field, self).save(**kwargs)

    def __str__( self ):
        required = ''
        if self.required:
            required = '* '

        return required + '{} - {} ({})'.format(self.label, self.get_type_display(), self.form)

    def _accepts_options( self ):
        self.with_options = self.type in [
            self.FIELD_SELECT,
            self.FIELD_CHECKBOX_GROUP,
            self.FIELD_RADIO_GROUP,
        ]
