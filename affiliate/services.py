from affiliate import managers
from base import services


class AffiliateService(services.ApplicationService):
    """ Application service de afiliado. """
    manager_class = managers.AffiliateManager


class AffiliationService(services.ApplicationService):
    """ Application service de afiliação. """
    manager_class = managers.AffiliationManager

    def __init__(self, **kwargs):
        # Suporta edição sem informar links em data
        instance = kwargs.get('instance')
        data = kwargs.get('data')
        if instance and data:
            data = data.copy()

            link_fields = (
                'link_direct',
                'link_whatsapp',
                'link_facebook',
                'link_twitter'
            )
            for link_f in link_fields:
                if link_f not in data:
                    data[link_f] = getattr(instance, link_f)

            kwargs.update({'data': data})

        super().__init__(**kwargs)
