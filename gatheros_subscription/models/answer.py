from django.db import models
from . import Field, Subscription


class Answer(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, verbose_name='inscrição',
                                     related_name='answers')
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name='campo', related_name='answers')
    value = models.TextField(verbose_name='valor', null=True, blank=True)

    class Meta:
        verbose_name = 'resposta'
        verbose_name_plural = 'respostas'
        ordering = ['field']
        unique_together = (('subscription', 'field'),)

    def __str__(self):
        return '{} - {}'.format(self.field, self.value)
