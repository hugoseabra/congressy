# pylint: disable=C0103,E0611
"""
Formulário relacionados a Convites de Pessoas a serem membros de organizações
"""
from uuid import uuid4

import absoluteuri
from django import forms
from django.contrib.auth import (
    password_validation,
)
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from core.forms.widgets import AjaxChoiceField, TelephoneInput
from core.util import create_years_list
from gatheros_event.models import Person, Organization, Member
from mailer.services import notify_new_user


class ProfileCreateForm(forms.ModelForm):
    """ Formulário de criação de Perfil de pessoa no Gatheros. """
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))

    user = None

    class Meta:
        """ Meta """
        model = Person
        fields = ['name', 'email']

    # def __init__(self, **kwargs):
    #
    #     data = kwargs.get('data')
    #
    #     # Buscar se person existe
    #     if data:
    #         try:
    #             person = Person.objects.get(
    #                 email=data.get('email')
    #             )
    #
    #             kwargs['instance'] = person
    #
    #         except Person.DoesNotExist:
    #             pass
    #
    #     super().__init__(**kwargs)

    def save(self, domain_override=None, request=None,
             subject_template='registration/account_confirmation_subject.txt',
             email_template='registration/account_confirmation_email.html'):
        """
        Cria uma conta no sistema

        :param domain_override:
        :param request:
        :param subject_template:
        :param email_template:
        :return:
        """
        # Criando perfil
        # try:
        #     person = Person.objects.get(email=self.cleaned_data["email"])
        #     self.instance = person
        # except Person.DoesNotExist:
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

        if not self.instance.members.count():
            org = Organization(internal=False, name=self.instance.name)

            for attr, value in six.iteritems(self.instance.get_profile_data()):
                setattr(org, attr, value)

            org.save()

            Member.objects.create(
                organization=org,
                person=self.instance,
                group=Member.ADMIN
            )

        # Criando o email de confirmação e definição de senha
        reset_form = PasswordResetForm(
            data={
                'email': self.cleaned_data["email"]
            }
        )
        reset_form.is_valid()

        """
        Generates a one-use only link for resetting password and sends via
        e-mail to the
        user.
        """

        email = self.cleaned_data["email"]
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        url = absoluteuri.reverse(
            'password_reset_confirm',
            kwargs={
                'uidb64': uid,
                'token': token,
            }
        )

        context = {
            'email': email,
            'url': url,
            'site_name': get_current_site(request)
        }

        notify_new_user(context)

        # reset_form.save(
        #     domain_override=domain_override,
        #     subject_template_name=subject_template,
        #     email_template_name=email_template,
        #     request=request,
        # )

        return self.instance

    def clean_name(self):
        try:
            split_name = self.data.get('name').strip().split(' ')
            # array clean
            split_name = list(filter(None, split_name))

            if not split_name or len(split_name) == 1:
                raise Exception()

            first = split_name[0].strip()
            surnames = [n.strip() for n in split_name[1:]]

            return '{} {}'.format(first, ' '.join(surnames))

        except Exception:
            raise forms.ValidationError(
                'Você precisa informar o seu nome e sobrenome.'
            )

    def clean_email(self):
        return self.data.get('email').lower()

    def clean(self):

        cleaned_data = super(ProfileCreateForm, self).clean()

        email = cleaned_data.get('email')

        try:
            self.user = User.objects.get(username=email)

            if self.user.last_login:
                raise forms.ValidationError(
                    "Esse email já existe em nosso sistema. Tente novamente.")

            try:
                self.instance = self.user.person
            except AttributeError:
                pass

        except User.DoesNotExist:
            pass

        return cleaned_data


class ProfileForm(forms.ModelForm):
    """
    Pessoas que são usuários do sistema
    """

    states = (
        ('', '----'),
        # replace the value '----' with whatever you want, it won't matter
        ("AC", "Acre"),
        ("AL", "Alagoas"),
        ("AP", "Amapá"),
        ("AM", "Manaus"),
        ("BA", "Bahia"),
        ("CE", "Ceará"),
        ("DF", "Distrito Federal"),
        ("ES", "Espírito Santo"),
        ("GO", "Goiás"),
        ("MA", "Maranhão"),
        ("MT", "Mato Grosso"),
        ("MS", "Mato Grosso do Sul"),
        ("MG", "Minas Gerais"),
        ("PA", "Pará"),
        ("PB", "Paraíba"),
        ("PR", "Paraná"),
        ("PE", "Pernambuco"),
        ("PI", "Piauí"),
        ("RJ", "Rio de Janeiro"),
        ("RN", "Rio Grande do Norte"),
        ("RS", "Rio Grande do Sul"),
        ("RO", "Rondônia"),
        ("RR", "Roraima"),
        ("SC", "Santa Catarina"),
        ("SP", "São Paulo"),
        ("SE", "Sergipe"),
        ("TO", "Tocantins"),
    )
    empty = (
        ('', '----'),
    )

    state = forms.ChoiceField(label='Estado', choices=states, required=False)
    city_name = AjaxChoiceField(label='Cidade', choices=empty, required=False)
    email = forms.EmailField(label='E-Mail')

    error_messages = {
        'password_mismatch': "Os dois passwords não combinam",
    }
    new_password1 = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput,
        required=False
    )
    new_password2 = forms.CharField(
        label="Confirmar Senha",
        strip=False,
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        """ Meta """
        model = Person
        fields = ['name', 'email', 'new_password1', 'new_password2',
                  'gender', 'birth_date', 'zip_code', 'phone', 'city', 'cpf',
                  'street', 'number', 'complement', 'village', 'institution',
                  'institution_cnpj', 'function']

        widgets = {
            # CPF como telefone para aparecer como número no mobile
            'cpf': TelephoneInput(),
            'name': forms.TextInput(attrs={'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'me@you.com'}),
            'phone': TelephoneInput(attrs={'placeholder': '(00) 00000-0000'}),
            'zip_code': TelephoneInput(),
            'city': forms.HiddenInput(),
            'birth_date': forms.SelectDateWidget(
                attrs=({'style': 'width: 30%; display: inline-block;'}),
                years=create_years_list(), ),
        }

    def __init__(self, user, password_required=True, *args, **kwargs):
        if hasattr(user, 'person'):
            kwargs.update({'instance': user.person})

        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user

        self.fields['email'].widget.attrs['disabled'] = 'disabled'
        self.fields['email'].disabled = True

        self.fields['new_password1'].required = password_required
        self.fields['new_password2'].required = password_required

    def clean_new_password2(self):
        """ Limpa campo `password2` """
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, **_):
        """ Salva dados. """
        super(ProfileForm, self).save(commit=True)

        self.user.is_active = True
        if self.cleaned_data["new_password1"]:
            self.user.set_password(self.cleaned_data["new_password1"])
        self.user.save()

        self.instance.user = self.user
        self.instance.save()

        return self.instance
