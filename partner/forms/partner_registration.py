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

# @TODO make this a form.Form
from payment.models import BankAccount


class PartnerRegistrationForm(PersonForm):
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

        instance = kwargs.get('instance')
        if instance and isinstance(instance, Partner):
            if hasattr(instance, 'person'):
                kwargs['instance'] = instance.person
        else:
            data = kwargs.get('data')
            if data and 'email' in data:
                try:
                    kwargs['instance'] = Person.objects.get(
                        email=data['email'],
                        user_id__isnull=False
                    )

                except Person.DoesNotExist:
                    pass

        super(PartnerRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['phone'].required = True
        self.fields['email'].required = True
        self.fields['name'].required = True

    def clean(self):
        cleaned_data = super().clean()

        try:
            user = User.objects.get(email=cleaned_data['email'])
            if hasattr(user, 'person'):
                person = user.person
                if person.pk != self.instance.pk:
                    raise forms.ValidationError(
                        'Já existe um usuário com este e-mail. Se este e-mail'
                        ' é realmente seu, entre em contato conosco.'
                    )
            else:
                self.instance.user_id = user.pk

        except User.DoesNotExist:
            pass

        return cleaned_data

    def save(self, domain_override=None, request=None,
             commit=True,
             subject_template='registration/account_confirmation_subject.txt',
             email_template='registration/account_confirmation_email.html'):
        """
        Cria uma conta no sistema

        """

        super(PersonForm, self).save(commit=True)

        partner, created = Partner.objects.get_or_create(
            person=self.instance,
        )

        if created is False:
            self.notify_partner(request)
            return partner

        # Criando Organização.
        org = Organization(internal=False, name=self.instance.name)

        for attr, value in six.iteritems(self.instance.get_profile_data()):
            setattr(org, attr, value)

        org.save()

        Member.objects.create(
            organization=org,
            person=self.instance,
            group=Member.ADMIN
        )

        self.notify_partner(request)
        self.notify_partner_internal(request)
        return self.instance

    def clean_email(self):
        return self.data.get('email').lower()

    def notify_partner(self, request=None):
        email = self.cleaned_data["email"]
        phone = self.cleaned_data["phone"]

        context = {
            'partner_name': self.instance.name,
            'nome': self.instance.user.first_name,
            'partner_email': email,
            'partner_phone': phone,
            'site_name': get_current_site(request)
        }

        notify_new_partner(context)

    def notify_partner_internal(self, request=None):
        email = self.cleaned_data["email"]
        phone = self.cleaned_data["phone"]

        context = {
            'partner_name': self.instance.name,
            'nome': self.instance.user.first_name,
            'partner_email': email,
            'partner_phone': phone,
            'site_name': get_current_site(request)
        }

        notify_new_partner_internal(context)


class FullPartnerRegistrationForm(CombinedFormBase):
    form_classes = {
        'partner': PartnerRegistrationForm,
        'bank_account': BankAccountForm
    }

    def __init__(self, **kwargs):

        data = kwargs.get('data')
        instances = {}
        if data:
            if 'email' in data:
                try:
                    person = Person.objects.get(
                        email=data['email'],
                        user_id__isnull=False
                    )
                    instances['partner'] = person

                except Person.DoesNotExist:
                    pass

            try:
                account = BankAccount.objects.get(
                    bank_code=data['bank_code'],
                    agency=data['agency'],
                    agency_dv=data['agency_dv'],
                    account=data['account'],
                    account_dv=data['account_dv'],
                    legal_name=data['legal_name'],
                    account_type=data['account_type'],
                    document_number=data['document_number'],
                )
                instances['bank_account'] = account

            except BankAccount.DoesNotExist:
                pass

            if instances:
                kwargs['instances'] = instances

        super().__init__(**kwargs)

    def save(self, commit=True):
        instances = super().save(commit)
        partner = instances.get('partner')
        bank_account = instances.get('bank_account')

        person = partner.person

        if bank_account.document_type == 'cpf':
            person.cpf = bank_account.document_number
        elif bank_account.document_type == 'cnpj':
            person.institution_cnpj = bank_account.document_number

        person.save()

        partner.bank_account = bank_account
        partner.save()
        return instances
