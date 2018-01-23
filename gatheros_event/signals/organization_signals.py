""" Signals do model `Organization`. """
import pagarme
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import six

from gatheros_event.models import Person, Organization


@receiver(post_save, sender=Person)
def update_person_related_organization(instance, raw, **_):
    """
    Atualiza nomes de Organização e Usuário assim que o nome da
    pessoa é atualizado.
    """

    # Disable when loaded by fixtures
    if raw is True:
        return

    for member in instance.members.filter(organization__internal=True):

        organization = member.organization

        for attr, value in six.iteritems(instance.get_profile_data()):
            setattr(organization, attr, value)

        organization.save()


@receiver(post_save, sender=Organization)
def create_financial_org(instance, raw, **_):
    """
    Atualiza nomes de Organização e Usuário assim que o nome da
    pessoa é atualizado.
    """

    # Disable when loaded by fixtures
    if raw is True:
        return

    required_data = ['bank_code',
                     'agency',
                     'account',
                     'legal_name',
                     'account_type',
                     'cnpj_ou_cpf', ]

    try:

        for item in required_data:
            getattr(instance, item)


        params = {
            'agencia': instance.agency,
            'bank_code': instance.bank_code,
            'conta': instance.account,
            'document_number': instance.cnpj_ou_cpf,
            'legal_name': instance.legal_name
        }

        if hasattr(instance, 'agencia_dv'):
            params['agencia_dv'] = instance.agencia_dv

        if hasattr(instance, 'conta_dv'):
            params['conta_dv'] = instance.conta_dv

        pagarme.authentication_key(settings.PAGARME_API_KEY)

        bank_account = pagarme.bank_account.create(params)

        if bank_account:
            instance.active_bank_account = True

        instance.save()

    except AttributeError:
        pass
