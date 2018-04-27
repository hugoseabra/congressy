from datetime import datetime
from addon import constants, managers
from base import services


class ThemeService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.ThemeManager


class OptionalTypeService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.OptionalTypeManager


class ProductService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.ProductManager


class ServiceService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.ServiceManager


def remove_expired_optional_subscription(
        subscription_optional,
        min_days=constants.MINIMUM_RELEASE_DAYS):
    """
        Verifica se a inscrição de um opcional será excluída
    """
    subscription = subscription_optional.subscription
    if subscription.status == subscription.CONFIRMED_STATUS:
        return False

    diff_datetime = datetime.now() - subscription.created

    if diff_datetime.days <= int(min_days):
        return False

    subscription_optional.delete()
    return True


class SubscriptionServiceReleaseMixin(object):
    """
        Mixin para processar liberação de opcional através da verificação
        da inscrição do opcional
    """

    def release_optional(self):
        """
            Exclui Inscrição de Opcional caso a inscrição informada não esteja
            confirmada e o número de dias desde a criação da mesma for maior do
            que o configurado no sistema.

            Importante notar que este liberação é para quando se tem a
            Inscrição de Opcional existente, ou seja, quando existe Instance
            no Manager.
        """
        has_instance = hasattr(self.manager, 'instance')

        # Se manager não possui instancia de Inscrição de opcional, não há
        # nada a fazer.
        if has_instance is False or not self.manager.instance.pk:
            return False

        return remove_expired_optional_subscription(self.manager.instance)


class SubscriptionProductService(
    services.ApplicationService,
    SubscriptionServiceReleaseMixin
):
    """ Application service. """
    manager_class = managers.SubscriptionProductManager


class SubscriptionServiceService(
    services.ApplicationService,
    SubscriptionServiceReleaseMixin
):
    """ Application service. """
    manager_class = managers.SubscriptionServiceManager
