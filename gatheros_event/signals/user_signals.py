from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in, sender=User)
def add_organization_info( user, request, **_ ):
    if request.path == '/admin/login/' or not hasattr(user, 'person'):
        return

    organizations = []
    members = []
    selected_org = {}
    select_member = {}
    for member in user.person.members \
            .filter(organization__active=True) \
            .order_by('-organization__internal', 'organization__name'):
        organization = member.organization
        org_data = {
            'pk': organization.pk,
            'name': organization.name,
            'internal': organization.internal,
        }

        member_data = {
            'organization': org_data,
            'group_name': member.get_group_display(),
            'group': member.group
        }

        if organization.internal is True:
            selected_org = org_data
            select_member = member_data

        organizations.append(org_data)
        members.append(member_data)

    if not selected_org:
        selected_org = organizations[0]

    request.session['organizations'] = organizations
    request.session['members'] = members
    request.session['organization_context'] = selected_org
    request.session['member_group'] = select_member
