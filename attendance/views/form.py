
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from attendance.forms import attendance_service
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_event.helpers.account import update_account


class BaseAttendanceServiceView(AccountMixin, View):
    template_name = 'attendance/form.html'
    success_message = ''
    success_url = None
    form_title = None
    event = None

    def pre_dispatch(self, request):
        self.event = self.get_event()

        if self.event:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        return super().pre_dispatch(request)

    def get_permission_denied_url(self):
        return reverse_lazy('event:event-list')

    def get_event(self):
        self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        return self.event

    def form_valid(self, form):
        try:
            response = super(BaseAttendanceServiceView, self).form_valid(form)
            update_account(
                request=self.request,
                organization=form.instance.organization,
                force=True
            )

        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        else:
            messages.success(self.request, self.success_message)
            return response

    def _get_referer_url(self):
        request = self.request
        previous_url = request.META.get('HTTP_REFERER')
        if previous_url:
            host = request.scheme + '://' + request.META.get('HTTP_HOST', '')
            previous_url = previous_url.replace(host, '')

            if previous_url != request.path:
                return previous_url

        return self.success_url

    def get_form_title(self):
        return self.form_title

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseAttendanceServiceView, self).get_context_data(
            **kwargs)
        context['next_path'] = self._get_referer_url()
        context['form_title'] = self.get_form_title()

        return context


class AddAttendanceServiceView(BaseAttendanceServiceView, generic.CreateView):
    form_class = attendance_service.AttendanceServiceForm
    success_message = 'Lista de checkin criada com sucesso.'
    form_title = 'Nova lista de checkin'
    object = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        data = kwargs.get("data", {}).copy()

        data.update({"event": self.kwargs.get("event_pk")})
        kwargs.update({"data": data})
        return kwargs

    def get_form(self, form_class=None):
        if not form_class:
            form_class = self.form_class

        kwargs = self.get_form_kwargs()

        return form_class(**kwargs)

    def post(self, request, *args, **kwargs):

        lot_categories = request.POST.getlist('lot_categories', [])
        self.object = None
        form = self.get_form()
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(
                form=form,
            ))

        self.object = form.save()
        return self.form_valid(form)

    def get_success_url(self):
        form = self.get_form()
        event = form.instance
        return reverse(
            'event:event-panel',
            kwargs={'pk': event.pk}
        )

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)

        context['category_list'] = \
            self.event.lot_categories.all().order_by('name')

        return context
