from affiliate import services
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

