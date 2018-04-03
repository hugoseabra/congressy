from django.db import transaction

from affiliate import services
from affiliate.models import Affiliate
from base import forms
from gatheros_event.forms import PersonForm
from payment.forms import BankAccountForm


class AffiliateForm(forms.CombinedFormBase):
    form_classes = (
        ('person', PersonForm),
        ('bank_account', BankAccountForm),
        # ('affiliate', services.AffiliateService),
    )

    display_fields = {
        'person': (
            'name',
            'gender',
            'email',
            'birth_date',
        ),
    }

    def save(self, commit=True):
        with transaction.atomic():
            instances = super().save(commit)

            person = instances.get('person')
            bank_account = instances.get('bank_account')

            data = {
                'person': person.pk,
                'bank_account': bank_account.pk,
            }

            try:
                affiliate = Affiliate.objects.get(person=person)
                service = services.AffiliateService(data=data,
                                                    instance=affiliate)

            except Affiliate.DoesNotExist:
                service = services.AffiliateService(data=data)

            if not service.is_valid():
                raise Exception(
                    'Não foi possível salvar afiliado: {}' + service.errors
                )

        return service.save()
