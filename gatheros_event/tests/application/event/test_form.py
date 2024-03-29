""" Testes de aplicação com `Event` - Formulários. """
import os
import tempfile
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import six

from gatheros_event.forms import (
    EventBannerForm,
    EventEditDatesForm,
    EventEditSubscriptionTypeForm,
    EventForm,
    EventPlaceForm,
    EventPublicationForm,
    EventSocialMediaForm,
    EventTransferForm,
)
from gatheros_event.models import Event, Member, Organization


class BaseEventForm(TestCase):
    """ Classe base para testes de formulários de evento. """
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_user(self):
        return User.objects.get(email='lucianasilva@gmail.com')

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

    def get_main_form(self, user=None, instance=None, data=None):
        """ Resgata form principal """
        if not user:
            user = self._get_user()

        if not data:
            data = self._get_data()

        return EventForm(user=user, instance=instance, data=data)


class EventFormTest(BaseEventForm):
    """ Testes de formulário de evento. """

    def test_render(self):
        """ Testa se organização """
        user = self._get_user()
        form = self.get_main_form(user=user)
        content = form.as_ul()

        for member in user.person.members.all():
            org = member.organization
            can_add = user.has_perm('gatheros_event.can_add_event', org)
            if can_add:
                self.assertIn(content, org.name)
            else:
                self.assertNotIn(content, org.name)

    def test_create_edit_event(self):
        """ Testa criação e edição de evento. """

        def test_instance_data(form_obj, model_data):
            """ Testa dados da instância. """
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


class EventDatesFormTest(BaseEventForm):
    """ Testes de formulário de datas de evento. """

    def test_dates_edition_event(self):
        """ Testa edição de dados de evento. """

        def test_instance_data(form_obj, model_data):
            """ Testa dados da instância. """
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


class EventSubscriptionTypeFormTest(BaseEventForm):
    """ Testes de edição de tipo de inscrição de evento. """

    def test_subscription_type_edition_event(self):
        """ Testa edição de tipo de inscrição de evento. """

        def test_instance_data(form_obj, model_data):
            """ Testa dados da instância. """
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


class EventPublicationFormTest(BaseEventForm):
    """ Testes de formulário de publicação/despublicação de evento. """

    def test_publication_edition_event(self):
        """ Testa edição de publicação/despublicação de evento. """

        def test_instance_data(form_obj, model_data):
            """ Testa dados da instância. """
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
    """ Tests de formulário de banners de evento. """
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
            'media',
            'event'
        )
        self.event_path = os.path.join(settings.MEDIA_ROOT, 'event')
        self.persisted_path = 'event'

        self.file_names = {
            'banner_top': 'Evento_Banner_topo.png',
            'banner_slide': 'Evento_Banner_destaque.png',
            'banner_small': 'Evento_Banner_pequeno.png',
        }

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='streaming-de-sucesso')

    def _upload_banners(self):
        """ Testa upload de banners. """
        event = self._get_event()

        file_dict = {}
        for field_name, file_name in six.iteritems(self.file_names):
            # Campo ImageFile deve estar vazio
            self.assertFalse(bool(getattr(event, field_name)))

            file_path = os.path.join(self.file_base_path, file_name)
            with open(file_path, 'rb') as f:
                file_dict.update({
                    field_name: SimpleUploadedFile(
                        f.name,
                        f.read(),
                        'image/png'
                    )
                })

        # Enviando arquivos
        form = EventBannerForm(instance=event, files=file_dict)
        self.assertTrue(form.is_valid())
        form.save()

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_uploaded_files(self):
        """ Verificando se tudo foi gravado corretamente """

        # Envia os banners
        self._upload_banners()

        event = self._get_event()
        for field_name in self.file_names.keys():
            # Campo ImageFile deve estar preenchido
            self.assertTrue(bool(getattr(event, field_name)))

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_clear_fields(self):
        """ Testa o submit dos campos clear """

        # Envia os banners
        self._upload_banners()

        # Guardando path do arquivo para checagem
        event = self._get_event()
        file_paths = {}
        for field_name in self.file_names.keys():
            attr = getattr(event, field_name)
            file_paths.update({field_name: attr.file.name})

        # Limpando campos com "-clear"
        dict_clear = {}
        for field_name in self.file_names.keys():
            key = field_name + '-clear'
            dict_clear[key] = 'on'

        form = EventBannerForm(
            instance=event,
            data=dict_clear
        )
        form.save()

        # Verificando se os campos foram limpos e os arquivos apagados
        event = self._get_event()
        dir_path = None
        for field_name in self.file_names.keys():
            # Campo ImageFile deve estar limpo
            self.assertFalse(bool(getattr(event, field_name)))

            # Arquivo não deve mais existir no disco
            file_path = file_paths.get(field_name)
            dir_path = os.path.dirname(file_path)
            self.assertFalse(os.path.isfile(file_path))

        # Diretório não deve mais existir
        self.assertFalse(os.path.isdir(dir_path))

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_signal_delete(self):
        """ Testa o submit dos campos clear """

        # Envia os banners
        self._upload_banners()

        # Remove o evento
        event = self._get_event()
        dir_path = os.path.dirname(event.banner_top.file.name)
        event.delete()

        # Diretório não deve mais existir
        self.assertFalse(os.path.isdir(dir_path))


class EventPlaceFormTest(TestCase):
    """ Testes de formulário de local de event. """
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
    """ Testas formulário de dados sociais de evento. """
    fixtures = [
        '007_organization',
        '009_place',
        '010_event',
    ]

    # noinspection PyMethodMayBeStatic
    def _get_event(self):
        return Event.objects.get(slug='encontro-de-lideres-2017')

    def test_social_media_edition_event(self):
        """ Testa edição de dados sociais de evento. """
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


class EventTransferFormTest(TestCase):
    """ Testes de formulário de transferência de evento. """
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
    ]

    def setUp(self):
        self.organization = Organization.objects.get(slug='luciana-silva')
        self.member = self.organization.members.first()
        self.events = self._get_events()

    # noinspection PyMethodMayBeStatic
    def _get_events(self):
        member = self.organization.members.first()
        person = member.person

        members = person.members.filter(group=Member.ADMIN)
        orgs = [member.organization for member in members]
        events = []
        for org in orgs:
            events += list(org.events.all())

        return events

    # noinspection PyMethodMayBeStatic
    def _get_org_not_member(self):
        members = self.member.person.members.all()
        pks = [member.organization.pk for member in members]
        return Organization.objects.exclude(pk__in=pks).first()

    def _get_form(self, data=None):
        event = self.events[0]

        return EventTransferForm(
            user=self.member.person.user,
            instance=event,
            data=data
        )

    def test_render_correct_orgs(self):
        """ Testa renderização de formulário. """
        members = self.member.person.members.filter(group=Member.ADMIN)
        pks_admin = [member.organization.pk for member in members if
                     member.organization.pk != self.organization.pk]

        members = self.member.person.members.exclude(group=Member.ADMIN)
        pks_not_admin = [member.organization.pk for member in members if
                         member.organization.pk != self.organization.pk]

        form = self._get_form(data={
            'organization_to': self.organization.pk
        })
        rendered = form.as_ul()

        for pk in pks_admin:
            # Ignore a organização do evento
            if pk == form.instance.organization.pk:
                continue

            self.assertIn(str(pk), rendered)

        for pk in pks_not_admin:
            self.assertNotIn(str(pk), rendered)

    def test_transfer_not_member(self):
        """
        Testa registrição de transferência de evento por não-membro de
        organização.
        """
        org = self._get_org_not_member()
        form = self._get_form(data={
            'organization_to': org.pk
        })
        self.assertFalse(form.is_valid())
        self.assertIn('organization_to', form.errors)

    def test_transfer_org_not_admin(self):
        """
        Testa restrição de transferência de evento por uma organização na qual
        ele não é admin.
        """
        person = self.member.person
        member = person.members.exclude(group=Member.ADMIN).first()

        form = self._get_form(data={
            'organization_to': member.organization.pk
        })
        self.assertFalse(form.is_valid())
        self.assertIn('organization_to', form.errors)

    def test_transfer(self):
        """ Testa transferência de evento para outra organização. """
        form = self._get_form()
        member = self.member.person.members.filter(
            group=Member.ADMIN
        ).exclude(organization__pk=form.instance.organization.pk).first()
        org = member.organization

        form = self._get_form(data={
            'organization_to': org.pk
        })
        if not form.is_valid():
            print(form.as_ul())
            print(form.errors)

        self.assertTrue(form.is_valid())
        form.save()

        event = Event.objects.get(pk=form.instance.pk)
        self.assertEqual(event.organization.pk, org.pk)
