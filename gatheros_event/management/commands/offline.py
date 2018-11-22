from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from offline import (
    MixBoletoOffline,
    ScientificWorkOffline,
    PartnerOffline,
    ServiceTagsOffline,
    ImporterOffline,
    CertificateOffline,
    AssociateOffline,
    PaymentOffline,
    SurveyOffline,
    AttendanceOffline,
    RaffleOffline,
    DjangoCronOffline,
    AddonOffline,
    SubscriptionOffline,
    EventOffline,
    PersonOffline,
)


class Command(BaseCommand):
    help = 'Limpar todos os dados e deixar apenas os dados do evento solicitado'

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
            MixBoletoOffline(stdout=self.stdout, style=self.style).erase_all()
            ScientificWorkOffline(stdout=self.stdout,
                                  style=self.style).erase_all()
            PartnerOffline(stdout=self.stdout, style=self.style).erase_all()
            ServiceTagsOffline(stdout=self.stdout,
                               style=self.style).erase_all()
            ImporterOffline(stdout=self.stdout, style=self.style).erase_all()
            CertificateOffline(stdout=self.stdout,
                               style=self.style).erase_all()
            CertificateOffline(stdout=self.stdout,
                               style=self.style).erase_all()
            AssociateOffline(stdout=self.stdout, style=self.style).erase_all()
            DjangoCronOffline(stdout=self.stdout, style=self.style).erase_all()

            # =========== FILTERS =============================================
            SurveyOffline(stdout=self.stdout, style=self.style) \
                .filter(event_pk)
            AttendanceOffline(stdout=self.stdout, style=self.style) \
                .filter(event_pk)
            RaffleOffline(stdout=self.stdout, style=self.style).filter(
                event_pk)
            PaymentOffline(stdout=self.stdout, style=self.style) \
                .erase_all() \
                .filter(event_pk)
            AddonOffline(stdout=self.stdout, style=self.style).filter(event_pk)
            SubscriptionOffline(stdout=self.stdout, style=self.style) \
                .filter(event_pk)
            EventOffline(stdout=self.stdout, style=self.style) \
                .erase_all() \
                .filter(event_pk)
            
            PersonOffline(stdout=self.stdout, style=self.style).erase(event_pk)

            if debug:
                raise Exception('rollback')
