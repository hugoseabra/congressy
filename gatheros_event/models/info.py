# pylint: disable=W5101
"""
Informação relacionada a um evento para estrutrar uma exibição mais elaborada
das informações sobre o evento para os usuaŕios.
"""
import os
from urllib.parse import parse_qs, urlparse

from django.db import models
from django.utils.html import strip_tags
from stdimage import StdImageField
from stdimage.validators import MaxSizeValidator, MinSizeValidator

from . import Event
from .mixins import GatherosModelMixin


def get_image_path(instance, filename):
    """ Resgata localização onde as imagens serão inseridas. """
    return os.path.join('event', str(instance.event.id), filename)


class Info(models.Model, GatherosModelMixin):
    """ Informações de evento """

    CONFIG_TYPE_TEXT_ONLY = 'text_only'
    CONFIG_TYPE_MAIN_IMAGE = 'image_main'
    CONFIG_TYPE_4_IMAGES = '4_images'
    CONFIG_TYPE_VIDEO = 'video'

    CONFIG_TYPE_CHOICES = (
        (CONFIG_TYPE_TEXT_ONLY, 'Somente texto'),
        (
            CONFIG_TYPE_MAIN_IMAGE,
            'Imagem única (Largura 360px, Altura: livre)'
        ),
        (CONFIG_TYPE_4_IMAGES, '4 imagens pequenas (Tamanho: 300px x 300px)'),
        (CONFIG_TYPE_VIDEO, 'Vídeo (Youtube)'),
    )

    description = models.TextField(verbose_name='descrição (texto)')
    description_html = models.TextField(
        verbose_name='descrição do evento',
        help_text="Descreva as normas de seu evento, como a programação, "
                  "regras, reembolsos, palestrantes, atrações"
    )
    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='evento'
    )

    config_type = models.CharField(
        max_length=15,
        verbose_name='Exibição',
        default=CONFIG_TYPE_TEXT_ONLY,
        choices=CONFIG_TYPE_CHOICES
    )
    lead = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='descrição breve',
        help_text="Inspire aos visitantes a permanecerem no website do seu"
                  " evento"
    )
    image_main = StdImageField(
        max_length=255,
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem principal',
        variations={'default': (480, 638), 'thumbnail': (200, 266, True)},
        validators=[MinSizeValidator(480, 638), MaxSizeValidator(1400, 1861)],
        help_text="Banner do evento, mínimo de: 480px largura x"
                  " 640px altura.(png/jpg)" 
                  " <a target='_blank'"
                  " href='http://via.placeholder.com/480x638'>Exemplo"
                  " </a>"
    )
    image_main2 = StdImageField(
        max_length=255,
        upload_to=get_image_path,
        blank=True,
        null=True,
        verbose_name='imagem principal',
        variations={'default': (960, 503), 'thumbnail': (400, 210, True)},
        validators=[MinSizeValidator(1200, 629), MaxSizeValidator(2880, 1509)],
        help_text="Banner com tamanho ideal de 1920px largura x"
                  " 1006px altura.(png/jpg) e não ultrapasse 10Mb de tamanho"
                  " - <a target='_blank'"
                  " href='http://via.placeholder.com/1920x1006'>Exemplo</a>"
    )

    show_banner = models.BooleanField(
        default=True,
        verbose_name='Mostrar banner no hotsite',
    )

    youtube_video = models.URLField(
        verbose_name='URL do Youtube',
        null=True,
        blank=True,
        help_text="Exemplo: https://www.youtube.com/embed/T2oI7M6DE7c"
    )

    scientific_rules = models.TextField(
        verbose_name="normas de evento cientifico",
        null=True,
        blank=True,
    )

    editorial_body = models.TextField(
        verbose_name="corpo editorial de evento cientifico",
        null=True,
        blank=True,
    )

    voucher_extra_info = models.CharField(
        max_length=2000,
        null=True,
        blank=True,
        verbose_name='Informações Extras do Voucher',
        help_text="Informações extras que serão impressas junto com o voucher.",
    )

    enable_streaming_page = models.BooleanField(
        default=False,
        verbose_name='Habilitar página de streaming de vídeo',
    )

    stream_page_title = models.CharField(
        max_length=80,
        blank=True,
        default='Transmissão ao vivo',
        verbose_name='Título da Página de Vídeo',
    )

    stream_youtube_code = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Código do Vídeo (Youtube)',
        help_text='https://www.youtube.com/watch?v=<strong>CÓDIGO</strong>',
    )

    @property
    def youtube_image(self):
        if not self.youtube_video:
            return None

        uuid = self.youtube_video.split('/')[-1]
        return 'https://img.youtube.com/vi/{0}/0.jpg'.format(uuid)

    def save(self, **kwargs):
        """
        Sobrescrição do save padrão

        :param kwargs:
        :return: instance
        """

        "Remove tags da descrição em html para criar uma descrição puro texto"
        self.description = strip_tags(self.description_html)

        if self.youtube_video:
            "Extrai o código do vídeo e cria url de embed"
            parse_result = urlparse(self.youtube_video)
            try:
                "https://www.youtube.com/watch?v=T2oI7M6DE7c"
                uuid = parse_qs(parse_result.query)['v'][0]
            except KeyError:
                "https://youtu.be/T2oI7M6DE7c"
                uuid = parse_result.path[1:]

            self.youtube_video = \
                'https://www.youtube.com/embed/{0}'.format(uuid)

        return super(Info, self).save(kwargs)

    class Meta:
        verbose_name = 'Informação de Evento'
        verbose_name_plural = 'Infomações de Eventos'
        ordering = ['event']

    def __str__(self):
        return self.event.name
