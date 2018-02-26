from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from gatheros_front.forms import AuthenticationForm
from gatheros_subscription.views.subscription import MySubscriptionsListView


@login_required
def start(request):
    # org = account.get_organization(request)
    #
    # if org:
    #     if org.internal:
    #         return MySubscriptionsListView.as_view()(request)
    #
    #     return EventPanelView.as_view()(request, pk=org.pk)

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
