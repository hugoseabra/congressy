from datetime import datetime

from django.core.management import call_command
from django.db.transaction import atomic
from django_cron import CronJobBase, Schedule

from core.helpers import sentry_log
from gatheros_subscription.models import Subscription
from payment.models import Transaction, SplitRule
from payment.payable.updater import update_payables


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
            transactions__manual=False,
            origin=Subscription.DEVICE_ORIGIN_HOTSITE,
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
                sub.transactions.first().pk,
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


class SubscriptionPaidAndIncomplete(CronJobBase):
    RUN_EVERY_MINS = 60  # every hours
    RETRY_AFTER_FAILURE_MINS = 5

    code = 'payment.cron.SubscriptionPaidAndIncomplete'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)

    def do(self):
        incomplete_subs = Subscription.objects.filter(
            status=Subscription.CONFIRMED_STATUS,
            completed=False,
        )

        if incomplete_subs.count() == 0:
            return

        sub_txt = '\n'
        with atomic():
            for sub in incomplete_subs:
                sub.completed = True
                sub.save()

                sub_txt += "    - Subscription pk: {} \n"
                sub_txt += "    - Event: {}(ID: {})\n"
                sub_txt += "    - Person: {}(ID: {})\n"
                sub_txt += "    - E-mail: {}\n\n"

                sub_txt = sub_txt.format(
                    sub.pk,
                    sub.event.name,
                    sub.event.pk,
                    sub.person.name,
                    sub.person.pk,
                    sub.person.email,
                )

            msg1 = 'Inscrições pagas e incompletas: {}'.format(
                incomplete_subs.count(),
            )

            msg2 = sub_txt

            sentry_log(
                message=msg1 + msg2,
                type='error',
                notify_admins=True,
            )

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
        # Verifica todas as regras que estejam com recebíveis agendadas para
        # verificação, excluindo as regras que não possuem recebíveis agendados
        split_rule_qs = SplitRule.objects.filter(
            payables__next_check__lte=datetime.now(),
        ).exclude(
            payables__next_check__isnull=True,
        )

        for split_rule in split_rule_qs[:50]:
            update_payables(split_rule)
