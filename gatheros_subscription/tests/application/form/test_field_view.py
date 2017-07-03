from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from gatheros_event.models import Event
from gatheros_subscription.models import Field


class BaseEventFieldTest(TestCase):
    fixtures = [
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
        '009_place',
        '010_event',
        '003_form',
        '004_field',
        '005_field_option',
    ]

    def setUp(self):
        self.user = User.objects.get(email='diegotolentino@gmail.com')
        self.event = Event.objects.get(slug='arte-e-agricultura-urbana')

    def _get_url(self, event=None):
        if not event:
            event = self.event

        return reverse('gatheros_subscription:fields-config', kwargs={
            'event_pk': event.pk
        })

    def _login(self):
        self.client.force_login(self.user)

    def test_not_logged(self):
        """ Redireciona para tela de login quando não logado. """
        response = self.client.get(self._get_url(), follow=True)

        redirect_url = reverse('gatheros_front:login')
        redirect_url += '?next=/'
        self.assertRedirects(response, redirect_url)

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 200)

    def test_not_allowed_different_event(self):
        members = self.user.person.members.all()
        org_pks = [member.organization.pk for member in members]

        event = Event.objects.filter(
            subscription_type=Event.SUBSCRIPTION_BY_LOTS,
        ).exclude(organization_id__in=org_pks).first()

        url = self._get_url(event=event)
        response = self.client.get(url, follow=True)

        self.assertContains(
            response,
            'Você não pode realizar esta ação'
        )


class EventConfigFieldViewTest(BaseEventFieldTest):
    pass


class EventFormFieldAddViewTest(BaseEventFieldTest):
    def _get_url(self, event=None):
        if not event:
            event = self.event

        return reverse('gatheros_subscription:field-add', kwargs={
            'event_pk': event.pk
        })

    def test_add(self):
        """ Testa adição pela view. """
        self._login()

        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'name': 'Um evento de teste 111',
            'label': 'Um evento de teste 111',
            'active': False,
        }

        response = self.client.post(self._get_url(), data=data, follow=True)
        self.assertContains(response, 'Campo criado com sucesso')


class EventFormFieldEditViewTest(BaseEventFieldTest):
    def _get_url(self, event=None, field=None):
        if not event:
            event = self.event

        if not field:
            field = event.form.fields.filter(form_default_field=False).first()

        return reverse('gatheros_subscription:field-edit', kwargs={
            'event_pk': event.pk,
            'field_pk': field.pk
        })

    def test_edit_not_allowed(self):
        """ Testa edição de campo fixo pela view. """
        self._login()

        field = self.event.form.fields.filter(form_default_field=True).first()

        data = {'field_type': Field.FIELD_INPUT_TEXT}

        response = self.client.post(
            self._get_url(field=field),
            data=data,
            follow=True
        )
        self.assertContains(response, 'Este campo não pode ser editado')

    def test_edit(self):
        """ Testa edição pela view. """
        self._login()

        field = self.event.form.fields.filter(
            field_type=Field.FIELD_BOOLEAN,
            form_default_field=False,
            active=True
        ).first()

        data = {
            'field_type': Field.FIELD_INPUT_TEXT,
            'label': field.name + ' edited',
            'active': False,
        }

        response = self.client.post(
            self._get_url(field=field),
            data=data,
            follow=True
        )
        self.assertContains(response, 'Campo alterado com sucesso')

        field = Field.objects.get(pk=field.pk)
        self.assertEqual(field.field_type, data['field_type'])
        self.assertEqual(field.label, data['label'])
        self.assertEqual(field.active, data['active'])


class EventFormFieldDeleteViewTest(BaseEventFieldTest):
    def _get_url(self, event=None, field=None):
        if not event:
            event = self.event

        if not field:
            field = event.form.fields.filter(form_default_field=False).first()

        return reverse('gatheros_subscription:field-delete', kwargs={
            'event_pk': event.pk,
            'field_pk': field.pk
        })

    def test_delete_not_allowed(self):
        """ Testa exclusão de campo fixo pela view. """
        self._login()

        field = self.event.form.fields.filter(form_default_field=True).first()

        response = self.client.post(self._get_url(field=field), follow=True)
        self.assertContains(response, 'Você não pode excluir este registro')

    def test_delete(self):
        """ Testa exclusão de campo pela view. """
        self._login()
        response = self.client.post(self._get_url(), follow=True)
        self.assertContains(response, 'Campo excluído com sucesso')


class EventFormFieldReorderViewTest(BaseEventFieldTest):
    def _get_url(self, event=None, field=None):
        if not event:
            event = self.event

        if not field:
            field = event.form.fields.filter(form_default_field=False).first()

        return reverse('gatheros_subscription:field-order', kwargs={
            'event_pk': event.pk,
            'field_pk': field.pk
        })

    def test_reorder_not_allowed(self):
        """ Testa exclusão de campo fixo pela view. """
        self._login()
        field = self.event.form.fields.filter(form_default_field=True).first()

        response = self.client.post(self._get_url(field=field), follow=True)
        self.assertContains(response, 'Você não pode realizar esta ação')

    def test_200_logged(self):
        """ 200 quando logado. """
        self._login()
        response = self.client.get(self._get_url())
        self.assertEqual(response.status_code, 405)

    def test_order_up(self):
        """ Testa reordenação crescente de campo pela view. """

        field = self.event.form.fields.filter(form_default_field=False).first()
        first_order = field.order

        self._login()
        self.client.post(self._get_url(field=field), data={'up': ''})

        field = Field.objects.get(pk=field.pk)
        self.assertEqual(field.order, first_order+1)

    def test_order_down(self):
        """ Testa reordenação decrescente de campo pela view. """

        field = self.event.form.fields.filter(form_default_field=False)[1]
        first_order = field.order

        self._login()
        self.client.post(self._get_url(field=field), data={'down': ''})

        field = Field.objects.get(pk=field.pk)
        self.assertEqual(field.order, first_order-1)
