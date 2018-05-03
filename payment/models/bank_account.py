from django.db import models
from django.core.validators import RegexValidator


class BankAccount(models.Model):
    class Meta:
        verbose_name = 'Conta Bancaria'
        verbose_name_plural = 'Contas Bancarias'

    CONTA_CORRENTE = 'conta_corrente'
    CONTA_POUPANCA = 'conta_poupanca'
    CONTA_CORRENTE_CONJUNTA = 'conta_corrente_conjunta'
    CONTA_POUPANCA_CONJUNTA = 'conta_poupanca_conjunta'

    BANCO_DO_BRASIL = "001"
    ITAU = "341"
    BRADESCO = "237"
    SANTANDER = "033"
    CAIXA_ECONOMICA = "104"
    BANCOOB = "756"
    SICOOB = "756"

    ACCOUNT_TYPES = (
        (CONTA_CORRENTE, 'Conta corrente'),
        (CONTA_POUPANCA, 'Conta poupanca'),
        (CONTA_CORRENTE_CONJUNTA, 'Conta corrente conjunta'),
        (CONTA_POUPANCA_CONJUNTA, 'Conta poupanca conjunta'),
    )

    BANK_CODES = (
        (BANCO_DO_BRASIL, 'Banco do Brasil'),
        (ITAU, 'Itau'),
        (BRADESCO, 'Bradesco'),
        (SANTANDER, 'Santander'),
        (CAIXA_ECONOMICA, 'Caixa Economica'),
        (BANCOOB, 'BANCOOB - Banco Cooperativo do Brasil'),
        (SICOOB, 'Sicoob'),
    )

    # Obrigatório - Código do banco
    bank_code = models.CharField(
        choices=BANK_CODES,
        max_length=3,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{1,10}$')],
        verbose_name='Banco'
    )

    # Obrigatório - Agencia
    agency = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        validators=[RegexValidator(r'^\d{1,10}$')],
        verbose_name='Agencia'
    )

    # Não obrigatório - Dígito verificador da agência
    agency_dv = models.CharField(
        blank=True,
        null=True,
        max_length=1,
        validators=[RegexValidator(r'^\d{1,10}$')],
        verbose_name='Dígito verificador da agência'
    )

    # Obrigatório - Numero da conta
    account = models.CharField(
        blank=True,
        null=True,
        max_length=13,
        validators=[RegexValidator(r'^\d{1,10}$')],
        verbose_name='Numero da Conta'
    )

    # Não obrigatório - Dígito verificador da Conta
    account_dv = models.CharField(
        blank=True,
        null=True,
        max_length=2,
        validators=[RegexValidator(r'^\d{1,10}$')],
        verbose_name='Dígito verificador da Conta'
    )

    # Obrigatório - CPF ou CNPJ da conta com ou sem pontuações
    document_number = models.CharField(
        unique=True,
        max_length=14,
        blank=True,
        null=True,
        verbose_name='CPF ou CNPJ'
    )

    # Obrigatório - Nome completo ou razão social
    legal_name = models.CharField(
        blank=True,
        max_length=30,
        null=True,
        verbose_name='Titular/Razão social',
        help_text='IMPORTANTE: este campo não pode ser muito diferente do'
                  ' titular da conta. Se o titular tiver mais de 30'
                  ' caracteres, você pode abreviar de forma que fique fácil'
                  ' identificar títular.'
    )

    # Obrigatório - Tipo da conta
    account_type = models.CharField(
        choices=ACCOUNT_TYPES,
        default=CONTA_CORRENTE,
        blank=True,
        null=True,
        max_length=25,
        verbose_name='Tipo de Conta'
    )

    bank_account_id = models.IntegerField(
        null=True,
        blank=True,
    )

    document_type = models.CharField(
        max_length=4,
        blank=True,
        null=True,
    )

    date_created = models.CharField(
        max_length=50,
        blank=True,
        null=True,
    )

    # Dados de recebedor do Pagar.me
    ativo = models.BooleanField(default=False)

    recipient_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    def __str__(self):
        return '{} - ({})'.format(self.bank_account_id, self.recipient_id)
