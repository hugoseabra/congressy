from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from data_cleaner import (
    MixBoletoDataCleaner,
    ScientificWorkDataCleaner,
    PartnerDataCleaner,
    ServiceTagsDataCleaner,
    ImporterDataCleaner,
    CertificateDataCleaner,
    AssociateDataCleaner,
    PaymentDataCleaner,
    SurveyDataCleaner,
    AttendanceDataCleaner,
    RaffleDataCleaner,
    DjangoCronDataCleaner,
    AddonDataCleaner,
    SubscriptionDataCleaner,
    EventDataCleaner,
    PersonDataCleaner,
    DjangoContribDataCleaner,
    ContractDataCleaner)


class Command(BaseCommand):
    help = 'Limpar todos os dados e deixar apenas os dados do evento' \
           ' solicitado'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--debug', action='store_true',
                            help='run as debug')

    def handle(self, *args, **kwargs):
        debug = kwargs['debug']

        with atomic():
            self.stdout.write(
                self.style.ERROR(
                    '\n\n\t ATENÇÃO: Esse script não deve ser usado em'
                    ' produção. Digite SIM para confirmar a isolação do banco'
                    ' de dados.'
                )
            )

            confirmation = input("\n\n\nTEM CERTEZA ABSOLUTA QUE DESEJA RODA "
                                 "ESSE SCRIPT? (DIGITE SIM PARA CONTINUAR): ")

            assert confirmation is not None and confirmation is not ''

            if confirmation.upper() != "SIM":
                return

            event_pk = input("Event PK: ")
            assert event_pk is not None and event_pk is not ''

            # =========== ERASE ALL ===========================================
            MixBoletoDataCleaner(stdout=self.stdout,
                                 style=self.style).erase_all()
            ScientificWorkDataCleaner(stdout=self.stdout,
                                      style=self.style).erase_all()
            PartnerDataCleaner(stdout=self.stdout,
                               style=self.style).erase_all()
            ServiceTagsDataCleaner(stdout=self.stdout,
                                   style=self.style).erase_all()
            ImporterDataCleaner(stdout=self.stdout,
                                style=self.style).erase_all()
            CertificateDataCleaner(stdout=self.stdout,
                                   style=self.style).erase_all()
            CertificateDataCleaner(stdout=self.stdout,
                                   style=self.style).erase_all()
            AssociateDataCleaner(stdout=self.stdout,
                                 style=self.style).erase_all()
            DjangoCronDataCleaner(stdout=self.stdout,
                                  style=self.style).erase_all()
            DjangoContribDataCleaner(stdout=self.stdout,
                                     style=self.style).erase_all()

            # =========== FILTERS =============================================
            SurveyDataCleaner(stdout=self.stdout, style=self.style) \
                .filter(event_pk)
            AttendanceDataCleaner(stdout=self.stdout, style=self.style) \
                .filter(event_pk)
            RaffleDataCleaner(stdout=self.stdout, style=self.style).filter(
                event_pk)
            PaymentDataCleaner(stdout=self.stdout, style=self.style) \
                .erase_all() \
                .filter(event_pk)
            AddonDataCleaner(stdout=self.stdout, style=self.style).filter(
                event_pk)
            ContractDataCleaner(stdout=self.stdout, style=self.style).filter(
                event_pk)
            SubscriptionDataCleaner(stdout=self.stdout, style=self.style) \
                .filter(event_pk)
            EventDataCleaner(stdout=self.stdout, style=self.style) \
                .erase_all() \
                .filter(event_pk)

            PersonDataCleaner(stdout=self.stdout, style=self.style).erase(
                event_pk)

            if debug:
                raise Exception('rollback')
