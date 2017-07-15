""" Mixin de models do Gatheros que centraliza funcionalidades. """
from django.db.models.fields import related
from core.model.deletable import DeletableModelMixin


class GatherosModelMixin(DeletableModelMixin):
    """Gatheros Model Mixin"""
    def can_write_to_field(self, field_name):
        """
        Verifica se valor do campo do model pode ser inserido diretamente.
        """
        related_classes = [
            related.ManyToManyDescriptor,
            related.ManyToManyField,
            related.ManyToManyRel,
            related.ManyToOneRel,
        ]

        if not hasattr(self, field_name):
            return False

        model_field = self._meta.get_field(field_name)
        for related_class in related_classes:
            if isinstance(model_field, related_class):
                return False

        return True
