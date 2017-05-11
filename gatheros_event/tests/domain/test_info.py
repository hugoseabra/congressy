from datetime import datetime, timedelta

from core.tests import GatherosTestCase
from gatheros_event.models import Category, Event, Info, Organization
from gatheros_event.models.rules import info as rule


class InfoModelTest(GatherosTestCase):
    fixtures = [
        'kanu_locations_city_test',
        '004_category',
        '007_organization',
        '009_place',
        '010_event',
    ]

    def _create_event(self, persist=False, **kwargs):
        data = {
            "name": 'Event tests',
            "organization": Organization.objects.first(),
            "category": Category.objects.first(),
            "subscription_type": Event.SUBSCRIPTION_DISABLED,
            "date_start": datetime.now(),
            "date_end": datetime.now() + timedelta(hours=8)
        }
        return self._create_model(
            Model=Event,
            data=data,
            persist=persist,
            **kwargs
        )

    def _create_info(self, event=None, persist=False, **kwargs):
        if not event:
            event = self._create_event(persist=True)

        data = {
            'text': 'Some text',
            'event': event,
            'config_type': None,
            'image_main': None,
            'image1': None,
            'image2': None,
            'image3': None,
            'image4': None,
            'youtube_video_id': None
        }

        return self._create_model(
            Model=Info,
            data=data,
            persist=persist,
            **kwargs
        )

    def _populate_files(self, info):
        info.image_main = 'some_main_image.jpg'
        info.image1 = 'image1.jpg'
        info.image2 = 'image2.jpg'
        info.image3 = 'image3.jpg'
        info.image4 = 'image4.jpg'
        info.youtube_video_id = 'some youtube id'

    def test_rule_1_imagem_unica_somente(self):
        rule_callback = rule.rule_1_imagem_unica_somente

        info = self._create_info(config_type=Info.CONFIG_TYPE_MAIN_IMAGE)

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[info],
            field='image_main'
        )

        """ MODEL """
        self._trigger_validation_error(info.save, field='image_main')

        """ FUNCIONANDO """
        self._populate_files(info)
        info.save()

        # Campos de 4 imagens e ID youtube devem ser nulos
        self.assertIsNone(info.image1.name)
        self.assertIsNone(info.image2.name)
        self.assertIsNone(info.image3.name)
        self.assertIsNone(info.image4.name)
        self.assertIsNone(info.youtube_video_id)

    def test_rule_2_4_imagens_somente(self):
        rule_callback = rule.rule_2_4_imagens_somente

        info = self._create_info(config_type=Info.CONFIG_TYPE_4_IMAGES)

        image_fileds = ['image1', 'image2', 'image3', 'image4']

        # Verifica se há erro quando algum dos campos é nulo

        """ RULE """
        for field in image_fileds:
            self._populate_files(info)
            setattr(info, field, None)
            self._trigger_validation_error(rule_callback, [info], field=field)

        """ MODEL """
        for field in image_fileds:
            self._populate_files(info)
            setattr(info, field, None)
            self._trigger_validation_error(info.save, field=field)

        """ FUNCIONANDO """
        self._populate_files(info)
        info.save()

        # Campos de image_main e youtube_video_id devem ser nulos
        self.assertIsNone(info.image_main.name)
        self.assertIsNone(info.youtube_video_id)

    def test_rule_3_youtube_video_somente(self):
        rule_callback = rule.rule_3_youtube_video_somente

        info = self._create_info(config_type=Info.CONFIG_TYPE_VIDEO)

        """ RULE """
        self._trigger_validation_error(
            callback=rule_callback,
            params=[info],
            field='youtube_video_id'
        )

        """ MODEL """
        self._trigger_validation_error(info.save, field='youtube_video_id')

        # """ FUNCIONANDO """
        self._populate_files(info)
        info.save()

        # Campos de image_main e 4 imagens pequenas devem ser nulos
        self.assertIsNone(info.image_main.name)
        self.assertIsNone(info.image1.name)
        self.assertIsNone(info.image2.name)
        self.assertIsNone(info.image3.name)
        self.assertIsNone(info.image4.name)
