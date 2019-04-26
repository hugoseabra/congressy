from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.transaction import atomic

from gatheros_event.models import Member, Organization
from gatheros_subscription.models import Subscription
from mailer.services import notify_new_user_and_free_subscription


class Command(BaseCommand):
    help = 'Criar usuários (se não tiverem) de participantes de uma' \
           ' determinada categoria e lote e e enviar o e-mail de boas-vindas.'

    def add_arguments(self, parser):
        parser.add_argument(
            'subscription_id',
            help='UUID da Inscrição',
            type=str,
        )

    def handle(self, *args, **options):

        uuid = options['subscription_id']

        try:
            with atomic():
                sub = Subscription.objects.get(uuid=uuid)

                if sub.free is False:
                    self.stderr.write(
                        "Inscrição '{}' não é gratuita.".format(uuid)
                    )
                    return

                person = sub.person

                if person.user_id:
                    user = person.user
                    self.stdout.write(self.style.SUCCESS(
                        'User existente: {} - {}'.format(user.get_full_name(),
                                                         user.pk)
                    ))
                    return

                split_name = person.name.upper().split(' ')
                first_name = split_name[0]
                last_name = split_name[-1]

                try:
                    user = User.objects.get(email=person.email)
                    self.stderr.write(
                        "Usuário já existe: {} ({})".format(
                            user.email,
                            user.pk,
                        )
                    )
                    return


                except User.DoesNotExist:
                    user = User.objects.create_user(
                        person.email,
                        person.email,
                        'mudar123',
                        first_name=first_name,
                        last_name=last_name,
                    )

                person.user = user
                person.save()

                if not person.members.count():
                    org = Organization(internal=False, name=person.name)

                    for attr, value in person.get_profile_data().items():
                        setattr(org, attr, value)

                    org.save()

                    Member.objects.create(
                        organization=org,
                        person=person,
                        group=Member.ADMIN
                    )

                notify_new_user_and_free_subscription(
                    event=sub.event,
                    subscription=sub,
                )

                self.stdout.write(self.style.SUCCESS(
                    'User: {} - {}'.format(user.get_full_name(), user.pk)
                ))

        except Subscription.DoesNotExist:
            self.stderr.write("Inscrição '{}' não encontrada.".format(uuid))
