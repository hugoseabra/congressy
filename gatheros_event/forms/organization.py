"""
Formulários de Organization
"""

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError

from gatheros_event.models import Member, Organization


class OrganizationForm(forms.ModelForm):
    """Formulário principal de evento"""

    user = None
    internal = False

    class Meta:
        model = Organization
        # fields = (
        #     'name',
        #     'description_html',
        #     'avatar',
        #     'website',
        #     'facebook',
        #     'twitter',
        #     'linkedin',
        #     'skype',
        # )

        fields = (
            'name',
            'description_html',
            'website',
            'facebook',
            'twitter',
            'linkedin',
            'skype',
        )

        widgets = {
            'description_html': CKEditorWidget(),
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
            'bank_code',
            'agency',
            'agencia_dv',
            'account',
            'conta_dv',
            'legal_name',
            'cnpj_ou_cpf',
            'account_type',
        )

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

        super(OrganizationFinancialForm, self).__init__(data=data, *args, **kwargs)

        banking_required_fields = ['bank_code', 'agency', 'account', 'cnpj_ou_cpf', 'account_type']

        for field in banking_required_fields:
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

    # def clean(self):
    #
    #     cleaned_data = super(OrganizationFinancialForm, self).clean()
    #
    #     bank_account = create_payme_back_account(cleaned_data)
    #
    #     message = None
    #
    #     try:
    #         if bank_account:
    #             message = bank_account[0]['message']
    #     except KeyError:
    #         pass
    #
    #     if message:
    #
    #         if message == 'Invalid format':
    #
    #             parameter_name = bank_account[0]['parameter_name']
    #
    #             if parameter_name == 'document_number':
    #                 parameter_name = 'cnpj_ou_cpf'
    #
    #             self.add_error(parameter_name, ValidationError('Formato de CPF ou CNPJ invalido'))
    #     else:
    #
    #         organization = self.instance
    #
    #         organization.active_bank_account = True
    #         organization.bank_account_id = bank_account['id']
    #         organization.document_type = bank_account['document_type']
    #         organization.charge_transfer_fees = bank_account['charge_transfer_fees']
    #         organization.date_created = bank_account['date_created']
    #
    #         recipient = create_payme_recipient(bank_account)
    #
    #         organization.active_recipient = True
    #         organization.recipient_id = recipient['id']
    #
    #     return cleaned_data






