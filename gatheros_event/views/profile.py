from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from gatheros_event.forms import ProfileCreateForm, ProfileForm
from gatheros_event.views.mixins import AccountMixin


class ProfileView(AccountMixin, FormView):
    template_name = 'gatheros_event/profile.html'
    messages = {
        'success': 'Perfil atualizado com sucesso'
    }

    def get_form(self, form_class=None):
        return ProfileForm(
            user=self.request.user,
            password_required=False,
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        form.save()
        messages.success(self.request, self.messages['success'])
        return redirect('event:profile')


class ProfileCreateView(TemplateView, FormView):
    template_name = 'gatheros_event/profile.html'
    messages = {
        'success': 'Informações registradas com sucesso, um email com '
                   'instruções foi enviado para "%s" click no link para '
                   'terminar o cadastro'
    }

    def get_form(self, form_class=None):
        return ProfileCreateForm(
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        form.save(request=self.request)

        messages.success(
            self.request,
            self.messages['success'] % form.cleaned_data["email"]
        )

        return redirect('event:profile')
