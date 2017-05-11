from threading import local

_user = local()
_session = local()
_user_context = local()


class CurrentSessionMiddleware(object):
    def process_request(self, request):
        _session.value = request.session


def get_current_session():
    return _session.value if hasattr(_session, 'value') else {}


class CurrentUserMiddleware(object):
    def process_request(self, request):
        _user.value = request.user


def get_current_user():
    return _user.value if hasattr(_user, 'value') else None


def get_current_user_id():
    current_user = get_current_user()
    return current_user.id if current_user else 0


class Organization(object):
    pk = None
    name = None
    internal = False
    group = None

    def __init__(self, pk, name, internal, group):
        self.pk = pk
        self.name = name
        self.internal = internal
        self.group = group


class Member(object):
    pk = None
    group = None
    group_name = None
    organization = None

    def __init__(self, pk, group, group_name, organization):
        self.pk = pk
        self.group = group
        self.group_name = group_name
        self.organization = Organization(**organization)


class UserContext(object):
    active_organization = None
    active_member_group = None
    organizations = []
    members = []
    superuser = False

    def __init__(self, session=None):
        if session:
            uc = session.get('user_context')
            if uc:
                active_org = Organization(**uc.get('active_organization'))
                active_member = Member(**uc.get('active_member_group'))
                self.active_organization = active_org
                self.active_member_group = active_member

                self.organizations = [
                    Organization(**dict_organization)
                    for dict_organization in uc.get('organizations', [])
                ]

                self.members = [
                    Member(**dict_member)
                    for dict_member in uc.get('members', [])
                ]

                self.superuser = uc.get('superuser', False)


class CurrentUserContextMiddleware(object):
    def process_request(self, request):
        user = request.user
        _user_context.value = UserContext(request.session) \
            if user.is_authenticated() else None


def get_user_context():
    uc = _user_context.value if hasattr(
        _user_context,
        'value'
    ) else None

    return UserContext() if not uc else uc
