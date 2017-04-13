from django.db import models
from kanu_locations.models import City
from . import Organization


class Place(models.Model):
    name = models.CharField(max_length=255, verbose_name='nome')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='organização',
                                     related_name='addresses')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='cidade')

    zip_code = models.CharField(max_length=255, verbose_name='CEP', blank=True, null=True)
    street = models.CharField(max_length=255, verbose_name='logradouro (rua, avenida, etc.)', blank=True, null=True)
    complement = models.CharField(max_length=255, verbose_name='complemento', blank=True, null=True)
    village = models.CharField(max_length=255, verbose_name='bairro', blank=True, null=True)
    reference = models.CharField(max_length=255, verbose_name='referência', blank=True, null=True)

    class Meta:
        verbose_name = 'local de Evento'
        verbose_name_plural = 'locais de Evento'
        ordering = ['name']

    def __str__(self):
        return '{} ({})'.format(self.name, self.organization.name)
