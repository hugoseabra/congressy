from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.urls import reverse_lazy
from django.views.decorators.csrf import get_token
from django.views.generic import FormView, TemplateView, View

from gatheros_event.forms import InvitationCreateForm, InvitationDecisionForm
from gatheros_event.models import Invitation
from gatheros_event.views.mixins import AccountMixin


class InvitationCreateView(AccountMixin, FormView):
    template_name = 'gatheros_event/organization/invitation-create.html'
    success_url = reverse_lazy(
        'gatheros_event:invitation-success'
    )

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
                    pk= kwargs.get('pk')
                )

        else:
            raise ValidationError(
                "Os valores de parametros devem ser: "
                "'invitation_decline' ou 'invitation_decline'"
            )


class InvitationProfileView(View):
    def get(self, request, **kwargs):
        from django.http.response import HttpResponse
        return HttpResponse('Terminar perfil de usuário')
