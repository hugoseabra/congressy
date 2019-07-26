from django import forms

from attendance.models import AttendanceService, AttendanceCategoryFilter
from ticket.models import Ticket


class AttendanceServiceForm(forms.ModelForm):
    tickets = forms.CharField(
        widget=forms.CheckboxSelectMultiple,
        label='Ticket',
        required=False,
    )

    class Meta:
        model = AttendanceService
        fields = (
            'name',
            'event',
            'tickets',
            'checkout_enabled',
            'with_certificate',
            'printing_queue_webhook',
            'accreditation',
            'pwa_pin',
        )

    def clean_lot_category_filter(self):
        category_pks = self.cleaned_data.get('tickets')
        if not category_pks:
            return category_pks

        return AttendanceCategoryFilter.objects.filter(pk__in=category_pks)

    def clean_accreditation(self):
        accreditation = self.cleaned_data.get('accreditation', False)
        event = self.cleaned_data.get('event')

        if accreditation is True:
            acc_qs = event.attendance_services.filter(accreditation=True)

            if self.instance:
                acc_qs = acc_qs.exclude(pk=self.instance.pk)

            if acc_qs.count() > 0:
                raise forms.ValidationError('Serviço de atendimento já possui'
                                            ' serviço de credenciamento.')

        return accreditation

    def _create_lot_category_filters(self, service):
        ticket_pks = self.data.getlist('ticket_list', []) or []
        existing_cat_filters = []

        if ticket_pks:
            for cat_filter in service.lot_category_filters.all():
                if cat_filter.ticket_id in ticket_pks:
                    existing_cat_filters.append(cat_filter.ticket_id)
                    continue

                cat_filter.delete()

            cat_filters = service.lot_category_filters

            for cf in cat_filters.exclude(ticket_id__in=ticket_pks):
                cf.delete()

            for ticket in Ticket.objects.filter(pk__in=ticket_pks):
                if ticket.pk in existing_cat_filters:
                    continue

                AttendanceCategoryFilter.objects.create(
                    attendance_service_id=service.pk,
                    ticket_id=ticket.pk,
                )
        else:
            for ticket in Ticket.objects.filter(
                    event_id=service.event_id):
                AttendanceCategoryFilter.objects.create(
                    attendance_service_id=service.pk,
                    ticket_id=ticket.pk,
                )

    def save(self, commit=True):
        service = super().save(commit)
        self._create_lot_category_filters(service=service)

        return service
