from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView

from gatheros_event.forms import ProfileForm
from gatheros_event.views.mixins import AccountMixin


class ProfileView(AccountMixin, FormView):
    template_name = 'gatheros_event/profile.html'

    def get_form(self, form_class=None):
        return ProfileForm(
            user=self.request.user,
            password_required=False,
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Perfil atualizado com sucesso')
        return redirect('gatheros_event:profile')
