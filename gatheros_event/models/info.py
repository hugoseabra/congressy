# pylint: disable=W5101
"""
Informação relacionada a um evento para estrutrar uma exibição mais elaborada
das informações sobre o evento para os usuaŕios.
"""
import os
from django.utils.html import strip_tags

from django.db import models
from stdimage import StdImageField
from stdimage.validators import MaxSizeValidator, MinSizeValidator

from . import Event


# @TODO Excluir imagens banners ao deletar evento.

def get_image_path(instance, filename):
    return os.path.join('event', str(instance.event.id), filename)


class Info(models.Model):
    """ Informações de evento """

    CONFIG_TYPE_MAIN_IMAGE = 'image_main'
    CONFIG_TYPE_4_IMAGES = '4_images'
    CONFIG_TYPE_VIDEO = 'video'

    CONFIG_TYPE_CHOICES = (
        (
            CONFIG_TYPE_MAIN_IMAGE,
            'Imagem única (Largura 360px, Altura: livre)'
        ),
        (CONFIG_TYPE_4_IMAGES, '4 imagens pequenas (Tamanho: 300px x 300px)'),
        (CONFIG_TYPE_VIDEO, 'Vídeo (Youtube)'),
    )

    text = models.TextField(verbose_name='texto')
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='evento'
    )

    config_type = models.CharField(
        max_length=15,
        verbose_name='Exibição',
        choices=CONFIG_TYPE_CHOICES
    )
    image_main = StdImageField(
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem principal',
        variations={'default': (750, 874), 'thumbnail': (200, 233, True)},
        validators=[MinSizeValidator(750, 874), MaxSizeValidator(1400, 1400)],
        help_text="Imagem única da descrição do evento: 750px x 874px"
    )
    image1 = StdImageField(
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem pequena #1',
        variations={'default': (350, 350), 'thumbnail': (200, 200, True)},
        validators=[MinSizeValidator(350, 350), MaxSizeValidator(1400, 1400)],
        help_text="Tamanho: 350px x 350px"
    )
    image2 = StdImageField(
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem pequena #2',
        variations={'default': (350, 350), 'thumbnail': (200, 200, True)},
        validators=[MinSizeValidator(350, 350), MaxSizeValidator(1400, 1400)],
        help_text="Tamanho: 350px x 350px"
    )
    image3 = StdImageField(
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem pequena #3',
        variations={'default': (350, 350), 'thumbnail': (200, 200, True)},
        validators=[MinSizeValidator(350, 350), MaxSizeValidator(1400, 1400)],
        help_text="Tamanho: 350px x 350px"
    )
    image4 = StdImageField(
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem pequena #4',
        variations={'default': (350, 350), 'thumbnail': (200, 200, True)},
        validators=[MinSizeValidator(350, 350), MaxSizeValidator(1400, 1400)],
        help_text="Tamanho: 350px x 350px"
    )
    youtube_video_id = models.CharField(
        max_length=12,
        verbose_name='ID do Youtube',
        null=True,
        blank=True,
        help_text="Exemplo: https://www.youtube.com/watch?v=id_do_video"
    )

    class Meta:
        verbose_name = 'Informação de Evento'
        verbose_name_plural = 'Infomações de Eventos'
        ordering = ['event']

    def __str__(self):
        return self.event.name

    def save(self, *args, **kwargs):
        self.event.description = strip_tags(self.text)
        super(Info, self).save(*args, **kwargs)
        self.event.save()
