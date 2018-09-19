from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import BasePermission

from gatheros_event.helpers.event_business import is_free_event
from .models import Service, Product


class IsNotFreeEvent(BasePermission):
    """
        Allows access only to not free events
    """

    def has_permission(self, request, view):
        optional_type = view.basename
        optional_pk = view.kwargs.get('pk')
        optional = None

        try:
            if optional_type == 'service':
                optional = Service.objects.get(pk=optional_pk)
            elif optional_type == 'product':
                optional = Product.objects.get(pk=optional_pk)
        except ObjectDoesNotExist:
            raise NotFound()

        if optional is None:
            raise NotFound()

        event = optional.lot_category.event

        if is_free_event(event):
            raise PermissionDenied()

        return True
