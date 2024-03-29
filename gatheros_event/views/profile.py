import json
from urllib import (
    parse as urllib_parse,
    request as urllib_request,
)

import absoluteuri
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.shortcuts import redirect, render_to_response
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import FormView, TemplateView

from core.forms.cleaners import clear_string
from gatheros_event.forms import ProfileCreateForm, ProfileForm
from gatheros_event.views.mixins import AccountMixin
from mailer.services import notify_reset_password

LOGIN_SUPERUSER_ONLY = getattr(settings, 'LOGIN_SUPERUSER_ONLY', False)
ALLOW_ACCOUNT_REGISTRATION = getattr(settings, 'ACCOUNT_REGISTRATION', False)


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    post_reset_login = True
    post_reset_login_backend = 'django.contrib.auth.backends.ModelBackend'

    @auth_views.method_decorator(auth_views.sensitive_post_parameters())
    @auth_views.method_decorator(auth_views.never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        INTERNAL_RESET_URL_TOKEN = auth_views.INTERNAL_RESET_URL_TOKEN
        INTERNAL_RESET_SESSION_TOKEN = auth_views.INTERNAL_RESET_SESSION_TOKEN

        if self.user is not None:
            token = kwargs['token']
            if token == INTERNAL_RESET_URL_TOKEN:
                session_token = self.request.session.get(
                    INTERNAL_RESET_SESSION_TOKEN
                )
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(
                        token,
                        INTERNAL_RESET_URL_TOKEN
                    )
                    return redirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return render_to_response(
            template_name='registration/password_reset_fail.html',
            context=self.get_context_data()
        )


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

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()

        to_be_pre_cleaned = [
            'cpf',
            'phone',
            'zip_code',
            'institution_cnpj'
        ]

        for field in to_be_pre_cleaned:
            if field in request.POST:
                request.POST[field] = clear_string(request.POST[field])

        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['person'] = self.member.person
        return context


class ProfileCreateView(TemplateView, FormView):
    template_name = 'registration/register.html'
    success_url = reverse_lazy('front:start')
    messages = {
        'success': 'Sua conta foi criada com sucesso! '
                   'Enviamos um email para "%s", clique no link do email para'
                   ' ativar sua conta.'
    }

    def dispatch(self, request, *args, **kwargs):
        if LOGIN_SUPERUSER_ONLY is True or ALLOW_ACCOUNT_REGISTRATION is False:
            messages.warning(
                self.request,
                'Não é possível redefinir sua senha neste ambiente.'
            )
            return redirect('front:start')

        if request.user.is_authenticated:
            return redirect('front:start')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['GOOGLE_RECAPTCHA_PUBLIC_KEY'] = \
            settings.GOOGLE_RECAPTCHA_PUBLIC_KEY

        ctx['is_embeded'] = self.request.GET.get('embeded') == '1'
        return ctx

    def get_form(self, form_class=None):
        return ProfileCreateForm(
            **self.get_form_kwargs()
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            self.messages['success'] % form.cleaned_data["email"]
        )

        form.save(request=self.request)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        recaptcha_response = self.request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'

        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        data = urllib_parse.urlencode(values).encode()
        req = urllib_request.Request(url, data=data)
        response = urllib_request.urlopen(req)
        result = json.loads(response.read().decode())

        if 'success' not in result or result['success'] is not True:
            messages.error(
                self.request,
                'Informe que você não é um robô para criar uma conta.'
            )
            form = self.get_form()
            return super().form_invalid(form)

        return super().post(request, *args, **kwargs)

    def get_success_url(self):

        if settings.DEBUG is False:
            redirect_to = reverse_lazy('public:remarketing-redirect')
            marketing_type = '?marketing_type=adwords'
            page_type = '&page_type=new_account'
            next_page = '&next=' + super().get_success_url()

            return redirect_to + marketing_type + page_type + next_page

        return super().get_success_url()


class PasswordResetView(auth_views.PasswordResetView):
    title = 'Recuperar Conta'

    def dispatch(self, request, *args, **kwargs):

        if LOGIN_SUPERUSER_ONLY is True or ALLOW_ACCOUNT_REGISTRATION is False:
            messages.warning(
                self.request,
                'Não é possível criar conta neste ambiente.'
            )
            return redirect('front:start')

        if request.user.is_authenticated:
            return redirect('front:start')

        return super().dispatch(request, *args, **kwargs)

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
                    'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user)
                }
            )

            context = {
                'email': email,
                'url': url,
                'user': user,
                'site_name': Site.objects.get_current().domain

            }

            notify_reset_password(context=context)

        except User.DoesNotExist:
            pass

        return redirect(self.get_success_url())
