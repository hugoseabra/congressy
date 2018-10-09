from django.db import models


class SyncResource(models.Model):
    """
    Persistência de credenciais de conexão de banco de dados da MixEvents.
    """

    class Meta:
        verbose_name = 'Conexão DB (MixEvents)'
        verbose_name_plural = 'Conexões DB (MixEvents)'

    alias = models.CharField(
        max_length=15,
        verbose_name='nome único',
        unique=True,
        help_text='Nome único a ser utilizado para busca de credenciais.',
        db_index=True,
    )

    host = models.TextField(
        verbose_name='DB Host',
    )

    user = models.CharField(
        max_length=80,
        verbose_name='DB User',
    )

    password = models.CharField(
        max_length=80,
        verbose_name='DB Pass',
    )

    db_name = models.CharField(
        max_length=80,
        verbose_name='DB Name',
    )


class SyncCategory(models.Model):
    """
    Relaciona entre ID da Categoria da MixEvents com a da Congressy, mantendo
    sincronia de existência de tais registros nas duas plataformas.
    """

    class Meta:
        verbose_name = 'Sync Categoria'
        verbose_name_plural = 'Sync Categorias'
        unique_together = ((
            "sync_resource",
            "mix_category_id",
            "cgsy_category_id",
        ))

    sync_resource = models.ForeignKey(
        to=SyncResource,
        verbose_name='Conexão de DB',
        on_delete=models.PROTECT,
    )

    mix_category_id = models.PositiveSmallIntegerField(
        verbose_name='ID da Categoria (MixEvents)',
        db_index=True,
    )

    cgsy_category_id = models.PositiveSmallIntegerField(
        verbose_name='ID da Categoria (Congressy)',
        db_index=True,
    )

    mix_created = models.DateTimeField(
        verbose_name='Data de criação (MixEvents)',
    )

    mix_updated = models.DateTimeField(
        verbose_name='Data de atualização (MixEvents)',
    )


class MixBoleto(models.Model):
    """
    Boletos gerados na plataforma MixEvents.
    """

    class Meta:
        verbose_name = 'Mix Boleto'
        verbose_name_plural = 'Mix Boletos'
        unique_together = ((
            "sync_resource",
            "mix_boleto_id",
            "cgsy_subscription_id",
        ))

    sync_resource = models.ForeignKey(
        to=SyncResource,
        verbose_name='Conexão de DB',
        on_delete=models.PROTECT,
    )

    mix_subscription_id = models.SmallIntegerField(
        verbose_name='ID de Inscrição (MixEvents)',
        db_index=True,
    )

    mix_boleto_id = models.PositiveSmallIntegerField(
        verbose_name='ID do Boleto (MixEvents)',
        db_index=True,
    )

    cgsy_subscription_id = models.UUIDField(
        verbose_name='UUID de Inscrição (Congressy)',
        db_index=True,
    )

    amount = models.DecimalField(
        max_digits=8,
        null=True,
        blank=True,
        decimal_places=2,
        verbose_name='valor',
    )

    installments = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='parcelas',
    )

    installment_part = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='número da parcela',
    )

    cancelled = models.BooleanField(
        verbose_name='Cancelado',
        default=False,
    )

    paid = models.BooleanField(
        verbose_name='Pago',
        default=False,
    )

    mix_created = models.DateTimeField(
        verbose_name='Data de criação (MixEvents)',
    )

    mix_updated = models.DateTimeField(
        verbose_name='Data de atualização (MixEvents)',
    )


class SyncBoleto(models.Model):
    """
    Relaciona entre MixBoleto (que reflete os boletos da MixEvents) com a
    Transação gerada na Congressy.
    """

    class Meta:
        verbose_name = 'Sync Boleto'
        verbose_name_plural = 'Sync Boletos'
        unique_together = (("mix_boleto", "cgsy_transaction_id"),)

    mix_boleto = models.ForeignKey(
        to=MixBoleto,
        verbose_name='ID MixBoleto',
        on_delete=models.PROTECT,
    )

    cgsy_transaction_id = models.UUIDField(
        verbose_name='UUID de Transação (Congressy)',
        db_index=True,
    )


class SyncSubscription(models.Model):
    """
    Relaciona entre MixBoleto (que reflete os boletos da MixEvents) com a
    Transação gerada na Congressy.
    """

    class Meta:
        verbose_name = 'Sync Inscrição'
        verbose_name_plural = 'Sync Inscrições'
        unique_together = ((
            "sync_resource",
            "mix_subscription_id",
            "cgsy_subscription_id",
        ))

    sync_resource = models.ForeignKey(
        to=SyncResource,
        verbose_name='Conexão de DB',
        on_delete=models.PROTECT,
    )

    mix_subscription_id = models.SmallIntegerField(
        verbose_name='ID de Inscrição (MixEvents)',
        db_index=True,
    )

    cgsy_subscription_id = models.UUIDField(
        verbose_name='UUID de Inscrição (Congressy)',
        db_index=True,
    )

    mix_created = models.DateTimeField(
        verbose_name='Data de criação (MixEvents)',
    )

    mix_updated = models.DateTimeField(
        verbose_name='Data de atualização (MixEvents)',
    )
