from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from gatheros_event.models import Organization


class Command(BaseCommand):
    help = 'Resetar todas as senhas de Usuario - AMBIENTE DEV APENAS'

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.ERROR(
                '\n\n\tWARNING: Esse script é pra uso apenas de'
                ' desenvolvimento e irá resetar todas as senhas de usuarios no'
                ' banco de dados para 123.\n\n'
            )
        )

        text = input("TEM CERTEZA ABSOLUTA QUE DESEJA RODA ESSE SCRIPT? "
                     "(DIGITE SIM PARA CONTINUAR): ")

        if text.upper() != "SIM":
            return

        now = datetime.now()
        days_ago = now - timedelta(days=30)
        days_ahead = now + timedelta(days=30)

        org_qs = Organization.objects.filter(
            events__date_start__gte=days_ago,
            events__date_start__lte=now,
            events__date_end__lte=days_ahead
        ).distinct().order_by('name')

        person_pks = list()

        for org in org_qs:
            for m in org.members.all():
                if m.person_id not in person_pks:
                    person_pks.append(m.person_id)

        users = User.objects.filter(
            person__uuid__in=person_pks,
            person__isnull=False,
            last_login__isnull=False,
        )

        num_users = users.count()
        self.stdout.write(self.style.SUCCESS(
            '- Users found: {}'.format(num_users)
        ))

        self.progress_bar(
            0,
            num_users,
            prefix='Progress:',
            suffix='Complete',
            length=50
        )

        for i, user in enumerate(users):
            user.set_password('123')
            user.save()
            self.progress_bar(
                i + 1,
                num_users,
                prefix='Progress:',
                suffix='Complete',
                length=50
            )

    @staticmethod
    def progress_bar(iteration, total, prefix='', suffix='', decimals=1,
                     length=100, fill='█'):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent
                                      complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(
            100 * (iteration / float(total)))
        filled_length = int(length * iteration // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
        # Print New Line on Complete
        if iteration == total:
            print()
