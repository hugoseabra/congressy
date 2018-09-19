from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from gatheros_event.models import Event, FeatureConfiguration, FeatureManagement
from mailer.services import notify_new_event


@receiver(post_save, sender=Event)
def create_feature_configuration(instance, raw, created, **_):
    if raw is True:
        return

    if created is True:
        try:
            instance.feature_configuration
        except AttributeError:
            FeatureConfiguration.objects.create(
                event=instance,
                feature_certificate=True,
                feature_internal_subscription=True,
                feature_multi_lots=True,
            )

        instance.feature_configuration.save()


@receiver(post_save, sender=Event)
def create_feature_management(instance, raw, created, **_):
    if raw is True:
        return

    if created is True:
        try:
            config = instance.feature_management
        except AttributeError:
            config = FeatureManagement.objects.create(event=instance)

        config.feature_products = instance.has_optionals
        config.feature_services = instance.has_extra_activities
        config.feature_checkin = instance.has_checkin
        config.feature_certificate = instance.has_certificate
        config.feature_survey = instance.has_survey

        config.save()


@receiver(post_save, sender=Event)
def send_email_on_new_event(instance, raw, created, **_):
    if raw is True:
        return

    if created and settings.DEBUG is False:
        notify_new_event(instance)
