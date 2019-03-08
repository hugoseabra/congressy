from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Criar usuários de participantes ' \
           '(se não tiverem) e e enviar o e-mail de boas-vindas'

    # def add_arguments(self, parser):
    #     parser.add_argument('from_product_id', type=int)
    #     parser.add_argument('to_category_id', type=int)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(
            'HELLO WORLD'
        ))
