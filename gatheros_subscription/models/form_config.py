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

    INSTITUTION_CNPJ_HIDE = 'institution-cnpj-hide'
    INSTITUTION_CNPJ_SHOW = 'institution-cnpj-show'
    INSTITUTION_CNPJ_REQUIRED = 'institution-cnpj-required'

    FUNCTION_HIDE = 'function-hide'
    FUNCTION_SHOW = 'function-show'
    FUNCTION_REQUIRED = 'function-required'

    CPF_OPTIONS = (
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

    INSTITUTION_CNPJ_OPTIONS = (
        (INSTITUTION_CNPJ_HIDE, 'Ocultar'),
        (INSTITUTION_CNPJ_SHOW, 'Mostrar'),
        (INSTITUTION_CNPJ_REQUIRED, 'Mostrar e Tornar obrigatório'),
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
        max_length=35,
        verbose_name='CPF ou ID/Passport',
        help_text='Configuração do campo de documentos pessoais no formulário.'
    )

    birth_date = models.CharField(
        choices=BIRTH_DATE_OPTIONS,
        default=BIRTH_DATE_HIDE,
        max_length=35,
        verbose_name='Data de Nascimento',
        help_text='Configuração do campo "Data de Nascimento" no formulário.'
    )

    address = models.CharField(
        choices=ADDRESS_OPTIONS,
        default=ADDRESS_HIDE,
        max_length=35,
        verbose_name='Endereço',
        help_text='Configuração do campo "Endereço" no formulário.'
                  ' Isto exigirá que alguns campos sejam obrigatórios.'
    )

    institution = models.CharField(
        choices=INSTITUTION_OPTIONS,
        default=INSTITUTION_HIDE,
        max_length=35,
        verbose_name='Empresa/Instituição',
        help_text='Empresa, Igreja, Fundação, etc.'
    )

    institution_cnpj = models.CharField(
        choices=INSTITUTION_CNPJ_OPTIONS,
        default=INSTITUTION_CNPJ_HIDE,
        max_length=35,
        verbose_name='CNPJ',
        help_text='CNPJ da empresa com a qual o(a) partcipante está'
                  ' vinculado(a).'
    )

    function = models.CharField(
        choices=FUNCTION_OPTIONS,
        default=FUNCTION_HIDE,
        max_length=35,
        verbose_name='Cargo/Função',
        help_text='Cargo ou função que exerce profissionalmente.'
    )

    class Meta:
        verbose_name = 'Configuração de formulário'
        verbose_name_plural = 'Configurações de Formulário'
        ordering = ['event']

    @property
    def cpf_show(self):
        show = FormConfig.CPF_SHOW
        required = FormConfig.CPF_REQUIRED
        return self.cpf == show or self.cpf == required

    @property
    def cpf_hide(self):
        return self.phone == FormConfig.CPF_HIDE

    @property
    def cpf_required(self):
        return self.cpf == FormConfig.CPF_REQUIRED

    @property
    def birth_date_show(self):
        show = FormConfig.CPF_SHOW
        required = FormConfig.CPF_REQUIRED
        return self.birth_date == show or self.birth_date == required

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
        show = FormConfig.INSTITUTION_SHOW
        required = FormConfig.INSTITUTION_REQUIRED
        return self.institution == show or self.institution == required

    @property
    def institution_hide(self):
        return self.institution == FormConfig.INSTITUTION_HIDE

    @property
    def institution_required(self):
        return self.institution == FormConfig.INSTITUTION_REQUIRED

    @property
    def institution_cnpj_show(self):
        show = FormConfig.INSTITUTION_CNPJ_SHOW
        required = FormConfig.INSTITUTION_CNPJ_REQUIRED
        show_cnpj = self.institution_cnpj
        return show_cnpj == show or show_cnpj == required

    @property
    def institution_cnpj_hide(self):
        return self.institution_cnpj == FormConfig.INSTITUTION_CNPJ_HIDE

    @property
    def institution_cnpj_required(self):
        return self.institution_cnpj == FormConfig.INSTITUTION_CNPJ_REQUIRED

    @property
    def function_show(self):
        show = FormConfig.FUNCTION_SHOW
        required = FormConfig.FUNCTION_REQUIRED
        return self.function == show or self.function == required

    @property
    def function_hide(self):
        return self.function == FormConfig.FUNCTION_HIDE

    @property
    def function_required(self):
        return self.function == FormConfig.FUNCTION_REQUIRED

    def __str__(self):
        return self.event.name

    def get_required_keys(self) -> list:
        required_keys = []

        config = self

        if config.phone:
            if 'phone' not in required_keys:
                required_keys.append('phone')

        if config.cpf == config.CPF_REQUIRED:
            if 'cpf' not in required_keys:
                required_keys.append('cpf')

        if config.birth_date == config.BIRTH_DATE_REQUIRED:
            if 'birth_date' not in required_keys:
                required_keys.append('birth_date')

        if config.city is True:
            if 'city' not in required_keys:
                required_keys.append('city')

            if 'uf' not in required_keys:
                required_keys.append('uf')

        if config.address == config.ADDRESS_SHOW:
            if 'street' not in required_keys:
                required_keys.append('street')

            if 'complement' not in required_keys:
                required_keys.append('complement')

            if 'number' not in required_keys:
                required_keys.append('number')

            if 'village' not in required_keys:
                required_keys.append('village')

            if 'zip_code' not in required_keys:
                required_keys.append('zip_code')

        if config.institution == config.INSTITUTION_REQUIRED:
            if 'institution' not in required_keys:
                required_keys.append('institution')

        if config.institution_cnpj == config.INSTITUTION_CNPJ_REQUIRED:
            if 'institution_cnpj' not in required_keys:
                required_keys.append('institution_cnpj')

        if config.function == config.FUNCTION_REQUIRED:
            if 'function' not in required_keys:
                required_keys.append('function')

        return required_keys
