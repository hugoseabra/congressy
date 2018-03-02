from uuid import uuid4

from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six

from core.forms import CombinedFormBase
from core.forms.widgets import TelephoneInput
from gatheros_event.forms import PersonForm
from gatheros_event.models import Person, Organization, Member
from mailer.services import notify_new_partner, notify_new_partner_internal
from partner.models import Partner
from payment.forms import BankAccountForm


class PartnerRegistrationForm(PersonForm):
    partner = None
    user = None

    class Meta:
        """ Meta """
        model = Person
        fields = ['name', 'email', 'phone']

        widgets = {
            # CPF como telefone para aparecer como número no mobile
            'name': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'me@you.com'}),
            'phone': TelephoneInput(attrs={'placeholder': '(00) 00000-0000'}),
        }

    def __init__(self, *args, **kwargs):
        super(PartnerRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['name'].required = True

    def save(self, domain_override=None, request=None,
             commit=True,
             subject_template='registration/account_confirmation_subject.txt',
             email_template='registration/account_confirmation_email.html'):
        """
        Cria uma conta no sistema

        """

        super(PersonForm, self).save(commit=True)

        # Criando usuário
        if not self.user:
            self.user = User.objects.create_user(
                username=self.cleaned_data["email"],
                email=self.cleaned_data["email"],
                password=str(uuid4())
            )

            self.user.save()

        person = self.instance

        # Vinculando usuário ao perfil
        person.user = self.user
        person.save()

        self.instance = Partner.objects.create(person=person)

        # Criando Organização.
        org = Organization(internal=False, name=person.name)

        for attr, value in six.iteritems(person.get_profile_data()):
            setattr(org, attr, value)

        org.save()

        Member.objects.create(
            organization=org,
            person=person,
            group=Member.ADMIN
        )

        email = self.cleaned_data["email"]
        phone = self.cleaned_data["phone"]

        context = {
            'partner_name': self.user.get_full_name(),
            'nome': self.user.first_name,
            'partner_email': email,
            'partner_phone': phone,
            'site_name': get_current_site(request)
        }

        notify_new_partner(context)
        notify_new_partner_internal(context)

        return self.instance

    def clean_email(self):
        return self.data.get('email').lower()

    def clean(self):

        cleaned_data = super(PartnerRegistrationForm, self).clean()

        email = cleaned_data.get('email')

        try:
            self.user = User.objects.get(username=email)
            raise forms.ValidationError(
                "Esse email já existe em nosso sistema. Tente novamente.")
        except User.DoesNotExist:
            pass

        return cleaned_data


class FullPartnerRegistrationForm(CombinedFormBase):
    form_classes = {
        'partner': PartnerRegistrationForm,
        'bank_account': BankAccountForm
    }

    def save(self, commit=True):
        instances = super().save(commit)
        partner = instances.get('partner')
        bank_account = instances.get('bank_account')

        if bank_account.document_type == 'cpf':
            person = partner.person
            person.cpf = bank_account.document_number
            person.save()

        partner.bank_account = bank_account
        partner.save()
        return instances
