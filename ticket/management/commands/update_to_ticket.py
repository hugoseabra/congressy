from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from gatheros_event.models import Event
from ticket.management import LotMapper, Normalizer, CommandFileLogger


class Command(BaseCommand):
    help = 'Atualizar toda infraestrutura de lotes para Ingressos'

    def __init__(self, stdout=None, stderr=None, no_color=False):
        super().__init__(stdout, stderr, no_color)
        self.logger = CommandFileLogger()

    def add_arguments(self, parser):
        parser.add_argument('-f',
                            '--future',
                            action='store_true',
                            help='Update only future events')

        parser.add_argument('-d',
                            '--debug',
                            action='store_true',
                            help='Dry run for debugging')
        parser.add_argument('-nw',
                            '--nowrite',
                            action='store_true',
                            help='Don\'t save a log file')

        parser.add_argument('-e',
                            '--event',
                            action='store',
                            help='Run for specific event')

    def handle(self, *args, **options):

        future = options['future']
        event = options['event']
        debug = options['debug']
        no_write = options['nowrite']

        past_events = Event.objects.filter(
            date_start__lt=datetime.now(),
            date_end__lt=datetime.now(),
        )

        future_events = Event.objects.filter(
            date_start__gt=datetime.now(),
            date_end__gt=datetime.now(),
        )

        live_events = Event.objects.filter(
            date_start__lte=datetime.now(),
            date_end__gt=datetime.now(),
        )

        with atomic():

            if event:
                self.update_future(Event.objects.filter(pk=event),
                                   no_write=no_write)
            elif future:

                self.update_future(future_events, no_write=no_write)

            else:
                self.update_past_and_present(past_events=past_events,
                                             present_events=live_events,
                                             no_write=no_write, )

                self.update_future(future_events, no_write=no_write)

            if debug:
                raise Exception('roll-back')

    def update_past_and_present(self, past_events, present_events, **kwargs):

        past_event_orgs = dict()
        present_event_orgs = dict()

        print('==========================================================')
        print('PAST EVENTS')
        print('==========================================================')

        for event in past_events:
            lot_map = LotMapper(event, old_map=True).create_map()

            normalizer = Normalizer(event, lot_map)
            normalizer.normalize()

            if event.organization.name not in past_event_orgs:
                past_event_orgs[event.organization.name] = {
                    'organization': event.organization,
                    'events': list()
                }

            past_event_orgs[event.organization.name]['events'].append(event)

            print('----------------------------------------------------------')

        if kwargs['no_write'] is False:
            self.logger.write_to_file('eventos_passados.txt', past_event_orgs)

        print('==========================================================')
        print('CURRENT EVENTS')
        print('==========================================================')

        for event in present_events:
            lot_map = LotMapper(event, old_map=True).create_map()
            normalizer = Normalizer(event, lot_map)
            normalizer.normalize()

            if event.organization.name not in present_event_orgs:
                present_event_orgs[event.organization.name] = {
                    'organization': event.organization,
                    'events': list()
                }

            present_event_orgs[event.organization.name]['events'] \
                .append(event)

            print('----------------------------------------------------------')

        if kwargs['no_write'] is False:
            self.logger.write_to_file('eventos_em_andamento.txt',
                                      present_event_orgs)

    def update_future(self, future_events, **kwargs):

        future_events_orgs = dict()

        print('==========================================================')
        print('FUTURE EVENTS')
        print('==========================================================')

        for event in future_events:
            lot_map = LotMapper(event, new_map=True).create_map()
            normalizer = Normalizer(event, lot_map)
            normalizer.normalize()

            if event.organization.name not in future_events_orgs:
                future_events_orgs[event.organization.name] = {
                    'organization': event.organization,
                    'events': list()
                }

                future_events_orgs[event.organization.name]['events'] \
                    .append(event)

            print('----------------------------------------------------------')

        if kwargs['no_write'] is False:
            self.logger.write_to_file('eventos_futuros.txt', future_events_orgs)
