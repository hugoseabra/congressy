from associate.models import Associate
from base import managers


class AssociateManager(managers.Manager):
    """ Manager de associado. """

    class Meta:
        model = Associate
        fields = '__all__'
