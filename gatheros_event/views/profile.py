from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import FormView, TemplateView

from gatheros_event.forms import ProfileCreateForm, ProfileForm
from gatheros_event.views.mixins import AccountMixin


class ProfileView(AccountMixin, FormView):

    template_name = 'profile/form.html'
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
    template_name = 'registration/register.html'
    messages = {
        'success': 'Sua conta foi criada com sucesso! git a'
                   'Enviamos um email para "%s", click no link do email para ativar sua conta.'
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
