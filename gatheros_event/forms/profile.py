# pylint: disable=C0103,E0611
"""
Formulário relacionados a Convites de Pessoas a serem membros de organizações
"""
from uuid import uuid4

from django import forms
from django.contrib.auth import (
    password_validation,
)
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.utils import six
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from gatheros_event.models import Person, Organization, Member
from mailer.services import notify_new_user


class ProfileCreateForm(forms.ModelForm):
    """ Formulário de criação de Perfil de pessoa no Gatheros. """
    email = forms.EmailField(label='E-mail', widget=forms.EmailInput(
        attrs={'class': 'form-control'}
    ))

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
        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            password=str(uuid4())
        )
        user.save()

        # Vinculando usuário ao perfil
        self.instance.user = user
        self.instance.save()

        try:
            self.instance.members.get(organization__internal=True)
        except Member.DoesNotExist:
            internal_org = Organization(
                internal=True,
                name=self.instance.name
            )

            for attr, value in six.iteritems(self.instance.get_profile_data()):
                setattr(internal_org, attr, value)

            internal_org.save()

            Member.objects.create(
                organization=internal_org,
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
        Generates a one-use only link for resetting password and sends via e-mail to the
        user.
        """

        email = self.cleaned_data["email"]

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'email': email,
            'domain': domain,
            'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'protocol': 'https',
        }

        notify_new_user(context)

        # reset_form.save(
        #     domain_override=domain_override,
        #     subject_template_name=subject_template,
        #     email_template_name=email_template,
        #     request=request,
        # )

        return self.instance

    def clean(self):

        cleaned_data = super(ProfileCreateForm, self).clean()

        email = cleaned_data.get('email')

        try:
            User.objects.get(username=email)
            raise forms.ValidationError("Esse email já existe em nosso sistema. Tente novamente.")
        except User.DoesNotExist:
            pass

        return cleaned_data


class ProfileForm(forms.ModelForm):
    """
    Pessoas que são usuários do sistema
    """
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
        fields = ['name', 'email', 'phone', 'new_password1', 'new_password2']
        # exclude = [
        #     'user',
        #     'synchronized',
        #     'term_version',
        #     'politics_version',
        # ]

    def __init__(self, user, password_required=True, *args, **kwargs):
        if hasattr(user, 'person'):
            kwargs.update({'instance': user.person})

        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user

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
