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
    DjangoCronOffline,
    EventOffline,
    SurveyOffline,
    SubscriptionOffline,
)


class Command(BaseCommand):
    help = 'Limpar todos os dados e deixar apenas os dados do evento solicitado'

    def handle(self, *args, **options):
        with atomic():
            # event_pk = input("Event PK: ")
            event_pk = 206
            assert event_pk is not None and event_pk is not ''

            MixBoletoOffline(stdout=self.stdout, style=self.style).erase_all()
            ScientificWorkOffline(stdout=self.stdout,
                                  style=self.style).erase_all()
            PartnerOffline(stdout=self.stdout, style=self.style).erase_all()
            ServiceTagsOffline(stdout=self.stdout, style=self.style).erase_all()
            ImporterOffline(stdout=self.stdout, style=self.style).erase_all()
            CertificateOffline(stdout=self.stdout, style=self.style).erase_all()
            CertificateOffline(stdout=self.stdout, style=self.style).erase_all()
            AssociateOffline(stdout=self.stdout, style=self.style).erase_all()
            PaymentOffline(stdout=self.stdout, style=self.style).erase_all()
            DjangoCronOffline(stdout=self.stdout, style=self.style).erase_all()
            EventOffline(stdout=self.stdout, style=self.style).erase_all()
            SubscriptionOffline(stdout=self.stdout, style=self.style).filter(event_pk)
            SurveyOffline(stdout=self.stdout, style=self.style).filter(event_pk)

            raise Exception('rollback')
