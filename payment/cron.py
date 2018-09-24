from django.contrib.auth.models import User
from django_cron import CronJobBase, Schedule

from core.helpers import sentry_log
from gatheros_subscription.models import Subscription
from payment.models import Transaction


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every hours
    RETRY_AFTER_FAILURE_MINS = 5

    code = 'cron.MyCronJob'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)

    def do(self):
        message = 'Active users: %d' % User.objects.count()
        print(message)


class SubscriptionStatusIrregularityTestJob(CronJobBase):
    RUN_EVERY_MINS = 60  # every hours
    RETRY_AFTER_FAILURE_MINS = 5

    code = 'payment.cron.SubscriptionStatusIrregularityTestJob'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)

    def do(self):
        irregularities = Subscription.objects.filter(
            status=Subscription.AWAITING_STATUS,
            transactions__status=Transaction.PAID,
        )

        if irregularities.count() > 0:
            sub_txt = '\n'
            for sub in irregularities:
                sub_txt += '    - Subscription pk: {} - ' \
                           'Last Transaction pk: {}\n' \
                           ''.format(sub.pk, sub.transactions.last().pk)

            msg1 = 'Inscrições pagas e não confirmadas: {}'.format(
                irregularities.count(),
            )

            msg2 = sub_txt

            sentry_log(
                message=msg1 + msg2,
                type='error',
                notify_admins=True,
            )

            print(msg1 + msg2)

            return msg1
