from django import forms

from payment.models import BankAccount
from payment.tasks import create_pagarme_recipient
from payment import exception as PaymentExceptions


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = (
            'bank_code',
            'agency',
            'agency_dv',
            'account',
            'account_dv',
            'legal_name',
            'document_number',
            'account_type',
        )

    def __init__(self, data=None, *args, **kwargs):

        self.bank_account_id = None
        self.document_type = None
        self.date_created = None

        super(BankAccountForm, self).__init__(data=data, *args,
                                              **kwargs)

        banking_required_fields = ['bank_code', 'agency', 'account',
                                   'account_dv', 'document_number',
                                   'account_type']

        for field in banking_required_fields:
            self.fields[field].required = True

    def clean(self):

        cleaned_data = super().clean()

        recipient_dict = {
            'agencia': cleaned_data.get('agency'),
            'agencia_dv': cleaned_data.get('agency_dv'),
            'bank_code': cleaned_data.get('bank_code'),
            'conta': cleaned_data.get('account'),
            'conta_dv': cleaned_data.get('account_dv'),
            'document_number': cleaned_data.get('document_number'),
            'legal_name': cleaned_data.get('legal_name'),
            'type': cleaned_data.get('account_type'),
        }

        try:
            recipient = create_pagarme_recipient(recipient_dict=recipient_dict)

            self.bank_account_id = recipient['bank_account']['id']
            self.document_type = recipient['bank_account']['document_type']
            self.recipient_id = recipient['id']
            self.date_created = recipient['bank_account']['date_created']

        except PaymentExceptions.RecipientError as e:
            error_dict = {
                "Unknown API error": "Problema ao criar conta. Tente "
                                     "novamente depois."
            }

            if e.message in error_dict:
                e.message = error_dict[e.message]

            raise forms.ValidationError(e.message)

        return cleaned_data

    def save(self, commit=True):
        self.instance = super().save(commit)

        self.instance.bank_account_id = self.bank_account_id
        self.instance.document_type = self.document_type
        self.instance.recipient_id = self.recipient_id
        self.instance.date_created = self.date_created
        self.instance.save()
        return self.instance
