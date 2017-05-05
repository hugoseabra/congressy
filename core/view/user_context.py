from django.views.generic.base import View

"""
Verifica credenciais de membro de usuário dentro da organização. 

USE:
1. Mixin da view
> class MyView(TemplateView, OrganizationPermissionViewMixin):

2. Para carregar as informações, use check() no dispatch() da View
>    def dispatch(self, request, *args, **kwargs):
>       super(MyView, self).dispatch(request, *args, **kwargs)
>       self.check(request.user)

"""


class UserContextMixin(View):
    organization = None
    members = []
    organizations = []
    super_user = False
    member_group = None
    user_context = {
        'active_organization': None,
        'active_member_group': None,
        'superuser': False,
    }

    def dispatch( self, request, *args, **kwargs ):
        if 'user_context' in request.session:
            self.user_context.update(request.session['user_context'])

        return super(UserContextMixin, self).dispatch(request, *args, **kwargs)
