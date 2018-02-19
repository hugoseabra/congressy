# noinspection PyPep8
import django

django.setup()

from gatheros_event.models import Event, Info, Organization, Category
from gatheros_subscription.models import Lot
from datetime import datetime, timedelta


# Static elements used in event creation.
info = {
    "description": "Descri&ccedil;&atilde;o Aqui\r\n\r\nAo contr&aacute;rio do"
                   " que se acredita, Lorem Ipsum n&atilde;o &eacute;"
                   " simplesmente um texto rand&ocirc;mico. Com mais de 2000"
                   " anos, suas ra&iacute;zes podem ser encontradas em uma"
                   " obra de literatura latina cl&aacute;ssica datada de 45"
                   " AC. Richard McClintock, um professor de latim do"
                   " Hampden-Sydney College na Virginia, pesquisou uma das"
                   " mais obscuras palavras em latim, consectetur, oriunda de"
                   " uma passagem de Lorem Ipsum, e, procurando por entre"
                   " cita&ccedil;&otilde;es da palavra na literatura"
                   " cl&aacute;ssica, descobriu a sua indubit&aacute;vel"
                   " origem. Lorem Ipsum vem das se&ccedil;&otilde;es"
                   " 1.10.32 e 1.10.33 do &quot;de Finibus Bonorum et"
                   " Malorum&quot; (Os Extremos do Bem e do Mal), de"
                   " C&iacute;cero, escrito em 45 AC. Este livro &eacute; um"
                   " tratado de teoria da &eacute;tica muito popular na"
                   " &eacute;poca da Renascen&ccedil;a. A primeira linha de"
                   " Lorem Ipsum, &quot;Lorem Ipsum dolor sit amet...&quot;"
                   " vem de uma linha na se&ccedil;&atilde;o 1.10.32.\r\n\r\nO"
                   " trecho padr&atilde;o original de Lorem Ipsum, usado desde"
                   " o s&eacute;culo XVI, est&aacute; reproduzido abaixo para"
                   " os interessados. Se&ccedil;&otilde;es 1.10.32 e 1.10.33"
                   " de &quot;de Finibus Bonorum et Malorum&quot; de Cicero"
                   " tamb&eacute;m foram reproduzidas abaixo em sua forma"
                   " exata original, acompanhada das vers&otilde;es para o"
                   " ingl&ecirc;s da tradu&ccedil;&atilde;o feita por H."
                   " Rackham em 1914.",
    "description_html": "<h1><strong>Descri&ccedil;&atilde;o Aqui</strong>"
                        "</h1>\r\n\r\n<p>Ao contr&aacute;rio do que se"
                        " acredita, Lorem Ipsum n&atilde;o &eacute;"
                        " simplesmente um texto rand&ocirc;mico. Com mais de"
                        " 2000 anos, suas ra&iacute;zes podem ser encontradas"
                        " em uma obra de literatura latina cl&aacute;ssica"
                        " datada de 45 AC. Richard McClintock, um professor de"
                        " latim do Hampden-Sydney College na Virginia,"
                        " pesquisou uma das mais obscuras palavras em latim,"
                        " consectetur, oriunda de uma passagem de Lorem Ipsum,"
                        " e, procurando por entre cita&ccedil;&otilde;es da"
                        " palavra na literatura cl&aacute;ssica, descobriu a"
                        " sua indubit&aacute;vel origem. Lorem Ipsum vem das"
                        " se&ccedil;&otilde;es 1.10.32 e 1.10.33 do &quot;de"
                        " Finibus Bonorum et Malorum&quot; (Os Extremos do Bem"
                        " e do Mal), de C&iacute;cero, escrito em 45 AC. Este"
                        " livro &eacute; um tratado de teoria da &eacute;tica"
                        " muito popular na &eacute;poca da Renascen&ccedil;a."
                        " A primeira linha de Lorem Ipsum, &quot;Lorem Ipsum"
                        " dolor sit amet...&quot; vem de uma linha na"
                        " se&ccedil;&atilde;o 1.10.32.</p>\r\n\r\n<p>O trecho"
                        " padr&atilde;o original de Lorem Ipsum, usado desde"
                        " o s&eacute;culo XVI, est&aacute; reproduzido abaixo"
                        " para os interessados. Se&ccedil;&otilde;es 1.10.32"
                        " e 1.10.33 de &quot;de Finibus Bonorum et"
                        " Malorum&quot; de Cicero tamb&eacute;m foram"
                        " reproduzidas abaixo em sua forma exata original,"
                        " acompanhada das vers&otilde;es para o ingl&ecirc;s"
                        " da tradu&ccedil;&atilde;o feita por H. Rackham em"
                        " 1914.</p>",
    "config_type": "text_only",
    "lead": "Evento Teste",
    "image_main": 'nego_borel_amnesia.jpg',
}
organization = Organization.objects.first()
category = Category.objects.first()


# Event configurations.
event_by_complex_lots_configs = {
    "2 Lotes Expirados": {
        'lots': [
            {
                'name': 'Lote Expirado #1',
                'date_start': datetime.now() - timedelta(days=2),
                'date_end': datetime.now() - timedelta(days=1),
            },
            {
                'name': 'Lote Expirado #2',
                'date_start': datetime.now() - timedelta(days=3),
                'date_end': datetime.now() - timedelta(days=2),
            },
        ],
    },
    "1 Lote Não Disponível (data futura)": {
        'lots': [
            {
                'name': 'Lote Não Disponível',
                'date_start': datetime.now() + timedelta(hours=1),
                'date_end': datetime.now() + timedelta(hours=2),
            },
        ],
    },
    "1 Lote Disponível Limitado Lotado": {
        'lots': [
            {
                'name': 'Lote Disponível Limitado Lotado',
                'date_start': datetime.now() - timedelta(hours=1),
                'date_end': datetime.now() + timedelta(hours=2),
                'limit': 5,
            },
        ],
    },
    "1 Lote Disponível Ilimitado": {
        'lots': [
            {
                'name': 'Lote Disponível Ilimitado',
                'date_start': datetime.now() - timedelta(hours=1),
                'date_end': datetime.now() + timedelta(hours=2),
            },
        ],
    },
    "1 Lote Disponível Limitado (5 vagas)": {
        'lots': [
            {
                'name': 'Lote Disponível Limitado (5 vagas)',
                'date_start': datetime.now() - timedelta(hours=1),
                'date_end': datetime.now() + timedelta(hours=2),
                'limit': 5,
            },

        ],
    },
    "1 Lote Disponível e 1 Não-iniciado": {
        'lots': [
            {
                'name': 'Lote Disponível',
                'date_start': datetime.now() - timedelta(hours=1),
                'date_end': datetime.now() + timedelta(hours=2),
            },
            {
                'name': 'Lote Não-iniciado',
                'date_start': datetime.now() + timedelta(hours=3),
                'date_end': datetime.now() + timedelta(hours=4),
            },
        ],
    },
    "1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)": {
        'lots': [
            {
                'name': 'Lote Disponível Limitado Lotado (5 vagas)',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() + timedelta(hours=3),
                'limit': 5,
            },
            {
                'name': 'Lote Disponível Limitado (5 vagas)',
                'date_start': datetime.now() - timedelta(hours=4),
                'date_end': datetime.now() + timedelta(hours=5),
                'limit': 5,
            },
        ],
    },
    "1 Lote Disponível Limitado Lotado e 1 Não-iniciado": {
        'lots': [
            {
                'name': 'Lote Disponível Limitado Lotado (5 vagas)',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() + timedelta(hours=3),
                'limit': 5,
            },
            {
                'name': 'Lote Não-iniciado',
                'date_start': datetime.now() + timedelta(hours=2),
                'date_end': datetime.now() + timedelta(hours=3),
            },
        ],
    },
    "1 Lote Expirado e 1 Disponível Ilimitado": {
        'lots': [
            {
                'name': 'Lote Expirado',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() - timedelta(hours=1),

            },
            {
                'name': 'Lote Disponivel Ilimitado',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() + timedelta(hours=1),

            },
        ],
    },
    "1 Lote Expirado e 1 Disponível Limitado (5 vagas)": {
        'lots': [
            {
                'name': 'Lote Expirado',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() - timedelta(hours=1),

            },
            {
                'name': 'Lote Disponivel Limitado (5 Vagas)',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() + timedelta(hours=1),
                'limit': 5,

            },
        ],
    },
    "1 Lote Expirado e 1 Disponível Limitado Lotado": {
        'lots': [
            {
                'name': 'Lote Expirado',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() - timedelta(hours=1),

            },
            {
                'name': 'Lote Disponivel Limitado Lotado (5 Vagas) ',
                'date_start': datetime.now() - timedelta(hours=2),
                'date_end': datetime.now() + timedelta(hours=1),
                'limit': 5,

            },
        ],
    }
}
event_by_simple_lots_configs = {
    "lotes disponível (c/ transferencia de taxas)": {
        'lots': [
            {
                'name': 'lotes disponível (c/ transferencia de taxas)',
                'date_start': datetime.now() - timedelta(days=2),
                'price': 10,
            },
        ],

    },
    "lotes disponível (s/ transferencia de taxas)": {
        'lots': [
            {
                'name': 'lotes disponível (s/ transferencia de taxas)',
                'date_start': datetime.now() - timedelta(days=2),
                'price': 10,
            },
        ],
    },

}
event_config = {
    "Não-publicado": {
        'subscription_type': 'simple',
        'published': False
    },
    "Disponivel": {
        'subscription_type': 'simple',
        'date_start': datetime.now() - timedelta(days=2),
    },
    "Futuro": {
        'subscription_type': 'simple',
    },
    "Futuro Publicado Insc. Desativadas": {
        'subscription_type': 'disabled',
        'published': False
    },
    "Futuro Publicado Insc. Simples": {
        'subscription_type': 'simple',
    },
}


# Function responsible for creating events.
def create_event(event_prefix, event_data):
    event_dict = {
        "name": '{0} - {1}'.format(event_prefix, event_name),
        "organization": organization,
        "category": category,
        "subscription_type": event_data.get('subscription_type', "by_lots"),
        "date_start": event_data.get('date_start', datetime.now() + timedelta(days=10)),
        "date_end": event_data.get('date_end', datetime.now() + timedelta(days=11)),
        "published": event_data.get('published', True),
    }

    event_object = Event.objects.create(**event_dict)
    info['event'] = event_object
    Info.objects.create(**info)

    return event_object


# Function responsible for creating the lotes.
def create_lot(lot, event, event_type):
    lot_dict = {
        'name': lot.get('name'),
        'date_start': lot.get('date_start'),
        'date_end': lot.get('date_end'),
        'limit': lot.get('limit', 0),
        'event': event,
    }

    if event_type == "Futuro e Pago c/ 'Lotes' com Transferência de Taxas" or \
            "Futuro e Pago c/ 'Lotes' com Transferência de Taxas":
        lot_dict['transfer_tax'] = True
        lot_dict['price'] = 10
    elif event_type == "Futuro e Pago c/ 'Lotes' sem Transferência de Taxas":
        lot_dict['price'] = 10

    Lot.objects.create(**lot_dict)


# Types of events.
types_of_events = [
    "Não-publicado",
    "Disponivel",
    "Futuro",
    "Futuro Publicado Insc. Desativadas"
    "Futuro Publicado Insc. Simples"
]
types_of_complex_lots_events = [
    "Futuro, Publicado e Gratuito c/ 'Lotes'",
    "Futuro e Pago c/ 'Lotes' sem Transferência de Taxas",
    "Futuro e Pago c/ 'Lotes' com Transferência de Taxas",
]
types_of_simple_lots_events = [
    "Futuro e Pago c/ 'Lotes' sem Transferência de Taxas",
    "Futuro e Pago c/ 'Lotes' com Transferência de Taxas",
]


# For-loops responsible for actually creating events and lotes.
for event_name in event_config.keys():
    data = event_config[event_name]
    event = create_event(event_name, data)
for event_type in types_of_complex_lots_events:
    for event_name in event_by_complex_lots_configs.keys():

        data = event_by_complex_lots_configs[event_name]
        event = create_event(event_type, data)

        for existing_lot in event.lots.all():
            existing_lot.delete()

        for lot in data.get('lots'):
            create_lot(lot, event, event_type)
for event_name in event_by_simple_lots_configs.keys():

    data = event_by_simple_lots_configs[event_name]

    event = create_event(event_name, data)

    for lot in data.get('lots'):
        create_lot(lot, event, event_name)
