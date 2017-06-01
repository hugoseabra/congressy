# pylint: disable=C0103,W0622
"""
Regras de negócio para informação de evento.
"""

from django.core.exceptions import ValidationError


def rule_1_imagem_unica_somente(info):
    """
    Se configuração é para imagem principal, imagem principal deve ser enviada
    e não pode haver outras imagens e link do youtube.
    """
    if info.config_type != info.CONFIG_TYPE_MAIN_IMAGE:
        return

    if not info.image_main:
        raise ValidationError({'image_main': [
            'Você deve inserir a imagem principal.'
        ]})

    for field in ['image1', 'image2', 'image3', 'image4']:
        value = getattr(info, field)
        if value:
            _remove_file(value)

        setattr(info, field, None)

    info.youtube_video_id = None


def rule_2_4_imagens_somente(info):
    """
    Se configuração é para 4 imagens, imagens devem ser enviadas e não pode
    haver imagem principal e link do youtube.
    """
    if info.config_type != info.CONFIG_TYPE_4_IMAGES:
        return

    errors = {}
    for field in ['image1', 'image2', 'image3', 'image4']:
        field_obj = getattr(info, field)
        name = getattr(field_obj, 'name')
        if not name:
            errors[field] = ['Você deve inserir uma imagem.']

    if errors:
        raise ValidationError(errors)

    if info.image_main:
        _remove_file(info.image_main)

    info.image_main = None
    info.youtube_video_id = None


def rule_3_youtube_video_somente(info):
    """
    Se configuração é link do youtube, imagens devem ser enviadas e não pode
    haver imagem principal e 4 imagens.
    """

    if info.config_type != info.CONFIG_TYPE_VIDEO:
        return

    if not info.youtube_video_id:
        raise ValidationError({'youtube_video_id': [
            'Você deve informar o ID do vídeo do youtube.'
        ]})

    for field in ['image_main', 'image1', 'image2', 'image3', 'image4']:
        value = getattr(info, field)
        if value:
            _remove_file(value)

        setattr(info, field, None)


def _remove_file(file):
    """
    Remove arquivos do storage.
    :param file: object - Instância de File
    :return: None
    """
    storage = file.storage
    path = file.path
    storage.delete(path)
