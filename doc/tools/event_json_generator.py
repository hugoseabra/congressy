# noinspection PyPep8

import json
from slugify import slugify

current_pk = 26

lote_types = [
    "2 Lotes Expirados",
    "1 Lote Não Disponível (data futura)",
    "1 Lote Disponível Limitado Lotado",
    "1 Lote Disponível Ilimitado",
    "1 Lote Disponível Limitado (5 vagas)",
    "1 Lote Disponível e 1 Não-iniciado",
    "1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)",
    "1 Lote Disponível Limitado Lotado e 1 Não-iniciado",
    "1 Lote Expirado e 1 Disponível Ilimitado",
    "1 Lote Expirado e 1 Disponível Limitado (5 vagas)",
    "1 Lote Expirado e 1 Disponível Limitado Lotado",
]


dict_list = []

for lote in lote_types:
    current_pk += 1
    event_name = "Evento Futuro Publicado, Pago Sem Transferencia de Taxas - " + lote
    slug = slugify(event_name)

    main_dict = {
        "model": "gatheros_event.event",
        "pk": current_pk,
        "fields": {
            "name": event_name,
            "organization": 1,
            "category": 2,
            "subscription_type": "by_lots",
            "subscription_offline": False,
            "slug": slug,
            "date_start": "2018-02-16T07:55:36",
            "date_end": "2018-02-17T07:56:19",
            "place": None,
            "banner_small": "",
            "banner_slide": "",
            "banner_top": "",
            "image_main": "",
            "website": None,
            "facebook": None,
            "twitter": None,
            "linkedin": None,
            "skype": None,
            "published": True,
        }
    }

    dict_list.append(main_dict)


print(json.dumps(dict_list))

