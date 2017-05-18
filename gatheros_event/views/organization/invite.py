from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from gatheros_event.forms import InvitationForm
from gatheros_event.views.mixins import AccountMixin


class OrganizationPanelView(AccountMixin, TemplateView):
    template_name = 'gatheros_event/organization/invite.html'


class InviteView(FormView):
    template_name = 'gatheros_event/organization/invite.html'

    # form_class = InvitationForm
    # success_url = '/thanks/'

    def get_form(self, form_class=None):
        """
        Retorna uma instancia de form para ser usada na view
        """
        kwargs = self.get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return InvitationForm(**kwargs)

    def form_valid(self, form):
        """
        No post executa este método se o form for válido

        :param form:
        :return:
        """
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_invite()
        return super(InviteView, self).form_valid(form)
