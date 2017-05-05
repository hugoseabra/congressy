from django.db import models
from kanu_locations.models import City

from . import Organization


# @TODO Usar GeoDjango para coodenadas
# @TODO Ver integração com Google Maps

class Place(models.Model):
    name = models.CharField(max_length=255, verbose_name='nome')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, verbose_name='organização',
                                     related_name='places')
    city = models.ForeignKey(City, on_delete=models.PROTECT, verbose_name='cidade')

    phone = models.CharField(max_length=9, blank=True, null=True, verbose_name='telefone')
    long = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    lat = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)

    zip_code = models.CharField(max_length=8, verbose_name='CEP', blank=True, null=True)
    street = models.CharField(max_length=255, verbose_name='logradouro (rua, avenida, etc.)', blank=True, null=True)
    number = models.CharField(max_length=20, verbose_name='número', blank=True, null=True,
                              help_text="Caso não tenha, informar S/N.")
    complement = models.CharField(max_length=255, verbose_name='complemento', blank=True, null=True)
    village = models.CharField(max_length=255, verbose_name='bairro', blank=True, null=True)
    reference = models.CharField(max_length=255, verbose_name='referência', blank=True, null=True,
                                 help_text="Alguma informação para ajudar a chegar ao local.")

    google_street_view_link = models.TextField(
        verbose_name='Link do Google StreetView',
        blank=True,
        null=True,
        help_text="Informações do Google StreetView para exibir imagens do local no site."
    )

    class Meta:
        verbose_name = 'local de Evento'
        verbose_name_plural = 'locais de Evento'
        ordering = ['name']

    def __str__( self ):
        return '{} ({})'.format(self.name, self.organization.name)

    def _add_prefix( self, *args, prefix=', ' ):
        for arg in args:
            if arg:
                return prefix

        return ''

    def get_formatted_zip_code( self ):
        zc = self.zip_code
        return '{0}.{1}-{2}'.format(zc[:2], zc[2:5], zc[5:])

    def get_complete_address( self ):
        address = ''
        if self.street:
            address += self.street

        if self.number:
            address += self._add_prefix(self.street) + 'Nº. ' + self.number

        if self.complement:
            address += self._add_prefix(self.street, self.number) + self.complement

        if self.village:
            address += self._add_prefix(self.street, self.number, self.complement) + self.village

        if self.zip_code:
            address += self._add_prefix(self.street, self.number, self.complement, self.village) \
                       + 'CEP: ' + self.get_formatted_zip_code()

        address += self._add_prefix(
            self.street,
            self.number,
            self.complement,
            self.village,
            self.zip_code,
            prefix=' - '
        ) + self.city.name + '-' + self.city.uf + '.'

        if self.reference:
            address += ' Referência: ' + self.reference

        return address
