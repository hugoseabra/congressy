from datetime import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q

from addon.models import Product, Service, Theme, SubscriptionService, \
    SubscriptionProduct
from attendance.models import AttendanceService, Checkin, Checkout
from core.cli.mixins import CliInteractionMixin
from gatheros_event.models import Person
from gatheros_subscription.management.cmd_event_mixins import CommandEventMixin
from gatheros_subscription.models import Subscription, EventSurvey, \
    LotCategory, Lot
from payment.models import Transaction, TransactionStatus
from survey.models import Author, Question, Option, Answer, Survey


class Command(BaseCommand, CliInteractionMixin, CommandEventMixin):
    help = "Coleta registros editados e/ou criados a partir de uma" \
           " data e hora."

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, nargs='?')

    def handle(self, *args, **options):
        event = self._get_event(pk=options.get('event_id'))

        print('==============================================================')
        self.collect_categories_and_lots(event)
        self.collect_surveys(event)
        self.collect_addons(event)
        self.collect_attendance_services(event)

        sub_pks = list()

        self.collect_subscriptions(event)

    def collect_categories_and_lots(self, event):
        categories = LotCategory.objects.filter(event_id=event.pk)
        self._collect_data('gatheros_subscription.lotcategory', categories)

        lots = Lot.objects.filter(event_id=event.pk)
        self._collect_data('gatheros_subscription.lot', lots)

    def collect_surveys(self, event):
        event_surveys = EventSurvey.objects.filter(event_id=event.pk)
        self._collect_data('gatheros_subscription.eventsurvey', event_surveys)

        survey_pks = [s.survey_id for s in event_surveys]
        surveys = Survey.objects.filter(pk__in=survey_pks)
        self._collect_data('survey.survey', surveys)

        questions = Question.objects.filter(survey_id__in=survey_pks)
        self._collect_data('survey.question', questions)

        question_pks = [q.pk for q in questions]
        options = Option.objects.filter(question_id__in=question_pks)
        self._collect_data('survey.option', options)

    def collect_addons(self, event):
        products = Product.objects.filter(lot_category__event_id=event.pk)
        self._collect_data('addon.product', products)

        services = Service.objects.filter(lot_category__event_id=event.pk)
        self._collect_data('addon.service', services)

        theme_pks = [s.theme_id for s in services]
        themes = Theme.objects.filter(pk__in=theme_pks)
        self._collect_data('addon.theme', themes)

    def collect_attendance_services(self, event):
        collection = AttendanceService.objects.filter(event_id=event.pk)
        self._collect_data('attendance.attendanceservice', collection)

    def collect_subscriptions(self, event):
        subscriptions = Subscription.objects.filter(event_id=event.pk)
        self._collect_data('gatheros_subscription.subscription', subscriptions)

        sub_pks = [s.pk for s in subscriptions]

        person_pks = [sub.person_id for sub in subscriptions]
        persons = Person.objects.filter(pk__in=person_pks)
        self._collect_data('gatheros_event.person', persons)

        user_pks = [p.user_id for p in persons if p.user_id]
        users = User.objects.filter(pk__in=user_pks)
        self._collect_data('auth.user', users)

        # SURVEY
        sub_author_pks = [sub.author_id for sub in subscriptions]
        authors = Author.objects.filter(
            Q(pk__in=sub_author_pks, ) | Q(user_id__in=user_pks, )
        )
        self._collect_data('survey.author', authors)

        author_pks = [a.pk for a in authors]
        answers = Answer.objects.filter(author_id__in=author_pks)
        self._collect_data('survey.answer', answers)

        # ADDON
        sub_services = SubscriptionService.objects.filter(
            subscription_id__in=sub_pks,
        )
        self._collect_data('addon.subscriptionservice', sub_services)

        sub_products = SubscriptionProduct.objects.filter(
            subscription_id__in=sub_pks,
        )
        self._collect_data('addon.subscriptionproduct', sub_products)

        # Transaction
        transactions = Transaction.objects.filter(subscription_id__in=sub_pks)
        self._collect_data('payment.transaction', transactions)

        trans_pks = [t.pk for t in transactions]
        transaction_statuses = TransactionStatus.objects.filter(
            transaction_id__in=trans_pks,
        )
        self._collect_data('payment.transactionstatus', transaction_statuses)

        # Attendances
        checkins = Checkin.objects.filter(subscription_id__in=sub_pks)
        self._collect_data('attendance.checkin', checkins)

        checkouts = Checkin.objects.filter(subscription_id__in=sub_pks)
        self._collect_data('attendance.checkout', checkouts)

    def _collect_data(self, name, collection):
        num_records = len(collection)

        if num_records == 0:
            return

        print()
        self.stdout.write(
            '{}: {} registros'.format(
                name,
                self.style.SUCCESS(str(num_records))
            )
        )

        self.progress_bar(
            0,
            num_records,
            prefix='Progress:',
            suffix='Complete',
            length=40
        )
        processed = 0

        # gatheros_event.person
        for item in collection:
            # Força sincronização mesmo sem alterar o registro.
            item.sync_force = True
            item.save()
            processed += 1

            self.progress_bar(
                processed,
                num_records,
                prefix='Progress:',
                suffix='Complete',
                length=40
            )
