from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import FormView, ListView, View

from gatheros_event.forms import OrganizationManageMembershipForm
from gatheros_event.helpers import account
from gatheros_event.helpers.account import update_account
from gatheros_event.models import Member, Organization
from gatheros_event.views.mixins import DeleteViewMixin
from .mixins import AccountMixin


class BaseOrganizationMixin(AccountMixin, View):
    member_organization = None

    def get_permission_denied_url(self):
        return reverse(
            'event:organization-panel',
            kwargs={'pk': self.kwargs.get('organization_pk')}
        )

    def get_member_organization(self):
        """ Resgata organização do contexto da view. """

        if self.member_organization:
            return self.member_organization

        self.member_organization = get_object_or_404(
            Organization,
            pk=self.kwargs.get('organization_pk')
        )
        return self.member_organization

    def can_access(self):
        org = self.get_member_organization()

        not_internal = org.internal is False
        can_view = self.request.user.has_perm(
            'gatheros_event.can_view_members',
            org
        )
        return not_internal and self.is_manager and can_view


class MemberListView(BaseOrganizationMixin, ListView):
    model = Member
    template_name = 'member/list.html'

    def dispatch(self, request, *args, **kwargs):

        member_org = self.get_member_organization()
        update_account(
            request=self.request,
            organization=member_org,
            force=True
        )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query_set = super(MemberListView, self).get_queryset()
        # organization = self.get_member_organization()
        organization = self.organization

        return query_set.filter(organization=organization).exclude(
            person__user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super(MemberListView, self).get_context_data(**kwargs)

        member_active_list = {}
        member_inactive_list = []

        def add_to_list(item):
            group_name = item.get_group_display()

            if item.active:
                selected_list = member_active_list

                if selected_list.get(group_name) is None:
                    selected_list[group_name] = []

                selected_list[group_name].append(item)

            else:
                member_inactive_list.append(member)

        for member in self.object_list:
            add_to_list(member)

        context.update({
            'can_manage': self._can_manage(),
            'can_manage_invitations': self._can_manage_invitations(),
            # 'member_organization': self.get_member_organization(),
            'member_organization': self.organization,
            'member_active_list': member_active_list,
            'has_inside_bar': True,
            'active': 'membros',
            'member_inactive_list': member_inactive_list,
        })

        return context

    def _can_manage(self):
        """ Checks if logged user can manage members. """
        return self.request.user.has_perm(
            'gatheros_event.can_manage_members',
            self.get_member_organization()
        )

    def _can_manage_invitations(self):
        return self.request.user.has_perm(
            'gatheros_event.can_invite',
            self.get_member_organization()
        )


class MemberManageView(BaseOrganizationMixin, FormView):
    http_method_names = ['post']
    form_class = OrganizationManageMembershipForm
    object = None

    def get_object(self):
        """ Recupera instância de membro como objeto principal. """
        if self.object:
            return self.object

        self.object = get_object_or_404(Member, pk=self.kwargs.get('pk'))
        return self.object

    def get_permission_denied_url(self):
        return reverse('front:start')

    def get_form_kwargs(self):
        kwargs = super(MemberManageView, self).get_form_kwargs()
        kwargs.update({
            'organization': self.get_member_organization()
        })
        return kwargs

    # noinspection PyUnusedLocal
    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        pk = self.kwargs.get('pk')
        if not pk:
            raise ImproperlyConfigured(
                'Campo `pk` não encontrado ou vazio. Informe o `pk` do membro.'
            )

        form = self.get_form()
        organization = self.get_member_organization()
        member = get_object_or_404(Member, pk=pk, organization=organization)

        if action == 'change_group':
            group = request.POST.get('group')
            if group:
                group = group.strip()

            available_groups = [Member.ADMIN, Member.HELPER]

            if group not in available_groups:
                raise ImproperlyConfigured(
                    'Campo `group` não encontrado ou vazio. Para alterar o'
                    ' grupo do membro você precisa informar um grupo válido.'
                    ' Os grupos podem ser: {available_groups}.'.format(
                        available_groups=', '.join(available_groups)
                    )
                )

            member.group = group
            member.save()
            messages.success(request, 'Membro alterado com sucesso.')
            return redirect(reverse('event:member-list', kwargs={
                'organization_pk': member.organization_id
            }))

        if action == 'activate' or action == 'deactivate':
            method = getattr(form, action)
            method(member)
            messages.success(request, 'Membro alterado com sucesso.')
            return redirect(reverse('event:member-list', kwargs={
                'organization_pk': member.organization_id
            }))

        elif action == 'delete':
            try:
                member_is_user = self._member_is_user()
                form.delete(member.person.user)

                if member_is_user:
                    self._update_active_organization()

            except Exception as e:
                messages.error(request, str(e))

            else:
                messages.success(
                    request,
                    'Você não é mais membro da organização `{}`.'.format(
                        organization.name
                    )
                )

            return redirect(reverse('front:start'))

        else:
            raise ImproperlyConfigured(
                'Campo `action` não encontrado ou vazio. Envie `action` com as'
                ' seguintes opçoes: activate, deactivate, delete.'
            )

    def can_access(self):
        if self._member_is_user():
            return True

        organization = self.get_member_organization()
        can_view = super(MemberManageView, self).can_access()
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_members',
            organization
        )

        can_change = self.request.user.has_perm(
            'gatheros_event.change_member',
            self.get_object()
        )

        return can_view and can_manage and can_change

    def _member_is_user(self):
        """
        Verifica se usuário logado é o mesmo do membro a ser gerenciado.
        """
        pk = self.kwargs.get('pk')
        organization = self.get_member_organization()
        try:
            member = Member.objects.get(
                pk=pk,
                organization=organization
            )
        except Member.DoesNotExist:
            return False

        member_person = member.person
        user_person = self.request.user.person
        return member_person.pk == user_person.pk

    def _update_active_organization(self):
        """ Atualiza contexto de usuário, definindo organização ativa. """
        account.clean_account(self.request)
        account.update_account(self.request)


class MemberDeleteView(BaseOrganizationMixin, DeleteViewMixin):
    model = Member
    success_message = 'Membro excluído com sucesso.'
    place_organization = None
    http_method_names = ['post']

    def get_success_url(self):
        org = self.get_member_organization()
        return reverse('event:member-list', kwargs={
            'organization_pk': org.pk
        })
