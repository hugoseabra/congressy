"""
Formulários de Organization
"""

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from core.forms import TelephoneInput, clean_phone as phone_cleaner
from gatheros_event.models import Member, Organization


class OrganizationForm(forms.ModelForm):
    """Formulário principal de evento"""

    user = None
    internal = False

    class Meta:
        model = Organization

        fields = (
            'name',
            'phone',
            'email',
            'description_html',
            'website',
            'facebook',
            'twitter',
            'linkedin',
            'skype',
        )

        widgets = {
            'description_html': CKEditorWidget(),
            'phone': TelephoneInput(attrs={'placeholder': '(99) 99999-9999'}),
            'email': forms.TextInput(
                attrs={'type': 'email',
                       'placeholder': 'me@you.com'}),
        }

    def __init__(self, user, internal=False, data=None, *args, **kwargs):
        self.user = user
        self.internal = internal

        try:
            self.user.person
        except ObjectDoesNotExist:
            raise IntegrityError(
                'Usuário não possui vínculo com pessoa, portanto, não é pode'
                ' ser um membro.'
            )

        instance = kwargs.get('instance')
        if instance and not instance.is_member(user):
            raise ValidationError({
                '__all__': 'Usuário não possui qualquer vínculo com a'
                           ' organização.'
            })

        super(OrganizationForm, self).__init__(data=data, *args, **kwargs)

        extra_required_fields = [
            'phone',
            'email',
        ]

        for field in extra_required_fields:
            self.fields[field].required = True

    def save(self, commit=True):
        """ Salva dados. """
        # noinspection PyProtectedMember
        is_new = self.instance._state.adding
        self.instance.internal = self.internal

        if is_new:
            self.instance.active = True

        result = super(OrganizationForm, self).save(commit=commit)
        if is_new:
            self.instance.members.create(
                person=self.user.person,
                group=Member.ADMIN
            )

        return result

    def clean_phone(self):

        cleaned_phone = phone_cleaner(self.cleaned_data.get('phone'))

        return cleaned_phone

    def clean_email(self):
        return self.data.get('email').lower()


class OrganizationManageMembershipForm(forms.Form):
    """ Formulário de gerenciamento de membros de organização. """
    organization = None

    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        super(OrganizationManageMembershipForm, self).__init__(*args, **kwargs)

    def deactivate(self, user):
        """ Desativa membro da organização. """
        member = self._get_member(user)
        member.active = False
        member.save()

    def activate(self, user):
        """ Ativa membro da organização. """
        member = self._get_member(user)
        member.active = True
        member.save()

    def delete(self, user):
        """ Remove membro da organização. """
        member = self._get_member(user)
        member.delete()

    def _get_member(self, user):
        try:
            return Member.objects.get(
                organization=self.organization,
                person=user.person
            )

        except Exception:
            raise Exception(
                'Não foi possível realizar cancelamento: membro `{}` não é da'
                ' organização `{}`.'.format(
                    user.get_full_name(),
                    self.organization.name
                )
            )


class OrganizationFinancialForm(forms.ModelForm):
    """Formulário principal de evento"""

    user = None
    internal = False

    class Meta:
        model = Organization
        fields = (
            'phone',
            'email',
            'bank_code',
            'agency',
            'agencia_dv',
            'account',
            'conta_dv',
            'legal_name',
            'cnpj_ou_cpf',
            'account_type',
        )

        widgets = {
            'phone': TelephoneInput(attrs={'placeholder': '(99) 99999-9999'}),
            'email': forms.TextInput(
                attrs={'type': 'email',
                       'placeholder': 'me@you.com'}),
        }


    def __init__(self, user, internal=False, data=None, *args, **kwargs):
        self.user = user
        self.internal = internal

        try:
            self.user.person
        except ObjectDoesNotExist:
            raise IntegrityError(
                'Usuário não possui vínculo com pessoa, portanto, não é pode'
                ' ser um membro.'
            )

        instance = kwargs.get('instance')
        if instance and not instance.is_member(user):
            raise ValidationError({
                '__all__': 'Usuário não possui qualquer vínculo com a'
                           ' organização.'
            })

        super(OrganizationFinancialForm, self).__init__(data=data, *args,
                                                        **kwargs)

        banking_required_fields = [
            'bank_code',
            'agency',
            'account',
            'cnpj_ou_cpf',
            'legal_name',
            'account_type',
        ]

        for field in banking_required_fields:
            self.fields[field].required = True

        extra_required_fields = [
            'phone',
            'email',
        ]

        for field in extra_required_fields:
            self.fields[field].required = True

    def save(self, commit=True):
        """ Salva dados. """
        # noinspection PyProtectedMember
        is_new = self.instance._state.adding
        self.instance.internal = self.internal

        if is_new:
            self.instance.active = True

        result = super(OrganizationFinancialForm, self).save(commit=commit)

        if is_new:
            self.instance.members.create(
                person=self.user.person,
                group=Member.ADMIN
            )

        return result

    def clean_phone(self):

        cleaned_phone = phone_cleaner(self.cleaned_data.get('phone'))

        return cleaned_phone

    def clean_email(self):
        return self.data.get('email').lower()
