# pylint: disable=W5101
"""
Models de certificados
"""

from decimal import Decimal

import os
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from stdimage import StdImageField
from stdimage.validators import MinSizeValidator


def get_image_path(instance, filename):
    """ Resgata localização onde as imagens serão inseridas. """
    return os.path.join('event', str(instance.event.id), filename)


class Certificate(models.Model):
    """ Certificado de evento."""

    MANAGE_TO_PDF_RATIO = Decimal(73.038516)

    class Meta:
        verbose_name = 'certificado'
        verbose_name_plural = 'certificados'

    event = models.OneToOneField(
        'gatheros_event.Event',
        on_delete=models.CASCADE,
        verbose_name='evento',
        related_name='certificate'
    )

    background_image = StdImageField(
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem de fundo do certificado do evento',
        variations={
            'default': (1402, 991),
            'regular': (1024, 724),
            'thumbnail': (283, 200),
        },
        validators=[MinSizeValidator(1402, 991)],
        help_text="Imagem de fundo300 do certificado, mínimo de: "
                  "1402px largura x "
                  "991px altura.(png/jpg) "
                  "<a  target='_blank'"
                  "href='http://via.placeholder.com/1402x991'>Exemplo"
                  "</a>"
    )

    text_content = models.TextField(
        default='Certificamos que {{NOME}} participou do evento {{EVENTO}}',
        verbose_name='texto',
        help_text='Texto principal do certificado.',
    )

    text_font_size = models.FloatField(
        default=20,
        verbose_name='tamanho da fonte do texto',
        help_text='Tamanho da fonte em (px)',
        null=True,
        blank=True,
    )

    text_width = models.FloatField(
        default=634,
        verbose_name='largura do bloco do texto',
        help_text='Tamanho (px) da largura do bloco.',
        null=True,
        blank=True,
    )

    text_height = models.FloatField(
        default=348,
        verbose_name='altura do bloco do texto',
        help_text='Tamanho (px) da altura do bloco.',
        null=True,
        blank=True,
    )

    text_line_height = models.FloatField(
        default=22,
        verbose_name='espaço entre-linhas do texto',
        help_text='Espaço entre-linhas (cm) do conteúdo.',
        null=True,
        blank=True,
    )

    text_position_x = models.FloatField(
        default=191,
        verbose_name='posição X do texto',
        help_text='Distância do bloco no eixo X.',
        null=True,
        blank=True,
    )

    text_position_y = models.FloatField(
        default=309,
        verbose_name='posição Y do texto',
        help_text='Distância do bloco no eixo Y.',
        null=True,
        blank=True,
    )

    title_content = models.CharField(
        default='Certificado',
        max_length=50,
        verbose_name='título',
        null=True,
        blank=True,
    )

    title_font_size = models.FloatField(
        default=60,
        verbose_name='tamanho da fonte do título',
        help_text='Tamanho da fonte em (px)',
        null=True,
        blank=True,
    )

    title_position_x = models.FloatField(
        default=286,
        verbose_name='posição X do título',
        help_text='Distância do bloco no eixo X.',
        null=True,
        blank=True,
    )

    title_position_y = models.FloatField(
        default=192,
        max_length=5,
        verbose_name='posição Y do título',
        help_text='distância do bloco no eixo Y.',
        null=True,
        blank=True,
    )

    title_hide = models.BooleanField(
        default=False,
        verbose_name='esconder título',
    )

    date_font_size = models.FloatField(
        default=20,
        verbose_name='tamanho da fonte da data',
        help_text='Tamanho da fonte em (px)',
        null=True,
        blank=True,
    )

    date_position_x = models.FloatField(
        default=15,
        verbose_name='posição X da data',
        help_text='Distância do bloco no eixo X.',
        null=True,
        blank=True,
    )

    date_position_y = models.FloatField(
        default=463,
        verbose_name='posição Y da data',
        help_text='Distância do bloco no eixo Y.',
        null=True,
        blank=True,
    )

    date_hide = models.BooleanField(
        default=False,
        verbose_name='esconder data',
    )

    event_location = models.CharField(
        max_length=50,
        verbose_name='local do evento',
        null=True,
        blank=True,
    )

    text_center = models.BooleanField(
        default=False,
        verbose_name='centralizar texto',
    )

    only_attending_participantes = models.BooleanField(
        default=True,
        verbose_name='apenas para presentes(check-in)',
    )

    font_color = models.CharField(
        max_length=20,
        verbose_name='cor da fonte',
        null=True,
        blank=True,
        default='#565656'
    )

    def __str__(self):
        return '{}'.format(self.event)


    @property
    def converted_text_font_size(self):
        return Decimal((self.text_font_size * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_text_width(self):
        return Decimal((self.text_width * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_text_height(self):
        return Decimal((self.text_height * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_text_line_height(self):
        return Decimal((self.text_line_height * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_text_position_x(self):
        return Decimal((self.text_position_x * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_text_position_y(self):
        return Decimal((self.text_position_y * 100)) / self.MANAGE_TO_PDF_RATIO

    # TITLE
    @property
    def converted_title_content(self):
        return Decimal((self.title_content * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_title_font_size(self):
        return Decimal((self.title_font_size * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_title_position_x(self):
        return Decimal((self.title_position_x * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_title_position_y(self):
        return Decimal((self.title_position_y * 100)) / self.MANAGE_TO_PDF_RATIO

    # DATE
    @property
    def converted_date_font_size(self):
        return Decimal((self.date_font_size * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_date_position_x(self):
        return Decimal((self.date_position_x * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def converted_date_position_y(self):
        return Decimal((self.date_position_y * 100)) / self.MANAGE_TO_PDF_RATIO

    @property
    def is_ready(self):

        if not self.background_image:
            return False

        if not hasattr(self.background_image, 'default'):
            return False

        if not self.background_image.default.readable():
            return False

        return True

    @property
    def event_has_city(self):

        try:
            _ = self.event.place.city
            return True
        except ObjectDoesNotExist:
            pass

        return False

    def event_has_any_type_of_location(self):
        return self.event_has_city or bool(self.event_location)


