# pylint: disable=C0103,E0611
"""
Formulário relacionados a Convites de Pessoas a serem membros de organizações
"""
import absoluteuri
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from gatheros_event.models import Invitation, Member
from gatheros_event.models.rules import check_invite
from mailer.services import notify_invite


def send_invitation(invitation):
    """ Envia convite para e-mail de convidado(s) """

    url = absoluteuri.reverse('public:invitation-decision', kwargs={
        'pk': invitation.pk
    })

    notify_invite(
        invitation.author.organization.name,
        url,
        invitation.author.person.name,
        invitation.to.first_name,
        invitation.to.email
    )


class InvitationCreateForm(forms.Form):
    """Formulário de criação de Convite"""
    to = forms.EmailField()
    organization = forms.HiddenInput()

    user = None
    _invites = None

    def __init__(self, user, data=None, *args, **kwargs):
        super(InvitationCreateForm, self).__init__(data=data, *args, **kwargs)

        self.user = user
        self._invites = []

    def clean(self):
        """ Limpa campos. """
        if self.errors:
            return []

        email = self.cleaned_data['to']
        organization = self.initial.get('organization')
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
        """ Notifica pessoa convidada """
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

    class Meta:
        """ Meta """
        model = Invitation
        exclude = []

    def accept(self):
        """ Aceita o convite e criar o membro """
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
        """ Recusa o convite """
        self.instance.delete()
