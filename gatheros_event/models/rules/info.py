"""
A exibição de informações do evento aceita apenas um tipo de configuração.
"""

from django.core.exceptions import ValidationError


def rule_1_imagem_unica_somente(info):
    if info.config_type != info.CONFIG_TYPE_MAIN_IMAGE:
        return

    if not info.image_main:
        raise ValidationError({'image_main': ['Você deve inserir a imagem principal.']})

    for field in ['image1', 'image2', 'image3', 'image4']:
        value = getattr(info, field)
        if value:
            _remove_file(value)

        setattr(info, field, None)

    info.youtube_video_id = None


def rule_2_4_imagens_somente(info):
    if info.config_type != info.CONFIG_TYPE_4_IMAGES:
        return

    errors = {}
    for field in ['image1', 'image2', 'image3', 'image4']:
        field_obj = getattr(info, field)
        name = getattr(field_obj, 'name')
        if not name:
            errors[field] = ['Você deve inserir uma image']

    if errors:
        raise ValidationError(errors)

    if info.image_main:
        _remove_file(info.image_main)

    info.image_main = None
    info.youtube_video_id = None


def rule_3_youtube_video_somente(info):
    if info.config_type != info.CONFIG_TYPE_VIDEO:
        return

    if not info.youtube_video_id:
        raise ValidationError({'youtube_video_id': ['Você deve informar o ID do vídeo do youtube.']})

    for field in ['image_main', 'image1', 'image2', 'image3', 'image4']:
        value = getattr(info, field)
        if value:
            _remove_file(value)

        setattr(info, field, None)


def _remove_file(file):
    storage, path = file.storage, file.path
    storage.delete(path)
