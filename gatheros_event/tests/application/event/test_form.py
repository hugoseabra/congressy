import os
import shutil
from datetime import datetime, timedelta

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import six

from gatheros_event.forms import (
    EventBannerForm,
    EventEditDatesForm,
    EventEditSubscriptionTypeForm,
    EventForm,
    EventPlaceForm,
    EventPublicationForm,
    EventSocialMediaForm,
)
from gatheros_event.models import Event, Organization


class BaseEventFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(self, pk):
        return Event.objects.get(pk=pk)

    # noinspection PyMethodMayBeStatic
    def _get_data(self):
        date_start = datetime.now() + timedelta(days=5)
        date_start = date_start.replace(
            hour=8,
            minute=0,
            second=0,
            microsecond=0
        )

        date_end = datetime.now() + timedelta(days=5, hours=8)
        date_end = date_end.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0
        )

        return {
            "name": 'Event tests',
            "organization": 1,
            "category": 1,
            "subscription_type": Event.SUBSCRIPTION_DISABLED,
            "date_start": date_start,
            "date_end": date_end,
            "subscription_offline": False,
            "published": False,
        }

    def get_main_form(self, instance=None, data=None):
        if not data:
            data = self._get_data()

        return EventForm(instance=instance, data=data)


class EventFormTest(BaseEventFormTest):
    def test_create_edit_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data.update({
            'name': 'Event - another name',
            'category': 2
        })

        form = self.get_main_form(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


class EventDatesFormTest(BaseEventFormTest):
    def test_dates_edition_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data = {
            'date_start': form.instance.date_start + timedelta(hours=4),
            'date_end': form.instance.date_end + timedelta(hours=4)
        }

        form = EventEditDatesForm(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


class EventSubscriptionTypeFormTest(BaseEventFormTest):
    def test_subscription_type_edition_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data = {
            'subscription_type': Event.SUBSCRIPTION_SIMPLE,
            'subscription_offline': True,
        }

        form = EventEditSubscriptionTypeForm(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


class EventPublicationFormTest(BaseEventFormTest):
    def test_publication_edition_event(self):
        def test_instance_data(form_obj, model_data):
            model = form_obj.instance
            for key, value in six.iteritems(model_data):
                model_v = getattr(model, key)

                if hasattr(model_v, 'pk'):
                    model_v = model_v.pk

                self.assertEqual(model_v, value)

        data = self._get_data()

        form = self.get_main_form()
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)

        data = {
            'published': True,
        }

        form = EventPublicationForm(instance=form.instance, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        test_instance_data(form, data)


class EventBannersFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.file_base_path = os.path.join(
            settings.BASE_DIR,
            'gatheros_event',
            'tests',
            'fixtures',
            'images',
            'event'
        )
        self.event_path = os.path.join(settings.MEDIA_ROOT, 'event')
        self.persisted_path = 'event'

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='streaming-de-sucesso')

    def tearDown(self):
        event = self._get_event()
        path = os.path.join(self.event_path, str(event.pk))
        if os.path.isdir(path):
            shutil.rmtree(path)

    def test_banner(self):
        event = self._get_event()

        file_names = {
            'banner_top': 'Evento_Banner_topo.png',
            'banner_slide': 'Evento_Banner_destaque.png',
            'banner_small': 'Evento_Banner_pequeno.png',
        }

        file_dict = {}
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(event, field_name)
            attr = getattr(event, field_name)

            # Campo ImageFile deve estar vazio
            self.assertEqual(attr.name, '')

            file_path = os.path.join(self.file_base_path, file_name)

            file = open(file_path, 'rb')
            file_dict[field_name] = SimpleUploadedFile(
                file_name,
                file.read(),
                'image/png'
            )

        form = EventBannerForm(instance=event, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

        event = self._get_event()
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(event, field_name)
            attr = getattr(event, field_name)
            file_dir = os.path.join(self.event_path, str(event.pk))
            file_path = os.path.join(file_dir, file_name)

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, '{}/{}/{}'.format(
                self.persisted_path,
                str(event.pk),
                file_name
            ))
            self.assertTrue(os.path.isfile(file_path))

        # Clear file deve limpar o campo no model e deletar os arquivos
        dict_clear = {}
        for field_name in six.iterkeys(file_names):
            key = field_name+'-clear'
            dict_clear[key] = 'on'

        form = EventBannerForm(
            instance=event,
            data=dict_clear
        )
        form.save()

        # Campos limpos e sem arquivos
        event = self._get_event()
        for field_name, file_name in six.iteritems(file_names):
            assert hasattr(event, field_name)
            attr = getattr(event, field_name)
            file_dir = os.path.join(self.event_path, str(event.pk))
            file_path = os.path.join(file_dir, file_name)

            # Campo ImageFile deve ter o arquivo enviado.
            self.assertEqual(attr.name, '')
            self.assertFalse(os.path.isfile(file_path))


class EventPlaceFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='encontro-de-lideres-2017')

    def test_render_form(self):
        """
        Se na apresentação do formulário aparece apenas os locais da
        organização do contexto.
        """
        event = self._get_event()
        organization = event.organization
        other_organization = Organization.objects.exclude(
            pk=organization.pk
        ).first()

        form = EventPlaceForm(instance=event)
        rendered = form.as_ul()

        # Formulário DEVE conter locais da organização do evento
        for place in organization.places.all():
            option = 'value="{}"'.format(place.pk)
            self.assertIn(option, rendered)

        # Formulário NÃO DEVE conter locais de outra organização
        for place in other_organization.places.all():
            option = 'value="{}"'.format(place.pk)
            self.assertNotIn(option, rendered)

    def test_update_place(self):
        """ Testa Form de atualização de local de evento. """

        event = self._get_event()
        current_place = event.place
        organization = event.organization
        place = organization.places.exclude(pk=event.place.pk).first()
        assert place is not None

        # Atualiza local
        form = EventPlaceForm(instance=event, data={'place': place.pk})
        self.assertTrue(form.is_valid())
        form.save()

        event = self._get_event()
        self.assertNotEqual(event.place.pk, current_place.pk)

        # Limpa local
        form = EventPlaceForm(instance=event, data={'place': None})
        self.assertTrue(form.is_valid())
        form.save()

        event = self._get_event()
        self.assertIsNone(event.place)


class EventSocialMediaFormTest(TestCase):
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='encontro-de-lideres-2017')

    def test_social_media_edition_event(self):
        data = {
            'website': 'http://seoresultados.com',
            'facebook': 'https://facebook.com/seo',
            'twitter': 'https://twitter.com/seo',
            'linkedin': 'https://linkedin.com/seo',
            'skype': 'seoresultados',
        }

        form = EventSocialMediaForm(instance=self._get_event(), data=data)
        self.assertTrue(form.is_valid())
        form.save()

        event = self._get_event()
        for key, value in six.iteritems(data):
            model_v = getattr(event, key)

            if hasattr(model_v, 'pk'):
                model_v = model_v.pk

            self.assertEqual(model_v, value)
