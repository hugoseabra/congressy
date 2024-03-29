import json
from urllib import (
    parse as urllib_parse,
    request as urllib_request,
)

import absoluteuri
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import Site
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic import TemplateView, View

from gatheros_front.forms import AuthenticationForm
from gatheros_subscription.views import MySubscriptionsListView
from mailer.services import notify_set_password

LOGIN_SUPERUSER_ONLY = getattr(settings, 'LOGIN_SUPERUSER_ONLY', False)
ALLOW_ACCOUNT_REGISTRATION = getattr(settings, 'ACCOUNT_REGISTRATION', False)


@login_required
def start(request):
    return MySubscriptionsListView.as_view()(request)


# noinspection PyClassHasNoInit
class Start(LoginRequiredMixin, TemplateView):
    template_name = 'gatheros_front/start.html'


# noinspection PyClassHasNoInit
class Login(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    form_class = AuthenticationForm

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # if 'show_captcha' in self.request.session \
        #         and self.request.session['show_captcha'] is True:
        #     form.add_captcha()

        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx['GOOGLE_RECAPTCHA_PUBLIC_KEY'] = \
            settings.GOOGLE_RECAPTCHA_PUBLIC_KEY

        ctx['allow_account_registration'] = \
            LOGIN_SUPERUSER_ONLY is False or ALLOW_ACCOUNT_REGISTRATION

        ctx['is_embeded'] = self.request.GET.get('embeded') == '1'
        if 'show_captcha' in self.request.session \
                and self.request.session['show_captcha'] is True:
            ctx['show_captcha'] = True
        return ctx

    def form_valid(self, form):

        # Recaptcha
        if 'show_captcha' in self.request.session \
                and self.request.session['show_captcha'] is True:

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

            if result['success']:

                return super().form_valid(form)

            else:
                return super().form_invalid(form)

        self.request.session['show_captcha'] = False
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        self.request.session['show_captcha'] = True
        return super().form_invalid(form)


class SetPasswordView(View):
    success_url = reverse_lazy('public:login')
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return redirect('front:start')

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        request.POST = request.POST.copy()
        email = request.POST.get('email')

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

            notify_set_password(context=context)
            messages.info(
                self.request,
                'Nós enviamos para seu email as instruções para '
                'definição de sua senha.'
            )

        except User.DoesNotExist:
            pass

        return redirect(self.success_url)
