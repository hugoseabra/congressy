from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, View

from core.view.delete import DeleteViewMixin
from gatheros_event.models import Member, Organization
from .mixins import AccountMixin


class BaseOrganizationMixin(AccountMixin, View):
    member_organization = None

    def dispatch(self, request, *args, **kwargs):
        if not self._can_view():
            messages.warning(
                request,
                'Você não tem permissão de realizar esta ação.'
            )
            org = self.get_member_organization()
            return redirect(reverse(
                'gatheros_event:organization-panel',
                kwargs={'pk': org.pk}
            ))

        return super(BaseOrganizationMixin, self).dispatch(
            request,
            *args,
            **kwargs
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

    def _can_view(self):
        org = self.get_member_organization()

        not_internal = org.internal is False
        not_participant = self.is_participant is False
        can_manage = self.request.user.has_perm(
            'gatheros_event.can_manage_members',
            org
        )
        return not_internal and not_participant and can_manage


class MemberListView(BaseOrganizationMixin, ListView):
    model = Member
    template_name = 'gatheros_event/member/list.html'

    def get_queryset(self):
        query_set = super(MemberListView, self).get_queryset()
        organization = self.get_member_organization()

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
            'member_organization': self.get_member_organization(),
            'member_active_list': member_active_list,
            'member_inactive_list': member_inactive_list,
        })

        return context


class MemberManageView(BaseOrganizationMixin):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')

        if not action:
            raise ImproperlyConfigured(
                'Campo `action` não encontrado ou vazio. Envie `action` com as'
                ' seguintes opçoes: activate, deactivate, delete.'
            )

        pk = self.kwargs.get('pk')
        if not pk:
            raise ImproperlyConfigured(
                'Campo `pk` não encontrado ou vazio. Informe o `pk` do membro.'
            )

        organization = self.get_member_organization()
        member = get_object_or_404(Member, pk=pk, organization=organization)

        if action == 'change_group':
            group = request.POST.get('group')
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

        if action == 'activate':
            member.active = True

        if action == 'deactivate':
            member.active = False

        member.save()

        messages.success(request, 'Membro alterado com sucesso.')
        return redirect(reverse('gatheros_event:member-list', kwargs={
            'organization_pk': member.organization_id
        }))

    def _can_view(self):
        pk = self.kwargs.get('pk')
        organization = self.get_member_organization()
        member = get_object_or_404(Member, pk=pk, organization=organization)

        can_view = super(MemberManageView, self)._can_view()
        can_change = self.request.user.has_perm(
            'gatheros_event.change_member',
            member
        )

        return can_view and can_change


class MemberDeleteView(BaseOrganizationMixin, DeleteViewMixin):
    model = Member
    success_message = 'Membro excluído com sucesso.'
    place_organization = None
    http_method_names = ['post']

    def get_success_url(self):
        org = self.get_member_organization()
        return reverse('gatheros_event:member-list', kwargs={
            'organization_pk': org.pk
        })
