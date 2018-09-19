from django.contrib.auth.models import User
from django_cron import CronJobBase, Schedule

from gatheros_subscription.models import Subscription
from payment.models import Transaction
from core.helpers import sentry_log


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
            subs_pk = list()
            for sub in irregularities:
                subs_pk.append(sub.pk)

            msg = 'Temos {} inscrições pendentes com pagamentos confirmados'\
                .format(len(subs_pk))
            
            subs_pk = ', '.join(str(e) for e in subs_pk)

            print('{}: {}'.format(msg, subs_pk))

            sentry_log(
                message=msg,
                type='error',
                extra_data={
                    'subscriptions_pk': subs_pk
                },
                notify_admins=True,
            )
