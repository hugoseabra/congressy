from django.db import models

from base.models import EntityMixin, RuleChecker, RuleIntegrityError
from core.model import track_data
from core.model.validators import cpf_validator, cnpj_validator
from core.util.phone import format_phone_number, get_country_code_by_region
from core.util.string import clear_string
from gatheros_event.locale import locales
from gatheros_event.locale.country_choices import get_country_choices
from gatheros_event.locale.phone_choices import get_phone_choices


class BeneficiaryEditionRule(RuleChecker):
    """
    Regra: A pessoa da inscrição é a mesma beneficiária do pagador.
    """

    def check(self, model_instance, *args, **kwargs):
        is_edition = model_instance.is_new is False

        if is_edition and model_instance.has_changed('beneficiary'):
            raise RuleIntegrityError(
                'Você não pode editar o beneficiário.'
            )


@track_data('beneficiary')
class Benefactor(EntityMixin, models.Model):
    rule_instances = (
        BeneficiaryEditionRule,
    )

    class Meta:
        verbose_name = 'benfeitor'
        verbose_name_plural = 'benfeitores'

    INTERNATIONAL_DOC_ID = 'ID'
    INTERNATIONAL_DOC_PASSPORT = 'Passport'
    INTERNATIONAL_DOC_EIN = 'EIN'
    INTERNATIONAL_DOC_TYPES = (
        (INTERNATIONAL_DOC_ID, 'ID'),
        (INTERNATIONAL_DOC_PASSPORT, 'Passport'),
        (INTERNATIONAL_DOC_EIN, 'EIN'),
    )

    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_UNDEFINED = 'U'
    GENDER_CHOICES = (
        (GENDER_MALE, 'Masculino'),
        (GENDER_FEMALE, 'Feminino'),
        (GENDER_UNDEFINED, 'Prefiro não definir'),
    )

    beneficiary = models.ForeignKey(
        'gatheros_event.Person',
        on_delete=models.CASCADE,
        verbose_name='pessoa',
        related_name='benefactors',
        # Making field required
        blank=False,
        null=True,
    )

    is_company = models.BooleanField(
        default=False,
        verbose_name='é pessoa juridica'
    )

    name = models.CharField(
        max_length=200,
        verbose_name='nome do pagador',
        blank=False,
        null=False,
    )

    reference = models.CharField(
        max_length=30,
        verbose_name='referência',
        blank=True,
        null=True,
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name='sexo',
        blank=True,
        null=True,
        default=GENDER_MALE
    )

    birth_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='data de nasc.'
    )

    email = models.EmailField(
        verbose_name='e-mail',
        null=False,
        blank=False,
    )

    city = models.ForeignKey(
        'kanu_locations.City',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='cidade-UF'
    )

    city_international = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Cidade (Fora do Brasil)',
        help_text='Informe a cidade e estado ou província.',
    )

    zip_code = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        verbose_name='CEP'
    )

    zip_code_international = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='CEP/Caixa Postal'
    )

    street = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='logradouro',
        help_text="Rua / Avenida / Viela / etc."
    )

    number = models.CharField(
        max_length=20,
        verbose_name='número',
        blank=True,
        null=True,
        help_text="Caso não tenha, informar S/N."
    )

    complement = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='complemento'
    )

    village = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='bairro'
    )

    address_international = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='endereço',
    )

    state_international = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='estado',
    )

    country = models.CharField(
        choices=get_country_choices(),
        default=locales.BRASIL['codes']['digits_2'],
        max_length=10,
        blank=True,
        null=False,
        verbose_name='país',
    )

    ddi = models.CharField(
        choices=get_phone_choices(),
        default=locales.BRASIL['codes']['digits_2'],
        max_length=10,
        blank=True,
        null=False,
        verbose_name='DDI',
        help_text='Código discagem do país.',
    )

    phone = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        verbose_name='celular',
    )

    cpf = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='CPF',
        validators=[cpf_validator],
    )

    cnpj = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name='CNPJ',
        help_text='CNPJ da empresa com a qual você está vinculado(a)',
        validators=[cnpj_validator],
    )

    ein = models.CharField(
        max_length=14,
        blank=True,
        null=True,
        verbose_name='EIN/Tax ID',
        help_text='Employer ID Number',
    )

    doc_type = models.CharField(
        max_length=11,
        verbose_name='tipo de documento',
        help_text='Informe o tipo de documento.',
        choices=INTERNATIONAL_DOC_TYPES,
        null=True,
        blank=True,
    )

    doc_number = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        verbose_name='Núm. Documento',
        help_text='Número de documento utilizado fora do Brasil.'
    )

    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    card_holder_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Nome impresso no cartão',
        help_text='Nome impresso no último cartão utilizado.'
    )

    def get_phone_display(self):
        phone = str(self.phone)
        if not phone:
            return ''

        return format_phone_number(
            get_country_code_by_region(self.ddi),
            clear_string(self.phone),
        )
