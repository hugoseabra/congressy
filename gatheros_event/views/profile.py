import absoluteuri
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import FormView, TemplateView

from gatheros_event.forms import ProfileCreateForm, ProfileForm
from gatheros_event.views.mixins import AccountMixin
from mailer.services import notify_reset_password


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
        'success': 'Sua conta foi criada com sucesso! '
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

        return redirect('front:start')


class PasswordResetView(auth_views.PasswordResetView):
    def form_valid(self, form):
        """
           Generates a one-use only link for resetting password and sends to the
           user.
        """

        email = form.cleaned_data["email"]

        try:
            user = User.objects.get(email=email)

            url = absoluteuri.reverse(
                'password_reset_confirm',
                kwargs={
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                }
            )

            context = {
                'email': email,
                'url': url,
                'user': user,

            }

            notify_reset_password(context=context)

        except User.DoesNotExist:
            pass

        return super().form_valid(form)
