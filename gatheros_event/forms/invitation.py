# pylint: disable=C0103,E0611
"""
Formulário relacionados a Convites de Pessoas a serem membros de organizações
"""

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import reverse

from core.fields import MultiEmailField
from gatheros_event.models import Invitation, Member
from gatheros_event.models.rules import check_invite


def send_invitation(invitation):
    url = reverse(
        'event:invitation-decision',
        kwargs={'pk': str(invitation.pk)}
    )

    send_mail(
        'Novo convite para organização',
        'Para aceitar clique no link: {0}'.format(url),
        settings.DEFAULT_FROM_EMAIL,
        [invitation.to.email]
    )


class InvitationCreateForm(forms.Form):
    """Formulário de criação de Convite"""
    to = MultiEmailField(label='Emails')
    organization = forms.HiddenInput()

    user = None
    _invites = None

    def __init__(self,  user, data=None, *args, **kwargs):
        super(InvitationCreateForm, self).__init__(data=data, *args, **kwargs)

        self.user = user
        self._invites = []

    def clean(self):
        if self.errors:
            return []

        organization = self.initial.get('organization')

        # Cria os convites
        for email in self.cleaned_data['to']:
            invited_user, _ = User.objects.get_or_create(
                username=email,
                defaults={'email': email}
            )
            invite = Invitation(
                author=organization.get_member(person=self.user),
                to=invited_user,
                group=Member.HELPER
            )

            # Submete os convites as regras
            check_invite(invite)

            # Adiciona na lista dos convites que estão ok
            self._invites.append(invite)

    def send_invite(self):
        """Notifica pessoa convidada"""
        for invite in self._invites:
            # Convite para um tipo inicialmente.
            invite.group = Member.HELPER
            invite.to.save()
            invite.save()

            send_invitation(invite)


class InvitationDecisionForm(forms.ModelForm):
    """
    Decide o resultado de um convite e suas implicações
    """

    def accept(self):
        """
        Aceita o convite e criar o membro

        :return:
        """
        user = self.instance.to

        # Se não tiver um perfil de pessoa vinculado não permite aceitar
        if not hasattr(user, 'person'):
            raise ValidationError('Usuário não tem perfil de pessoa')

        # Cria membro
        Member.objects.create(
            organization=self.instance.author.organization,
            person=user.person,
            group=self.instance.group
        )

        # Remove o convite que não é mais necessário
        self.instance.delete()

    def decline(self):
        """
        Recusa o convite
        :return:
        """
        self.instance.delete()

    class Meta:
        model = Invitation
        exclude = []
