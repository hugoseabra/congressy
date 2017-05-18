"""Gatheros testcase mixin"""

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase


class GatherosTestCase(TestCase):
    """Mixing for Django testcase class"""

    def _trigger_validation_error(self, callback, params=None, field=None):
        self._trigger_error(
            error_class=ValidationError,
            callback=callback,
            params=params,
            field=field
        )

    def _trigger_integrity_error(self, callback, params=None):
        self._trigger_error(
            error_class=IntegrityError,
            callback=callback,
            params=params
        )

    def _trigger_error(self, error_class, callback, params, field=None):
        if not params:
            params = []

        with self.assertRaises(error_class) as exc:
            callback(*params)

        if field:
            self.assertIn(field, dict(exc.exception))

    # noinspection PyMethodMayBeStatic
    def _create_model(self, model_class, data, persist=False, **kwargs):
        data.update(**kwargs)
        entity = model_class(**data)

        if persist:
            entity.save()

        return entity
