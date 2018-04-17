from django.contrib.auth.models import User
from django_cron import CronJobBase, Schedule


class MyCronJob(CronJobBase):
    RUN_EVERY_MINS = 1  # every hours
    RETRY_AFTER_FAILURE_MINS = 5

    code = 'cron.MyCronJob'
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS,
                        retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)

    def do(self):
        message = 'Active users: %d' % User.objects.count()
        print(message)
