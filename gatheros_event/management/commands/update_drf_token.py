from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from gatheros_event.models import Member, Organization
from django.contrib.auth.models import User
from django.db.models import Count


class Command(BaseCommand):
    help = 'Atualiza token de um usuário.'

    def add_arguments(self, parser):
        parser.add_argument('-uid',
                            '--user_id',
                            dest='user_id',
                            type=int,
                            required=True,
                            help='ID do usuário')
        parser.add_argument('-t',
                            '--token',
                            dest='token',
                            type=str,
                            required=True,
                            help='token desejado')

    def handle(self, *args, **options):

        try:
            Token.objects.get(user_id=options.get('user_id')).delete()
        except Token.DoesNotExist:
            pass

        token = Token(user_id=options.get('user_id'))
        token.key = options.get('token')
        token.save()
