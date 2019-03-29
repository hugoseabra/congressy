from datetime import datetime

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from attendance.models import AttendanceService, Checkin
from core.views.mixins import TemplateNameableMixin
from gatheros_event.models import Event
from gatheros_subscription.models import Subscription
from gatheros_subscription.views import SubscriptionViewMixin
from importer.forms import (
    FileCollectorFileForm,
)


class FileCollectorImportView(SubscriptionViewMixin, TemplateNameableMixin,
                              generic.FormView):
    """
        View usada para fazer apenas upload de arquivos
    """
    template_name = "importer/file-collector_upload.html"

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
            'importer:file-collector-import',
            kwargs={'event_pk': self.event.pk}
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
                    line=line.replace('\r', '').strip(),
                )
            )

        for item in lines:
            if item.state is True and item.registered is False:
                processable = True

        # messages.success(self.request, "Arquivo submetido com sucesso!")
        return self.render_to_response(self.get_context_data(
            items=lines,
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

    def __init__(self, event: Event, attendance: AttendanceService,
                 attendance_type: str, line: str) -> None:
        self.event = event
        self.attendance_type = attendance_type
        self.attendance = attendance
        self._raw_line = line
        self._processed_line = dict()
        self.state = False
        self.registered = False
        self.error = None
        self.checkin = None

        self._process()

    def _process(self):
        if self._raw_line:

            contents = self._raw_line.split(',')

            if len(contents) != 2:
                self.error = "Não foi possivel dar split corretamente nessa" \
                             " linha."
                return

            code = contents[0].strip()
            created_on = contents[1].strip()  # 14/03/2019 10:35:06

            try:
                created_on = datetime.strptime(created_on, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                self.error = "Não foi possivel serializar neste formato," \
                             " verifique se está: %d/%m/%Y %H:%M:%S"
                return

            self._processed_line['created_on'] = created_on

            try:
                sub = Subscription.objects.get(code=code, event=self.event)
                self._processed_line['pk'] = sub.pk

            except Subscription.DoesNotExist:
                self.error = "Não foi possivel encontrar essa inscrição"

                self._processed_line['pk'] = None
                self._processed_line['code'] = code
                return

            self._processed_line['code'] = code
            self._processed_line['name'] = sub.person.name

            if self.attendance_type == "checkin":
                self.registered = Checkin.objects.filter(
                    attendance_service=self.attendance,
                    checkout__isnull=True,
                    subscription=sub,
                ).exists()

            elif self.attendance_type == "checkout":
                checkins_qs = Checkin.objects.filter(
                    attendance_service=self.attendance,
                    checkout__isnull=True,
                    subscription=sub,
                )

                self.registered = checkins_qs.exists() is False

                if self.registered is False:
                    self.checkin = checkins_qs.last()

            self.state = True

    @property
    def processed_line(self):
        if self._processed_line is not None:
            return self._processed_line

        return self._raw_line
