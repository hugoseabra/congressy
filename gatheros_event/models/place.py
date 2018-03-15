# pylint: disable=W5101,E0401
"""
Local onde o evento vai acontecer, para facilitar a orientação aos possíveis
participantes e exibição de mapa.
"""
import os

from django.db import models

from kanu_locations.models import City
from . import Event
from .mixins import GatherosModelMixin


def get_image_path(_, filename):
    """ Resgata localização onde as imagens serão inseridas. """
    return os.path.join('place', os.path.basename(filename))


class Place(models.Model, GatherosModelMixin):
    """Local de evento."""

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='place'
    )
    show_location = models.BooleanField(
        default=False,
        verbose_name='ativar localização no site',
        help_text='Marque para mostrar a localização do evento no site.'
    )
    show_address = models.BooleanField(
        default=False,
        verbose_name='mostrar endereço',
        help_text='Exibir informações do local evento.'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='nome do local',
        blank=True,
        null=True
    )
    city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        verbose_name='cidade',
        blank=True,
        null=True,
    )
    phone = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        verbose_name='telefone'
    )
    long = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='longitude'
    )
    lat = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='latitude'
    )
    zoom = models.CharField(
        default=18,
        max_length=4,
        blank=True,
        null=True,
        verbose_name='zoom do mapa'
    )

    zip_code = models.CharField(
        max_length=8,
        verbose_name='CEP',
        blank=True,
        null=True
    )
    street = models.CharField(
        max_length=255,
        verbose_name='logradouro (rua, avenida, etc.)',
        blank=True,
        null=True
    )
    number = models.CharField(
        max_length=20,
        verbose_name='número',
        blank=True,
        null=True,
        help_text="Caso não tenha, informar S/N."
    )
    complement = models.CharField(
        max_length=255,
        verbose_name='complemento',
        blank=True,
        null=True
    )
    village = models.CharField(
        max_length=255,
        verbose_name='bairro',
        blank=True,
        null=True
    )
    reference = models.CharField(
        max_length=255,
        verbose_name='referência',
        blank=True,
        null=True,
        help_text="Alguma informação para ajudar a chegar ao local."
    )

    # google_streetview_link = models.URLField(
    #     verbose_name='Link do Google StreetView',
    #     blank=True,
    #     null=True,
    #     help_text="Informações para exibir imagens do local"
    # )
    #
    # google_streetview_img = models.ImageField(
    #     upload_to=get_image_path,
    #     blank=True,
    #     null=True,
    #     verbose_name='Imagem Google StreetView',
    #     help_text="Imagem estática do Google StreetView"
    # )
    #
    # google_maps_link = models.URLField(
    #     verbose_name='Link do Google Maps',
    #     blank=True,
    #     null=True,
    #     help_text="Informações para exibir mapa do local"
    # )
    #
    # google_maps_img = models.ImageField(
    #     upload_to=get_image_path,
    #     blank=True,
    #     null=True,
    #     verbose_name='Imagem Google Maps',
    #     help_text="Imagem estática do Google Maps"
    # )

    class Meta:
        verbose_name = 'local de evento'
        verbose_name_plural = 'locais de Evento'
        ordering = ['name']

    def __str__(self):
        return '{} ({})'.format(self.name, self.event.name)

    # noinspection PyMethodMayBeStatic
    def _add_prefix(self, *args, **kwargs):
        if [arg for arg in args if arg]:
            return kwargs.get('prefix', '')

        return ''

    def get_formatted_zip_code(self):
        """
        Recupera CEP formatado.
        :return: string
        """
        return '{0}.{1}-{2}'.format(
            self.zip_code[:2],
            self.zip_code[2:5],
            self.zip_code[5:]
        )

    def get_complete_address(self):
        """
        Recupera endereço completo e formatado.
        :return: string
        """
        address = ''
        if self.street:
            address += self.street

        if self.number:
            address += self._add_prefix(
                self.street,
                prefix=', '
            ) + 'Nº. ' + self.number

        if self.complement:
            address += self._add_prefix(
                self.street,
                self.number,
                prefix=', '
            ) + self.complement

        if self.village:
            address += self._add_prefix(
                self.street,
                self.number,
                self.complement,
                prefix=', '
            ) + self.village

        if self.zip_code:
            address += self._add_prefix(
                self.street,
                self.number,
                self.complement,
                self.village,
                prefix=', '
            ) + 'CEP: ' + self.get_formatted_zip_code()

            if self.city:
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
