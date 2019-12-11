# pylint: disable=C0103,E0611
"""
Formulário relacionados a Convites de Pessoas a serem membros de organizações
"""
from uuid import uuid4

import absoluteuri
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils import six
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from gatheros_event.models import Person, Organization, Member
from mailer.services import notify_new_user


class AccountCreateForm(forms.ModelForm):
    """ Formulário de criação de Perfil de pessoa no Gatheros. """
    email1 = forms.EmailField(
        label='E-mail',
        required=True,
        widget=forms.EmailInput,
    )
    email2 = forms.EmailField(
        label='Confirmar E-mail',
        required=True,
        widget=forms.EmailInput,
    )
    password1 = forms.CharField(
        label='Senha',
        required=True,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label='Confirmar senhar',
        required=True,
        widget=forms.PasswordInput,
    )

    user = None

    error_messages = {
        'email_mismatch': "Os dois e-mails informados não combinam",
        'password_mismatch': "Os dois passwords não combinam",
    }

    class Meta:
        """ Meta """
        model = Person
        fields = ['name']

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

    def clean_email1(self):
        email1 = self.data.get('email1')
        email2 = self.data.get('email2')

        if email1 and email2:
            email1 = email1.strip().lower()
            email2 = email2.strip().lower()
            if email1 != email2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch']
                )
        return email2

    def clean_password1(self):
        """ Limpa campo `password2` """
        password1 = self.data.get('password1')
        password2 = self.data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch']
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def clean(self):

        cleaned_data = super().clean()

        email = cleaned_data.get('email1')

        try:
            self.user = User.objects.get(username=email)

            if self.user.last_login:
                raise forms.ValidationError(
                    "Esse email já existe em nosso sistema. Tente novamente."
                )

            try:
                self.instance = self.user.person
            except AttributeError:
                pass

        except User.DoesNotExist:
            pass

        return cleaned_data

    def save(self, request, *args, **kwargs):

        email = self.cleaned_data.get('email1')
        self.instance.email = email

        super().save(*args, **kwargs)

        # Criando usuário
        if not self.user:
            self.user = User.objects.create_user(
                username=email,
                email=email,
            )

        self.user.set_password(self.cleaned_data.get('password1'))

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

        return self.instance
