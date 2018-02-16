# noinspection PyPep8
from gatheros_event.models import Event, Info

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
}

event_by_lots_configs = {
    "2 Lotes Expirados": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Não Disponível (data futura)": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Disponível Limitado Lotado": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Disponível Ilimitado": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Disponível Limitado (5 vagas)": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Disponível e 1 Não-iniciado": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Disponível Limitado Lotado e 1 Disponível Limitado (5 vagas)": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Disponível Limitado Lotado e 1 Não-iniciado": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Expirado e 1 Disponível Ilimitado": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Expirado e 1 Disponível Limitado (5 vagas)": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    },
    "1 Lote Expirado e 1 Disponível Limitado Lotado": {
        'date_start': '',
        'date_end': '',
        'published': False,
        'lots': [

        ],
    }
}


def create_event(data):
    event_dict = {
        "name": event_name,
        "organization": 1,
        "category": 2,
        "subscription_type": "by_lots",
        "date_start": data.get('date_start'),
        "date_end": data.get('date_end'),
        "published": data.get('published', False),
    }

    info['event'] = Event.objecs.create(**event_dict)
    Info.objects.create(**info)


def create_lot(data):
    pass


for event_name in event_by_lots_configs.keys():

    data = event_by_lots_configs[event_name]

    create_event(data)

    for lot in data.get('lots', []):
        create_lot(lot)
