import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import six

from gatheros_event.forms import (
    Info4ImagesForm,
    InfoMainImageForm,
    InfoTextForm,
    InfoVideoForm,
)
from gatheros_event.models import Event, Info


class BaseInfoFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
        '011_info',
    ]

    def setUp(self):
        self.file_base_path = os.path.join(
            settings.BASE_DIR,
            'gatheros_event',
            'tests',
            'fixtures',
            'images',
            'info'
        )
        self.persisted_path = 'event'

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='streaming-de-sucesso')

    # noinspection PyMethodMayBeStatic
    def _get_info(self):
        event = self._get_event()
        return event.info

    def tearDown(self):
        info = self._get_info()
        path = os.path.join(
            settings.MEDIA_ROOT,
            self.persisted_path,
            str(info.event.pk)
        )
        if os.path.isdir(path):
            shutil.rmtree(path)


class InfoTextFormTest(BaseInfoFormTest):
    def test_new_info(self):
        info = self._get_info()
        info.delete()

        event = self._get_event()
        data = {
            'event': event.pk,
            'text': info.event.description,
            'config_type': Info.CONFIG_TYPE_TEXT_ONLY,
        }

        form = InfoTextForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()

        event = self._get_event()
        info = event.info
        self.assertIsInstance(info, Info)
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_TEXT_ONLY)

    def test_video(self):
        info = self._get_info()
        assert info is not None

        data = {
            'event': info.event.pk,
            'text': info.event.description,
            'config_type': Info.CONFIG_TYPE_TEXT_ONLY,
        }

        form = InfoTextForm(instance=info, data=data)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_TEXT_ONLY)


class Info4ImagesFormTest(BaseInfoFormTest):
    def test_new_info(self):
        info = self._get_info()
        data = {
            'event': info.event_id,
            'config_type': Info.CONFIG_TYPE_4_IMAGES,
            'text': info.event.description,
        }
        info.delete()

        file_path = os.path.join(self.file_base_path, 'image1.jpg')
        persited_name = os.path.join(
            self.persisted_path,
            str(data['event']),
            'image1.jpg'
        )
        file = open(file_path, 'rb')
        file_dict = {'image1': SimpleUploadedFile(
            persited_name,
            file.read(),
            'image/jpeg'
        )}

        form = Info4ImagesForm(data=data, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertIsInstance(info, Info)
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_4_IMAGES)

    def test_images(self):
        info = self._get_info()
        assert info is not None

        file_names = {
            'image1': 'image1.jpg',
            'image2': 'image2.jpg',
            'image3': 'image3.jpg',
            'image4': 'image4.jpg',
        }

        file_dict = {}
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)

            # Campo ImageFile deve estar vazio
            self.assertEqual(attr.name, '')

            file_path = os.path.join(self.file_base_path, file_name)
            persited_name = os.path.join(
                self.persisted_path,
                str(info.event_id),
                file_name
            )

            file = open(file_path, 'rb')
            file_dict[field_name] = SimpleUploadedFile(
                persited_name,
                file.read(),
                'image/jpeg'
            )

        data = {
            'event': info.event_id,
            'text': info.event.description,
            'config_type': Info.CONFIG_TYPE_4_IMAGES,
        }
        form = Info4ImagesForm(instance=info, data=data, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_4_IMAGES)

        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)
            file_path = os.path.join(
                self.persisted_path,
                str(info.event.pk),
                file_name
            )

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, file_path)
            self.assertTrue(os.path.isfile(os.path.join(
                settings.MEDIA_ROOT,
                file_path
            )))


class InfoMainImageFormTest(BaseInfoFormTest):
    def test_new_info(self):
        info = self._get_info()
        data = {
            'event': info.event_id,
            'text': info.event.description,
            'config_type': Info.CONFIG_TYPE_MAIN_IMAGE,
        }
        info.delete()

        file_path = os.path.join(self.file_base_path, 'image_main.jpg')
        persited_name = os.path.join(
            self.persisted_path,
            str(data['event']),
            'image_main.jpg'
        )
        file = open(file_path, 'rb')
        file_dict = {'image_main': SimpleUploadedFile(
            persited_name,
            file.read(),
            'image/jpeg'
        )}

        form = InfoMainImageForm(data=data, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertIsInstance(info, Info)
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_MAIN_IMAGE)

    def test_main_image(self):
        info = self._get_info()
        assert info is not None

        file_names = {
            'image_main': 'image_main.jpg',
        }

        file_dict = {}
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)

            # Campo ImageFile deve estar vazio
            self.assertEqual(attr.name, '')

            file_path = os.path.join(self.file_base_path, file_name)
            persited_name = os.path.join(
                self.persisted_path,
                str(info.event_id),
                file_name
            )

            file = open(file_path, 'rb')
            file_dict[field_name] = SimpleUploadedFile(
                persited_name,
                file.read(),
                'image/jpeg'
            )

        data = {
            'event': info.event_id,
            'text': info.event.description,
            'config_type': Info.CONFIG_TYPE_MAIN_IMAGE,
        }
        form = InfoMainImageForm(instance=info, data=data, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_MAIN_IMAGE)

        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(info, field_name)
            attr = getattr(info, field_name)
            file_path = os.path.join(
                self.persisted_path,
                str(info.event.pk),
                file_name
            )

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, file_path)
            self.assertTrue(os.path.isfile(os.path.join(
                settings.MEDIA_ROOT,
                file_path
            )))


class InfoVideoFormTest(BaseInfoFormTest):
    def test_new_info(self):
        info = self._get_info()
        info.delete()

        event = self._get_event()
        data = {
            'event': event.pk,
            'text': info.event.description,
            'config_type': Info.CONFIG_TYPE_VIDEO,
            'youtube_video_id': 'jbVpFUGCw1o',
        }

        form = InfoVideoForm(data=data)
        self.assertTrue(form.is_valid())
        form.save()

        event = self._get_event()
        info = event.info
        self.assertIsInstance(info, Info)
        self.assertEqual(info.youtube_video_id, data['youtube_video_id'])
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_VIDEO)

    def test_video(self):
        info = self._get_info()
        assert info is not None

        data = {
            'event': info.event.pk,
            'text': info.event.description,
            'config_type': Info.CONFIG_TYPE_VIDEO,
            'youtube_video_id': 'jbVpFUGCw1o',
        }

        form = InfoVideoForm(instance=info, data=data)
        self.assertTrue(form.is_valid())
        form.save()

        info = self._get_info()
        self.assertEqual(info.config_type, Info.CONFIG_TYPE_VIDEO)
