# pylint: disable=W5101

"""
    Representação do serviços de opcional(add ons)
"""

from django.db import models

from addon import rules
from base.models import EntityMixin


class Session(EntityMixin, models.Model):
    """
        Sessão de Opcional, onde serão definidas a data de início e fim em que
        um Opcional estará ativo e se restrito como único opcional dentro
        permitido dentro do intervalo.
    """
    rule_instances = (
        rules.MustDateEndAfterDateStart,
    )

    date_start = models.DateTimeField(verbose_name="data inicial", )
    date_end = models.DateTimeField(verbose_name="data final", )

    restrict_unique = models.BooleanField(
        default=False,
        verbose_name='restringir como único',
        help_text='Restringir como sessão dentro do intervalo de tempo.'
    )

    def __str__(self):
        str = 'Session: {} a {}'.format(
            self.date_start.strftime('%d/%m/%Y %H:%M'),
            self.date_end.strftime('%d/%m/%Y %H:%M'),
        )

        if self.restrict_unique:
            str += ' (restricted)'

        return str
