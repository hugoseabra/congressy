from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.permissions import BasePermission

from .models import Service, Product


class IsNotFreeEvent(BasePermission):
    """
        Allows access only to not free events
    """

    def has_permission(self, request, view):
        optional_type = view.basename
        optional_pk = view.kwargs.get('pk')
        optional = None

        # try:
        #     if optional_type == 'service':
        #         optional = Service.objects.get(pk=optional_pk)
        #     elif optional_type == 'product':
        #         optional = Product.objects.get(pk=optional_pk)
        # except ObjectDoesNotExist:
        #     raise NotFound()
        #
        # if optional is None:
        #     raise NotFound()
        #
        # for lot in optional.lot_category.event.lots.all():
        #     if lot.price and lot.price > 0:
        #         return True
        #
        # if optional.lot_category.event.event_type == \
        #         optional.lot_category.event.EVENT_TYPE_FREE:
        #     raise PermissionDenied()

        return True

