# pylint: disable=W5101
"""
Define a configuração personalizada de um formulário de inscrição.
"""
import os
from urllib.parse import parse_qs, urlparse

from django.db import models
from django.utils.html import strip_tags
from stdimage import StdImageField
from stdimage.validators import MaxSizeValidator, MinSizeValidator

from gatheros_event.models import Event


class FormConfig(models.Model):
    """ Configuração de formulário de inscrição. """

    CPF_HIDE = 'cpf-hide'
    CPF_SHOW = 'cpf-show'
    CPF_REQUIRED = 'cpf-required'

    BIRTH_DATE_HIDE = 'birth-date-hide'
    BIRTH_DATE_SHOW = 'birth-date-show'
    BIRTH_DATE_REQUIRED = 'birth-date-required'

    ADDRESS_HIDE = 'address-hide'
    ADDRESS_SHOW = 'address-show'

    INSTITUTION_HIDE = 'institution-hide'
    INSTITUTION_SHOW = 'institution-show'
    INSTITUTION_REQUIRED = 'institution-required'

    FUNCTION_HIDE = 'function-hide'
    FUNCTION_SHOW = 'function-show'
    FUNCTION_REQUIRED = 'function-required'

    CPF_OPTIONS=(
        (CPF_HIDE, 'Ocultar'),
        (CPF_SHOW, 'Mostrar'),
        (CPF_REQUIRED, 'Mostrar e Tornar obrigatório'),
    )

    BIRTH_DATE_OPTIONS = (
        (BIRTH_DATE_HIDE, 'Ocultar'),
        (BIRTH_DATE_SHOW, 'Mostrar'),
        (BIRTH_DATE_REQUIRED, 'Mostrar e Tornar obrigatório'),
    )

    ADDRESS_OPTIONS = (
        (ADDRESS_HIDE, 'Ocultar'),
        (ADDRESS_SHOW, 'Mostrar'),
    )

    INSTITUTION_OPTIONS = (
        (INSTITUTION_HIDE, 'Ocultar'),
        (INSTITUTION_SHOW, 'Mostrar'),
        (INSTITUTION_REQUIRED, 'Mostrar e Tornar obrigatório'),
    )

    FUNCTION_OPTIONS = (
        (FUNCTION_HIDE, 'Ocultar'),
        (FUNCTION_SHOW, 'Mostrar'),
        (FUNCTION_REQUIRED, 'Mostrar e Tornar obrigatório'),
    )

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name='formconfig',
        primary_key=True,
        verbose_name='evento'
    )

    email = models.BooleanField(
        default=False,
        verbose_name='e-mail obrigatório',
    )

    phone = models.BooleanField(
        default=False,
        verbose_name='celular obrigatório',
    )

    city = models.BooleanField(
        default=False,
        verbose_name='cidade obrigatório',
        help_text="Caso você insirá o endereço, este campo será obrigatório"
                  " por padrão."
    )

    cpf = models.CharField(
        choices=CPF_OPTIONS,
        default=CPF_HIDE,
        max_length=25,
        verbose_name='CPF',
        help_text='Configuração do campo "CPF" no formulário.'
    )

    birth_date = models.CharField(
        choices=BIRTH_DATE_OPTIONS,
        default=BIRTH_DATE_HIDE,
        max_length=25,
        verbose_name='Data de Nascimento',
        help_text='Configuração do campo "Data de Nascimento" no formulário.'
    )

    address = models.CharField(
        choices=ADDRESS_OPTIONS,
        default=ADDRESS_HIDE,
        max_length=25,
        verbose_name='Endereço',
        help_text='Configuração do campo "Endereço" no formulário.'
                  ' Isto exigirá que alguns campos sejam obrigatórios.'
    )

    institution = models.CharField(
        choices=INSTITUTION_OPTIONS,
        default=INSTITUTION_HIDE,
        max_length=25,
        verbose_name='Empresa/Instituição',
        help_text='Empresa, Igreja, Fundação, etc.'
    )

    function = models.CharField(
        choices=FUNCTION_OPTIONS,
        default=FUNCTION_HIDE,
        max_length=25,
        verbose_name='Cargo/Função',
        help_text='Cargo ou função que exerce profissialmente.'
    )

    class Meta:
        verbose_name = 'Configuração de formulário'
        verbose_name_plural = 'Configurações de Formulário'
        ordering = ['event']

    @property
    def cpf_show(self):
        return self.phone == FormConfig.CPF_SHOW or FormConfig.CPF_REQUIRED

    @property
    def cpf_hide(self):
        return self.phone == FormConfig.CPF_HIDE

    @property
    def cpf_required(self):
        return self.birth_date == FormConfig.CPF_REQUIRED

    @property
    def birth_date_show(self):
        return self.phone == \
               FormConfig.BIRTH_DATE_SHOW or FormConfig.BIRTH_DATE_REQUIRED

    @property
    def birth_date_hide(self):
        return self.phone == FormConfig.BIRTH_DATE_HIDE

    @property
    def birth_date_required(self):
        return self.birth_date == FormConfig.BIRTH_DATE_REQUIRED

    @property
    def address_show(self):
        return self.address == FormConfig.ADDRESS_SHOW

    @property
    def address_hide(self):
        return self.address == FormConfig.ADDRESS_HIDE

    @property
    def institution_show(self):
        print(self.institution);
        return self.institution == \
               FormConfig.INSTITUTION_SHOW or FormConfig.INSTITUTION_REQUIRED

    @property
    def institution_hide(self):
        return self.institution == FormConfig.INSTITUTION_HIDE

    @property
    def institution_required(self):
        return self.institution == FormConfig.INSTITUTION_REQUIRED

    @property
    def function_show(self):
        return self.function == \
               FormConfig.FUNCTION_SHOW or FormConfig.FUNCTION_REQUIRED

    @property
    def function_hide(self):
        return self.function == FormConfig.FUNCTION_HIDE

    @property
    def function_required(self):
        return self.function == FormConfig.FUNCTION_REQUIRED

    def __str__(self):
        return self.event.name
