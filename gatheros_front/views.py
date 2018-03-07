import absoluteuri
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
from gatheros_subscription.views.subscription import MySubscriptionsListView
from mailer.services import notify_set_password


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
        if 'show_captcha' in self.request.session \
                and self.request.session['show_captcha'] is True:
            form.add_captcha()

        return form

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_embeded'] = self.request.GET.get('embeded') == '1'
        return ctx

    def form_valid(self, form):
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
