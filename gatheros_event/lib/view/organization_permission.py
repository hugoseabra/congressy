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


class OrganizationPermissionViewMixin(object):
    organization = None
    members = []
    organizations = []
    super_user = False
    member_group = None

    def check( self, request ):
        user = request.user
        self._retrieve_info_from_session(request.session)

        if user.is_superuser:
            self.super_user = True

    def get_organization_context(self):
        return {
            'organization': self.organization,
            'member_group': self.member_group,
            'super_user': self.super_user,
        }

    def _retrieve_info_from_session( self, session ):
        if 'organization_context' not in session:
            return

        self.organization = session['organization_context']
        self.organizations = session['organizations']
        self.members = session['members']
        self.member_group = session['member_group']
