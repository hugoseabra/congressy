from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.forms import BaseForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import View

from core.helper.account.middleware import get_user_context


class UserContextViewMixin(LoginRequiredMixin, View):
    user_context = None

    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.user_context = get_user_context()

        return super(UserContextViewMixin, self).dispatch(
            request,
            *args,
            **kwargs
        )


class UserContextFormMixin(BaseForm):
    user_context = None

    def __init__(self, *args, **kwargs):
        self.user_context = get_user_context()
        super(UserContextFormMixin, self).__init__(*args, **kwargs)
