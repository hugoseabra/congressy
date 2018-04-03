from django.db import transaction

from affiliate import managers
from base import services

from bitly.models import Bittle
from gatheros_event.models import Event


class AffiliateService(services.ApplicationService):
    """ Application service de afiliado. """
    manager_class = managers.AffiliateManager


class AffiliationService(services.ApplicationService):
    """ Application service de afiliação. """
    manager_class = managers.AffiliationManager

    def __init__(self, **kwargs):
        data = kwargs.get('data')
        if data:
            kwargs.update({'data': self._create_links(
                kwargs.get('data'),
                kwargs.get('instance')
            )})

        super().__init__(**kwargs)

    def _get_event_absolute_link(self, event):
        """ Resgata link absolute do site do evento """
        from django.contrib.sites.models import Site
        from project.manage.settings import SITE_ID as MANAGE_SITE_ID
        from django.conf import settings

        site = Site.objects.get(pk=int(MANAGE_SITE_ID))

        return '{protocol}://{domain}/{path}'.format(
            protocol=getattr(settings, 'ABSOLUTEURI_PROTOCOL', 'http'),
            domain=site.domain,
            path=event.slug
        )

    def _create_links(self, data, instance=None):
        # torna 'data' mutável
        data = data.copy()

        # Se não há evento, retornar normalmente para retornar o erro
        if 'event' not in data:
            return data

        try:
            event = Event.objects.get(pk=int(data.get('event')))

        except Event.DoesNotExist:
            return data

        hotsite_url = self._get_event_absolute_link(event)

        link_fields = (
            'link_direct',
            'link_whatsapp',
            'link_facebook',
            'link_twitter',
        )

        with transaction.atomic():
            for link_f in link_fields:
                link = getattr(instance, link_f) if instance else None

                # se já existe um link salvo, não edita-lo
                if link:
                    data[link_f] = link
                    continue

                incoming_link = data.get(link_f)

                # Se há um link vindo externamente, não permitir que seja
                # inserido.
                if not link and incoming_link:
                    del data[link_f]

                # Ignorar o link externo e criar um novo
                shortener = Bittle.objects.bitlify(hotsite_url)
                data[link_f] = shortener.short_url

        return data
