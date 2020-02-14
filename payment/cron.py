from django.core.management import call_command
from django.db.models import Count
from django_cron import CronJobBase, Schedule

from core.helpers import sentry_log
from gatheros_subscription.models import Subscription
from payment.models import Transaction


class SubscriptionPaidAndIncomplete(CronJobBase):
    RUN_EVERY_MINS = 60  # every hours
    RETRY_AFTER_FAILURE_MINS = 5

    code = 'payment.cron.SubscriptionPaidAndIncomplete'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)

    def do(self):
        irregularities = Subscription.objects.annotate(
            num_trans=Count('transactions')
        ).filter(
            status=Subscription.AWAITING_STATUS,
            origin=Subscription.DEVICE_ORIGIN_HOTSITE,
            transactions__status=Transaction.PAID,
            lot__price__gt=0,
            num_trans__gt=0,
        )

        if irregularities.count() == 0:
            return

        sub_txt = '\n'
        for sub in irregularities:
            sub_txt += "    - Subscription pk: {} \n" \
                       "    - Transaction pk: {}\n" \
                       "    - Event: {}(ID: {})\n" \
                       "    - Person: {}(ID: {})\n" \
                       "    - E-mail: {}\n\n".format(
                sub.pk,
                sub.transactions.last().pk,
                sub.event.name,
                sub.event.pk,
                sub.person.name,
                sub.person.pk,
                sub.person.email,
            )

        msg1 = 'Inscrições pagas e não confirmadas: {}'.format(
            irregularities.count(),
        )

        msg2 = sub_txt

        sentry_log(
            message=msg1 + msg2,
            type='error',
            notify_admins=True,
        )

        call_command('normalize_paid_subscription_with_status_pending')

        print(msg1 + msg2)

        return msg1


class CheckPayables(CronJobBase):
    """
    Verifica recebíveis que não irão mais ser processados por postback.
    """
    RUN_EVERY_MINS = 15  # every 15 minutes
    RETRY_AFTER_FAILURE_MINS = 5

    code = 'payment.cron.CheckPayables'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)

    def do(self):
        call_command('update_payables')
