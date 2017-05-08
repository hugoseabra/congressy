from django.contrib.auth.decorators import login_required
from django.forms.forms import BaseForm
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import View

from core.helper.account.middleware import get_current_session


class UserContext(object):
    user_context = {
        'active_organization': {'pk': None},
        'active_member_group': {'pk': None},
        'organizations': [],
        'members': [],
        'superuser': False,
    }


class UserContextViewMixin(UserContext, View):
    @method_decorator(login_required)
    @method_decorator(never_cache)
    def dispatch( self, request, *args, **kwargs ):
        if 'user_context' in request.session:
            self.user_context.update(request.session['user_context'])

        return super(UserContextViewMixin, self).dispatch(
            request,
            *args,
            **kwargs
        )


class UserContextFormMixin(UserContext, BaseForm):
    def __init__( self, *args, **kwargs ):
        self._populate_user_context()
        super(UserContextFormMixin, self).__init__(*args, **kwargs)

    def _populate_user_context( self ):
        session = get_current_session()
        if 'user_context' in session:
            self.user_context.update(session['user_context'])
