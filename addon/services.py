from addon import managers
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


class SubscriptionProductService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.SubscriptionProductManager


class SubscriptionServiceService(services.ApplicationService):
    """ Application service. """
    manager_class = managers.SubscriptionServiceManager
