"""
    Formulário usado para selecionar o lote do evento.
"""

from django import forms

from ticket.models import Ticket


class BaseTicketForm(forms.Form):
    private = False

    def __init__(self, event, excluded_ticket_pk=None, code=None, **kwargs):
        self.event = event
        self.excluded_ticket_pk = excluded_ticket_pk

        super().__init__(**kwargs)

        self.fields['ticket'].choices = self.get_ticket_choices()

        if code:
            try:
                ticket = Ticket.objects.get(
                    exhibition_code=code.upper(),
                    event_id=self.event.pk,
                )

                name = '{} (cupom: {})'.format(
                    ticket.display_name_and_price,
                    code,
                )

                self.fields['ticket'].initial = ticket.pk
                self.fields['ticket'].choices.append(
                    (ticket.pk, name)
                )

            except Ticket.DoesNotExist:
                pass

    def get_ticket_choices(self):
        ticket_qs = self.event.tickets \
            .filter(private=self.private) \
            .order_by('name', 'lots__date_start')

        if self.excluded_ticket_pk is not None:
            ticket_qs = ticket_qs.exclude(pk=self.excluded_ticket_pk)

        return [
            (ticket.pk, ticket.display_name_and_price)
            for ticket in ticket_qs
            if ticket.running is True
        ]


class TicketForm(BaseTicketForm):
    private = False

    ticket = forms.ChoiceField(
        required=False,
        label='ingresso',
        widget=forms.Select(),
    )


class PrivateTicketForm(BaseTicketForm):
    private = True

    ticket = forms.ChoiceField(
        required=False,
        label='ingresso',
        widget=forms.HiddenInput(),
    )
