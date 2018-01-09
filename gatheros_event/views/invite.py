from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import get_token
from django.views.generic import FormView, ListView, TemplateView, UpdateView

from gatheros_event.forms import (
    InvitationCreateForm,
    InvitationDecisionForm,
    ProfileForm
)
from gatheros_event.forms.invitation import send_invitation
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Invitation, Organization
from gatheros_event.views.mixins import AccountMixin, DeleteViewMixin


class InvitationListView(AccountMixin, ListView):
    model = Invitation
    template_name = 'invitation/list.html'
    invitation_organization = None
    context_object_name = 'open_invitations'

    def get_context_data(self, **kwargs):
        context = super(InvitationListView, self).get_context_data(**kwargs)
        context['invitation_organization'] = self.get_invitation_organization()

        open_list = [item for item in self.object_list if not item.is_expired]
        expired_list = [item for item in self.object_list if item.is_expired]

        context['open_invitations'] = open_list
        context['expired_invitations'] = expired_list

        context['can_view_members'] = self._can_view_members()
        context['can_manage_members'] = self._can_manage_members()

        return context

    def dispatch(self, request, *args, **kwargs):
        if not self._can_view():
            if self.organization.internal:
                messages.warning(request, 'Você não pode acessar esta área.')
                return redirect(reverse_lazy('front:start'))
            else:
                org = self.get_invitation_organization()
                messages.warning(request, 'Você não pode realizar esta ação.')
                return redirect(reverse(
                    'event:organization-panel',
                    kwargs={'pk': org.pk}
                ))

        return super(InvitationListView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    def get_queryset(self):
        query_set = super(InvitationListView, self).get_queryset()
        organization = self.get_invitation_organization()

        return query_set.filter(author__organization=organization).distinct()

    def get_invitation_organization(self):
        if self.invitation_organization:
            return self.invitation_organization

        self.invitation_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.invitation_organization

    def _can_view(self):
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_invite',
            self.get_invitation_organization()
        )
        return self.is_manager and can_manage

    def _can_view_members(self):
        return self.request.user.has_perm(
            'gatheros_event.can_view_members',
            self.get_invitation_organization()
        )

    def _can_manage_members(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_members',
            self.get_invitation_organization()
        )


class InvitationCreateView(AccountMixin, FormView):
    template_name = 'invitation/invitation-create.html'
    invitation_organization = None

    def get_permission_denied_url(self):
        return reverse(
            'event:organization-panel',
            kwargs={'pk': self.kwargs.get('organization_pk')}
        )

    def get_context_data(self, **kwargs):
        context = super(InvitationCreateView, self).get_context_data(**kwargs)
        context['invitation_organization'] = self.get_invitation_organization()

        context['can_view_members'] = self._can_view_members()
        context['can_manage_members'] = self._can_manage_members()

        return context

    def get_initial(self):
        """
        Valores iniciais para os campos do form
        :return:
        """
        initial = super(InvitationCreateView, self).get_initial()
        initial.update({
            'organization': self.get_invitation_organization()
        })
        return initial

    def get_form(self, form_class=None):
        """
        Retorna uma instancia de form para ser usada na view
        """
        return InvitationCreateForm(
            user=self.request.user,
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        """
        No post executa este método se o form for válido

        :param form:
        :return: HttpResponseRedirect
        """
        form.send_invite()
        messages.success(self.request, 'Convite(s) enviado(s) com sucesso.')
        return super(InvitationCreateView, self).form_valid(form)

    def get_invitation_organization(self):
        if self.invitation_organization:
            return self.invitation_organization

        self.invitation_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.invitation_organization

    def get_success_url(self):
        return reverse('event:invitation-list', kwargs={
            'organization_pk': self.get_invitation_organization().pk
        })

    def can_access(self):
        return self.request.user.has_perm(
            'gatheros_event.can_invite',
            self.get_invitation_organization()
        )

    def _can_view_members(self):
        return self.request.user.has_perm(
            'gatheros_event.can_view_members',
            self.get_invitation_organization()
        )

    def _can_manage_members(self):
        return self.request.user.has_perm(
            'gatheros_event.can_manage_members',
            self.get_invitation_organization()
        )


class InvitationResendView(UpdateView):
    """ Reenvio de convite previamente existente. """

    model = Invitation
    invitation_organization = None

    def dispatch(self, request, *args, **kwargs):
        if not self._can_view():
            messages.warning(request, 'Você não pode realizar esta ação.')
            org = self.get_invitation_organization()
            return redirect(reverse(
                'event:organization-panel',
                kwargs={'pk': org.pk}
            ))

        return super(InvitationResendView, self).dispatch(
            request,
            *args,
            **kwargs
        )

    # noinspection PyMethodMayBeStatic
    def post(self, request, **kwargs):
        """
        Processa reenvio de convite
        :param request:
        :param kwargs:
        :return:
        """
        if self.object.is_expired:
            self.object.renew(save=True)
            send_invitation(self.object)
            messages.success(request, 'Convite renovado com sucesso.')
        else:
            messages.success(
                request,
                'O convite não está expirado e não precisa ser renovado.'
            )

        return redirect(reverse('event:invitation-list', kwargs={
            'organization_pk': self.object.author.organization_id
        }))

    def get_invitation_organization(self):
        if self.invitation_organization:
            return self.invitation_organization

        self.invitation_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.invitation_organization

    def _can_view(self):
        self.object = self.get_object()
        org = self.get_invitation_organization()

        same_org = org.pk == self.object.author.organization.pk

        can_delete = self.request.user.has_perm(
            'gatheros_event.can_invite',
            org
        )

        return same_org and can_delete


class InvitationDecisionView(TemplateView):
    def get(self, request, **kwargs):
        """
        Exibe form de decisão
        :param request:
        :param kwargs:
        :return:
        """
        invite = get_object_or_404(Invitation, pk=kwargs.get('pk'))
        context = self.get_context_data(**kwargs)
        context.update({'request': request})

        authenticated = request.user.is_authenticated()

        # Se tem perfil, precisa do login login
        if not authenticated and hasattr(invite.to, 'person'):
            return redirect('public:login')

        # Se o usuário autenticado for diferente do usuário do convite
        if authenticated and not request.user == invite.to:
            messages.error(request, "Usuário do convite é diferente do logado")
            context.update({
                'messages': messages.get_messages(request)
            })
            return render_to_response(
                'invitation/invitation-decision.html',
                context
            )

        # Se não estiver logado e se o usuário convidado não tem perfil
        context.update({
            'csrf_token': get_token(request),
            'messages': messages.get_messages(request),
            'author': invite.author,
            'organization': invite.author.organization
        })

        return render_to_response(
            'invitation/invitation-decision.html',
            context
        )

    # noinspection PyMethodMayBeStatic
    def post(self, request, **kwargs):
        """
        Trata a ação de Aceitar ou Recusar o Convite
        :param request:
        :param kwargs:
        :return:
        """

        invite = get_object_or_404(Invitation, pk=kwargs.get('pk'))
        org_id = invite.author.organization_id
        form = InvitationDecisionForm(instance=invite)
        form.is_valid()

        context = self.get_context_data(**kwargs)
        context.update({'request': request})
        context.update({'organization': invite.author.organization})

        if 'invitation_decline' in request.POST:
            form.decline()
            return render_to_response(
                'invitation/invitation-decline.html',
                context
            )

        elif 'invitation_accept' in request.POST:
            try:
                # Se der tudo certo no aceite, redireciona para painel
                form.accept()

                # Atualização contexto de organizações
                update_account(request=self.request, force=True)

                return redirect('event:organization-panel', pk=org_id)
            except ValidationError:
                # Se errado direciona para a criação do perfil
                return redirect(
                    'public:invitation-profile',
                    pk=kwargs.get('pk')
                )

        else:
            raise ValidationError(
                "Os valores de parametros devem ser: "
                "'invitation_decline' ou 'invitation_decline'"
            )


class InvitationProfileView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(InvitationProfileView, self).get_context_data(**kwargs)

        invite = get_object_or_404(Invitation, pk=kwargs.get('pk'))

        context.update({
            'invite': invite,
            'csrf_token': get_token(self.request),
            'request': self.request,
            'author': invite.author,
            'organization': invite.author.organization,
        })

        return context

    def get(self, request, **kwargs):
        """
        Exibe form de decisão
        :param request:
        :param kwargs:
        :return:
        """
        context = self.get_context_data(**kwargs)

        # Se não estiver logado e se o usuário convidado não tem perfil
        context.update({
            'request': request,
            'form': ProfileForm(
                user=context['invite'].to,
                initial={
                    'email': context['invite'].to.email
                }
            ),
        })

        return render_to_response(
            'invitation/invitation-profile.html',
            context
        )

    def post(self, request, **kwargs):
        """
        Cria o perfil e aceita o convite
        """
        context = self.get_context_data(**kwargs)
        context.update({'request': request})

        invite = context.get('invite')

        # Cria os forms que fazem parte do post
        form = ProfileForm(user=invite.to, data=request.POST)

        # Verifica erros no form
        if not form.is_valid():
            context.update({
                'messages': messages.get_messages(self.request),
                'form': form,
            })
            return render_to_response(
                'invitation/invitation-profile.html',
                context
            )

        # Salva o form
        form.save()

        # Aceitar o convite
        invite_form = InvitationDecisionForm(instance=invite)
        invite_form.is_valid()

        # Deve conseguir aceitar o convite corretamente
        try:
            invite_form.accept()

            # Atualização contexto de organizações
            update_account(request=self.request, force=True)

            return redirect(reverse(
                'event:organization-panel',
                kwargs={'pk': invite.author.organization_id}
            ))
        except ValidationError:
            raise ValidationError(
                "Algo errado ocorreu e não foi possível aceitar o "
                "convite, apos salvar o perfil. Contate o suporte técnico"
            )


class InvitationDeleteView(DeleteViewMixin):
    model = Invitation
    success_message = 'Convite excluído com sucesso.'
    invitation_organization = None

    def get_invitation_organization(self):
        if self.invitation_organization:
            return self.invitation_organization

        self.invitation_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.invitation_organization

    def get_success_url(self):
        org = self.get_invitation_organization()
        return reverse('event:invitation-list', kwargs={
            'organization_pk': org.pk
        })


class MyInvitationsListView(AccountMixin, ListView):
    """ Lista de inscrições """

    model = Invitation
    template_name = 'invitation/my_invitations.html'
    ordering = ('created', 'author__person__name', '-expired',)

    def get_permission_denied_url(self):
        return reverse('front:start')

    def get_queryset(self):
        query_set = super(MyInvitationsListView, self).get_queryset()
        return query_set.filter(
            to=self.request.user,
            expired__gt=datetime.now(),
        )
