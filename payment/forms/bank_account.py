from django import forms
from localflavor.br.forms import BRCPFField, BRCNPJField

from core.forms.cleaners import clear_string
from payment import exception as PaymentExceptions
from payment.models import BankAccount
from payment.tasks import create_pagarme_recipient


class BankAccountForm(forms.ModelForm):
    type_of_document = forms.BooleanField(label='Tipo de Documento',
                                          required=False)

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
        self.recipient_id = None

        super(BankAccountForm, self).__init__(data=data, *args,
                                              **kwargs)

        banking_required_fields = [
            'bank_code',
            'agency',
            'account',
            'account_dv',
            'document_number',
            'account_type',
            'legal_name',
        ]

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

        for key, value in recipient_dict:
            if value is None:
                raise forms.ValidationError("O valor {} é "
                                            "obrigatorio.".format(key))

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

    def clean_document_number(self):

        type_of_document = self.data.get('type_of_document')
        document_number = clear_string(self.data.get('document_number'))

        if type_of_document:
            document_number = BRCNPJField().clean(document_number)

        else:
            document_number = BRCPFField().clean(document_number)

        return document_number

    def save(self, commit=True):
        self.instance = super().save(commit)

        self.instance.bank_account_id = self.bank_account_id
        self.instance.document_type = self.document_type
        self.instance.recipient_id = self.recipient_id
        self.instance.date_created = self.date_created
        self.instance.save()
        return self.instance
