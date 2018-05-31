# pylint: disable=W5101
"""
Models de certificados
"""

import os

from django.db import models
from stdimage import StdImageField
from stdimage.validators import MinSizeValidator


def get_image_path(instance, filename):
    """ Resgata localização onde as imagens serão inseridas. """
    return os.path.join('event', str(instance.event.id), filename)


class Certificate(models.Model):
    """ Certificado de evento."""

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
        variations={'default': (1402, 991)},
        validators=[MinSizeValidator(1402, 991)],
        help_text="Imagem de fundo do certificado, mínimo de: "
                  "595px largura x "
                  "842 altura.(png/jpg) "
                  "<a  target='_blank'"
                  "href='http://via.placeholder.com/595x842'>Exemplo"
                  "</a>"
    )

    text_content = models.TextField(
        default='Certificamos que {{NOME}} participou do evento {{EVENTO}}',
        verbose_name='texto',
        help_text='Texto principal do certificado.',
    )

    date_content = models.TextField(
        verbose_name='texto',
        help_text='Texto de data do certificado.',
        null=True,
        blank=True,
    )

    text_font_size = models.PositiveIntegerField(
        default=20,
        verbose_name='tamaho da fonte do texto',
        help_text='Tamanho da fonte em (px)',
        null=True,
        blank=True,
    )

    text_width = models.PositiveIntegerField(
        default=634,
        verbose_name='largura do bloco do texto',
        help_text='tamanho (px) da largura do bloco.',
        null=True,
        blank=True,
    )

    text_height = models.PositiveIntegerField(
        default=348,
        verbose_name='altura do bloco do texto',
        help_text='tamanho (px) da altura do bloco.',
        null=True,
        blank=True,
    )

    text_line_height = models.FloatField(
        max_length=3,
        verbose_name='espaço entre-linhas do texto',
        help_text='espaço entre-linhas (cm) do conteúdo.',
        null=True,
        blank=True,
    )

    text_position_x = models.FloatField(
        default=191,
        verbose_name='posição X do texto',
        help_text='distância do bloco no eixo X.',
        null=True,
        blank=True,
    )

    text_position_y = models.FloatField(
        default=309,
        max_length=5,
        verbose_name='posição Y do texto',
        help_text='distância do bloco no eixo Y.',
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

    title_font_size = models.PositiveIntegerField(
        default=60,
        verbose_name='tamaho da fonte do título',
        help_text='Tamanho da fonte em (px)',
        null=True,
        blank=True,
    )

    title_position_x = models.FloatField(
        default=286,
        verbose_name='posição X do título',
        help_text='distância do bloco no eixo X.',
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

    date_font_size = models.PositiveIntegerField(
        default=20,
        verbose_name='tamaho da fonte da data',
        help_text='Tamanho da fonte em (px)',
        null=True,
        blank=True,
    )

    date_position_x = models.FloatField(
        default=15,
        max_length=5,
        verbose_name='posição X da data',
        help_text='distância do bloco no eixo X.',
        null=True,
        blank=True,
    )

    date_position_y = models.FloatField(
        default=463,
        max_length=5,
        verbose_name='posição Y da data',
        help_text='distância do bloco no eixo Y.',
        null=True,
        blank=True,
    )

    date_hide = models.BooleanField(
        default=False,
        verbose_name='esconder data',
    )

    def __str__(self):
        return '{}'.format(self.event)
