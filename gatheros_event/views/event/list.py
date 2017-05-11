from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import classonlymethod
from django.views.generic import ListView, View

from core.helper.account.middleware import get_user_context
from core.view.user_context import UserContextViewMixin
from gatheros_event.models import Event, Member


class ManagerView(LoginRequiredMixin, UserContextViewMixin, ListView):
    model = Event
    template_name = 'gatheros_event/event/list.html'
    ordering = ['name']

    def get_queryset(self):
        qs = super(ManagerView, self).get_queryset()
        organization = self.user_context.active_organization
        return qs.filter(organization__pk=organization.pk)

    def get_context_data(self, **kwargs):
        context = super(ManagerView, self).get_context_data(**kwargs)
        context.update(self.get_event_list_context())
        return context

    def get_event_list_context(self):
        member_group = self.user_context.active_member_group

        def can_add():
            return self.request.user.is_superuser or (
                member_group and member_group.group in [
                    Member.ADMIN,
                ]
            )

        def can_edit():
            return member_group.group in [
                Member.ADMIN,
                Member.HELPER,
            ]

        def can_delete():
            return member_group.group in [
                Member.ADMIN,
            ]

        return {
            'can_add': can_add,
            'can_edit': can_edit,
            'can_delete': can_delete,
        }


class SuperUserView(
    LoginRequiredMixin,
    UserContextViewMixin,
    ListView
):
    model = Event
    template_name = 'gatheros_event/event/list_superuser.html'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        return super(SuperUserView, self).get_context_data(**kwargs)


class EventListView(View):
    @classonlymethod
    def as_view(cls):
        super_view = SuperUserView.as_view()
        manager_view = ManagerView.as_view()

        def view(request, *args, **kwargs):
            if get_user_context().superuser:
                return super_view(request, *args, **kwargs)

            return manager_view(request, *args, **kwargs)

        return view
