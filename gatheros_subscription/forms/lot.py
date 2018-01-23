""" Formulários de `Lot` """
from datetime import timedelta, datetime

from datetimewidget.widgets import DateTimeWidget
from django import forms

from gatheros_subscription.models import Lot


class LotForm(forms.ModelForm):
    """ Formulário de lote. """
    event = None

    class Meta:
        """ Meta """
        model = Lot
        fields = [
            'event',
            'name',
            'date_start',
            'date_end',
            'limit',
            'price',
            'private',
            'exhibition_code',
            # 'discount_type',
            # 'discount',
            'transfer_tax',

        ]
        widgets = {
            'event': forms.HiddenInput(),
            'price': forms.TextInput(),
            'date_start':  DateTimeWidget(
                bootstrap_version=3,
                attrs={'style': 'background-color:#FFF'},
            ),
            'date_end':  DateTimeWidget(
                bootstrap_version=3,
                attrs={'style': 'background-color:#FFF'},
            ),
        }

    def __init__(self, **kwargs):

        # if 'instance' in kwargs and kwargs['instance'] is not None:
        #     self.instance = kwargs.get('instance')
        #     if not self.instance.exhibition_code:
        #         kwargs['initial']['exhibition_code'] = \
        #             str(uuid.uuid4()).split('-')[0].upper()
        #
        # else:
        #     event = kwargs.get('initial').get('event')
        #     kwargs['initial']['date_end'] = event.date_start - timedelta(minutes=1)

        super(LotForm, self).__init__(**kwargs)

        self.event = kwargs.get('initial').get('event')

        # self._set_dates_help_texts()
        #
        self._set_widget_date()

    def _set_dates_help_texts(self):
        last_lot = self.event.lots.last()

        if not last_lot:
            return

        if self.instance.pk == last_lot.pk:
            date_start_help = \
                'Este lote pega todo o período anterior ao' \
                ' evento.'.format(last_lot.name)

        else:
            diff = self.event.date_start - last_lot.date_end
            if diff.days <= 1:
                date_start_help = \
                    'O lote anterior ({}) pega todo o' \
                    ' período anterior ao evento.'.format(last_lot.name)
            else:
                lot_date_end = last_lot.date_end.strftime('%d/%m/%Y %Hh%M')
                date_start_help = \
                    'Existe um lote anterior ({}) que finaliza em {}.' \
                    ' Tente não chocar as' \
                    ' datas.'.format(last_lot.name, lot_date_end)

        self.fields['date_start'].help_text = date_start_help

        event_date_start = self.event.date_start.strftime('%d/%m/%Y %Hh%M')

        self.fields['date_end'].help_text = \
            'O evento inicia-se em {}. O final do lote será anterior a' \
            ' este data.'.format(event_date_start)

    def _set_widget_date(self):

        self.fields['date_start'].widget = DateTimeWidget(
            bootstrap_version=3,
            attrs={'style': 'background-color:#FFF'},
            options={'startDate': '{0:%d-%m-%Y %H:%M}'.format(datetime.now()),
                     'endDate': '{0:%d-%m-%Y %H:%M}'.format(self.event.date_start - timedelta(minutes=2))})

        self.fields['date_end'].widget = DateTimeWidget(
            bootstrap_version=3,
            attrs={'style': 'background-color:#FFF'},
            options={'startDate': '{0:%d-%m-%Y %H:%M}'.format(datetime.now()),
                     'endDate': '{0:%d-%m-%Y %H:%M}'.format(self.event.date_start - timedelta(minutes=2))})


    # def clean_date_start(self):
    #     lots = self.event.lots.order_by('date_start')
    #     date_start = self.cleaned_data['date_start']
    #
    #     lot_dt = date_start
    #     for lot in lots:
    #         lot.date_end = lot_dt - timedelta(minutes=1)
    #         lot.save()
    #
    #         lot_dt = lot.date_start
    #
    #     return date_start


    # SMART WIDGET
    # def _set_widget_start_date(self):
    #
    #     previous_lot_exist = self.event.lots.last()
    #     last_call = self.event.date_start - timedelta(minutes=1)
    #
    #     if previous_lot_exist:
    #         if previous_lot_exist.date_start < datetime.now():
    #             str_date = '{0:%d-%m-%Y %H:%M}'.format(datetime.now())
    #         else:
    #             str_date = '{0:%d-%m-%Y %H:%M}'.format(
    #                 previous_lot_exist.date_start + timedelta(days=1))
    #         last_date_str = '{0:%d-%m-%Y %H:%M}'.format(last_call)
    #     else:
    #         str_date = '{0:%d-%m-%Y %H:%M}'.format(datetime.now())
    #         last_date_str = '{0:%d-%m-%Y %H:%M}'.format(last_call)
    #
    #     self.fields['date_start'].widget = DateTimeWidget(
    #         bootstrap_version=3,
    #         attrs={'style': 'background-color:#FFF'},
    #         options={'startDate': str_date, 'endDate': last_date_str})
