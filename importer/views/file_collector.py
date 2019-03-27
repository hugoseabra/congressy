from datetime import datetime
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from attendance.models import AttendanceService, Checkin, Checkout
from core.views.mixins import TemplateNameableMixin
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from gatheros_subscription.views import SubscriptionViewMixin
from importer.forms import (
    FileCollectorFileForm,
)


class FileCollectorImportView(SubscriptionViewMixin, TemplateNameableMixin, generic.FormView):
    """
        View usada para fazer apenas upload de arquivos
    """
    template_name = "importer/file-collector_upload.html"

    def dispatch(self, request, *args, **kwargs):

        res = super().dispatch(request, *args, **kwargs)

        if not request.user.is_staff:
            return redirect(reverse_lazy('attendance:manage-list-attendance', kwargs={
                'event_pk': self.event.pk
            }))

        return res

    def get_form(self, form_class=None):
        kwargs = self.get_form_kwargs()

        kwargs['event'] = self.event

        return FileCollectorFileForm(**kwargs)

    def get_context_data(self, data=None, processable=False, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_inside_bar'] = True
        context['data'] = data
        context['user_id'] = self.request.user.person.name
        context['processable'] = processable
        context['active'] = 'inscricoes'
        return context

    def get_success_url(self):
        return reverse_lazy(
            'importer:file-collector-import', kwargs={'event_pk': self.event.pk}
        )

    def form_valid(self, form):
        content = form.cleaned_data['collector_file'].read().decode("utf-8")
        lines = list()

        processable = False

        raw_lines = content.split('\n')

        if len(raw_lines) > 1:
            raw_lines.pop(0)

        for line in raw_lines:
            lines.append(
                Parser(
                    event=self.event,
                    attendance=form.cleaned_data['services'],
                    attendance_type=form.cleaned_data['type'],
                    line=line,
                )
            )

        for item in lines:
            if item.state is True and item.registered is False:
                processable = True

        # messages.success(self.request, "Arquivo submetido com sucesso!")
        return self.render_to_response(self.get_context_data(
            data=lines,
            processable=processable,
            form=form,
        ))

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""

        for error, value in form.errors.items():

            if error == 'collector_file':
                error = "Arquivo"

            messages.error(self.request,
                           "{}: {}".format(error, value[0]))

        return self.render_to_response(self.get_context_data(form=form))


class Parser:

    def __init__(self, event: Event, attendance: AttendanceService, attendance_type: str, line: str) -> None:
        self.event = event
        self.attendance_type = attendance_type
        self.attendance = attendance
        self._raw_line = line
        self._processed_line = None
        self.state = False
        self.registered = False
        self.error = None
        self.checkin = None

        self._process()

    def _process(self):
        if self._raw_line:

            contents = self._raw_line.split(',')

            if len(contents) != 2:
                self.error = "Não foi possivel dar split corretamente nessa linha."
                return

            sub_id = contents[0]
            timestamp = contents[1]  # 14/03/2019 10:35:06
            try:
                timestamp = datetime.strptime(timestamp, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                self.error = "Não foi possivel serializar neste formato, verifique se está: %d/%m/%Y %H:%M:%S"
                return

            try:
                sub = Subscription.objects.get(code=sub_id, event=self.event)
            except Subscription.DoesNotExist:
                self.error = "Não foi possivel encontrar essa inscrição"
                return

            if self.attendance_type == "checkin":
                self.registered = Checkin.objects.filter(attendance_service=self.attendance, subscription=sub).exists()
            elif self.attendance_type == "checkout":
                self.registered = Checkout.objects.filter(checkin__attendance_service=self.attendance,
                                                          checkin__subscription=sub).exists()

                self.checkin = Checkin.objects.get(attendance_service=self.attendance, subscription=sub)

            self.state = True

            self._processed_line = (sub, timestamp)

    @property
    def processed_line(self):
        if self._processed_line is not None:
            return self._processed_line

        return self._raw_line