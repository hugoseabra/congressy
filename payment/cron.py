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
            subs_pks = list()
            for sub in irregularities:
                subs_pks.append(sub.pk)

            msg1 = 'Inscrições pagas e não confirmadas: {}'.format(
                len(subs_pks)
            )

            msg2 = "\n  - " + "\n  - ".join(
                [str(sub_pk) for sub_pk in subs_pks]
            )

            sentry_log(
                message=msg1 + msg2,
                type='error',
                notify_admins=True,
            )

            print(msg1 + msg2)

            return msg1
