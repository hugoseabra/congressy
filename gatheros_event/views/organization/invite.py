from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.views.decorators.csrf import get_token
from django.views.generic import FormView, TemplateView

from gatheros_event.forms import (
    InvitationCreateForm,
    InvitationDecisionForm,
    ProfileForm
)
from gatheros_event.models import Invitation
from gatheros_event.views.mixins import AccountMixin


class InvitationCreateView(AccountMixin, FormView):
    template_name = 'gatheros_event/organization/invitation-create.html'
    success_url = reverse_lazy(
        'gatheros_event:invitation-success'
    )

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(InvitationCreateView, self).dispatch(
            request,
            *args,
            **kwargs
        )
        if not self._can_view():
            if self.organization.internal:
                messages.warning(request, 'Você não está em uma organização.')
                return redirect(reverse_lazy('gatheros_front:start'))
            else:
                messages.warning(request, 'Você não pode realizar esta ação.')
                return redirect(reverse_lazy(
                    'gatheros_event:organization-panel'
                ))

        return dispatch

    def get_initial(self):
        """
        Valores iniciais para os campos do form
        :return:
        """
        return {
            'organization': self.request.GET.get('organization', None)
        }

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

        return super(InvitationCreateView, self).form_valid(form)

    def _can_view(self):
        not_internal = self.organization.internal is False
        can_view = self.request.user.has_perm(
            'gatheros_event.can_invite',
            self.organization
        )
        return not_internal and can_view


class InvitationCreateSuccessView(AccountMixin, TemplateView):
    template_name = 'gatheros_event/organization/' \
                    'invitation-create-success.html'


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

        # Se tem perfil, precisa do login login
        if not request.user.is_authenticated() \
                and hasattr(invite.to, 'person'):
            return redirect('gatheros_front:login')

        # Se o usuário autenticado for diferente do usuário do convite
        if request.user.is_authenticated() \
                and not request.user == invite.to:
            messages.error(request, "Usuário do convite é diferente do logado")
            context.update({
                'messages': messages.get_messages(request)
            })
            return render_to_response(
                'gatheros_event/organization/invitation-decision.html',
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
            'gatheros_event/organization/invitation-decision.html',
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
        form = InvitationDecisionForm(instance=invite)
        form.is_valid()

        if 'invitation_decline' in request.POST:
            form.decline()
            return render_to_response(
                'gatheros_event/organization/invitation-decline.html',
                # context
            )

        elif 'invitation_accept' in request.POST:
            try:
                # Se der tudo certo no aceite, redireciona para painel
                form.accept()
                return redirect('gatheros_event:organization-panel')
            except ValidationError:
                # Se errado direciona para a criação do perfil
                return redirect(
                    'gatheros_event:invitation-profile',
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
            'form': ProfileForm(
                user=context['invite'].to,
                initial={
                    'email': context['invite'].to.email
                }
            ),
        })

        return render_to_response(
            'gatheros_event/organization/invitation-profile.html',
            context
        )

    def post(self, request, **kwargs):
        """
        Cria o perfil e aceita o convite
        """
        context = self.get_context_data(**kwargs)
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
                'gatheros_event/organization/invitation-profile.html',
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
            return redirect('gatheros_event:organization-panel')
        except ValidationError:
            raise ValidationError(
                "Algo errado ocorreu e não foi possível aceitar o "
                "convite, apos salvar o perfil. Contate o suporte técnico"
            )
