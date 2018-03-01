from uuid import uuid4

from django import forms
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six

from core.forms import CombinedFormBase
from core.forms.widgets import TelephoneInput
from gatheros_event.forms import ProfileCreateForm
from gatheros_event.models import Person, Organization, Member
from mailer.services import notify_new_partner, notify_new_partner_internal
from partner.models import Partner
from payment.forms import BankAccountForm


class PartnerRegistrationForm(ProfileCreateForm):

    partner = None

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

        super(ProfileCreateForm, self).save(commit=True)

        # Criando usuário
        if not self.user:
            self.user = User.objects.create_user(
                username=self.cleaned_data["email"],
                email=self.cleaned_data["email"],
                password=str(uuid4())
            )

            self.user.save()

        # Vinculando usuário ao perfil
        self.instance.user = self.user
        self.instance.save()

        self.partner = Partner(person=self.instance)
        self.partner.save()

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


class FullPartnerRegistrationForm(CombinedFormBase):
    form_classes = [PartnerRegistrationForm, BankAccountForm]
