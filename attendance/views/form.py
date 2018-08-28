from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect

from django.views import View, generic
from attendance.forms import AttendanceServiceForm
from attendance.models import AttendanceCategoryFilter
from gatheros_event.models import Event
from gatheros_event.views.mixins import AccountMixin
from gatheros_event.helpers.account import update_account


class BaseAttendanceServiceView(AccountMixin, View):
    template_name = 'attendance/form.html'
    success_message = ''
    success_url = None
    form_title = None
    event = None

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            data = kwargs.get("data", {}).copy()

            data.update({"event": int(self.kwargs.get("event_pk"))})
            kwargs.update({"data": data})

        return kwargs

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        except Event.DoesNotExist:
            messages.warning(
                request,
                "Evento não informado."
            )
            return redirect(reverse_lazy('event:event-list'))

        else:
            update_account(
                request=self.request,
                organization=self.event.organization,
                force=True
            )

        return super().dispatch(request, *args, **kwargs)

    def get_permission_denied_url(self):
        return reverse_lazy('event:event-list')

    def get_event(self):
        self.event = Event.objects.get(pk=self.kwargs.get('event_pk'))

        return self.event

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super(BaseAttendanceServiceView, self).get_context_data(
            **kwargs)
        context['event'] = self.event

        return context


class AddAttendanceServiceView(BaseAttendanceServiceView, generic.CreateView):
    form_class = AttendanceServiceForm
    success_message = 'Lista de checkin criada com sucesso.'
    form_title = 'Nova lista de checkin'
    object = None

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(
                form=form,
            ))

        self.object = form.save()
        return self.form_valid(form)

    def get_success_url(self):
        return reverse(
            'attendance:manage-list-attendance',
            kwargs={'event_pk': self.event.pk}
        )

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)

        context['category_list'] = self.event.lot_categories.all()
        return context


class EditAttendanceServiceView(BaseAttendanceServiceView, generic.UpdateView):
    template_name = 'attendance/edit-form.html'
    form_class = AttendanceServiceForm
    model = AttendanceServiceForm.Meta.model
    success_url = reverse_lazy('attendance:manage-list-attendance')
    success_message = 'Lista de checkin alterada com sucesso.'

    def get_success_url(self):
        return reverse(
            'attendance:manage-list-attendance',
            kwargs={'event_pk': self.event.pk}
        )

    def get_lot_categories(self):
        items = []
        lc_filter_pks = []
        for item in AttendanceCategoryFilter.objects.filter(
                attendance_service_id=self.object.pk):
            lc_filter_pks.append(item.lot_category_id)

        for lc in self.event.lot_categories.all().order_by('name'):
            items.append({
                'name': lc.name,
                'value': lc.pk,
                'checked': lc.pk in lc_filter_pks
            })

        return items

    def get_context_data(self, **kwargs):
        # noinspection PyUnresolvedReferences
        context = super().get_context_data(**kwargs)
        context['lot_categories'] = self.get_lot_categories()
        return context


class DeleteAttendanceServiceView(BaseAttendanceServiceView, generic.DeleteView):
    model = AttendanceServiceForm.Meta.model
    delete_message = "Tem certeza que deseja excluir a lista de checkin \"{name}\"?"
    success_message = "Lista de checkin excluída com sucesso!"

    def get_success_url(self):
        return reverse(
            'attendance:manage-list-attendance',
            kwargs={'event_pk': self.event.pk}
        )
