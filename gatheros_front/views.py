from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

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
