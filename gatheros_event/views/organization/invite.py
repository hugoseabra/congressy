from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from gatheros_event.forms import InvitationForm
from gatheros_event.views.mixins import AccountMixin


class InviteView(AccountMixin, FormView):
    template_name = 'gatheros_event/organization/invite.html'
    success_url = reverse_lazy('gatheros_event:organization-invite-success')

    def get_form(self, form_class=None):
        """
        Retorna uma instancia de form para ser usada na view
        """
        return InvitationForm(user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        """
        No post executa este método se o form for válido

        :param form:
        :return: HttpResponseRedirect
        """
        form.send_invite()
        return super(InviteView, self).form_valid(form)


class InviteSuccessView(AccountMixin, TemplateView):
    template_name = 'gatheros_event/organization/invite-success.html'


class InviteAcceptView(AccountMixin, FormView):
    template_name = 'gatheros_event/organization/invite-accept.html'
