import uuid

from django.contrib.auth.models import User
from django.core import mail
from django.shortcuts import reverse
from django.test import TestCase

from gatheros_event.forms import InvitationCreateForm, ProfileCreateForm, \
    ProfileForm
from gatheros_event.models import Person


class ProfileFormTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.data = {
            # Informações do perfil
            "name": "João Das Couves",
            "gender": "M",
            "email": "joao-das-couves@gmail.com",
            "city": 5413,

            # Senha do usuário
            'new_password1': '123',
            'new_password2': '123',
        }

    def test_init_without_user(self):
        """
        Form sem usuário deve emitir um exception
        """
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            InvitationCreateForm()

    @staticmethod
    def get_user(email="joao-das-couves@gmail.com"):
        return User.objects.get(email=email)

    def get_form(self, email="joao-das-couves@gmail.com", user=None, **kwargs):
        if not user:
            user = self.get_user(email)
        return ProfileForm(user, **kwargs)

    def test_init_with_user_without_data(self):
        """
        Checa campos obrigatórios
        """
        form = self.get_form(data={}, password_required=False)
        self.assertFalse(form.is_valid())
        self.assertListEqual(
            sorted(list(form.errors.keys())),
            sorted(list(['name', 'email', 'gender', 'city']))
        )

    def test_save_sucess(self):
        """
        Cria um perfil com sucesso
        """
        # Garante que o perfil não existe
        with self.assertRaises(Person.DoesNotExist):
            Person.objects.get(email='joao-das-couves@gmail.com')

        form = self.get_form(data=self.data, )
        self.assertTrue(form.is_valid())
        self.assertIsInstance(form.save(), Person)

    def test_create_set_passaword(self):
        """
        Cria um perfil e define a senha do usuário
        """
        password = uuid.uuid4()
        self.data.update({
            'new_password1': password,
            'new_password2': password,
        })
        form = self.get_form(data=self.data, )
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.get(email=self.data['email'])
        self.assertTrue(user.check_password(password))

    def test_create_notset_passaword(self):
        """
        Cria um perfil e não define a senha do usuário
        """

        # Removendo password dos valores do form
        del self.data['new_password1']
        del self.data['new_password2']

        form = self.get_form(data=self.data, password_required=False)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertIsInstance(
            User.objects.get(email=self.data['email']),
            User
        )

    def test_update_change_passaword(self):
        """
        Atualiza um perfil e muda a senha do usuário
        """
        password = uuid.uuid4()
        self.data.update({
            'new_password1': password,
            'new_password2': password,
        })
        form = self.get_form(email='lucianasilva@gmail.com', data=self.data)
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.get(email=self.data['email'])
        self.assertFalse(user.check_password(password))

    def test_update_keep_passaword(self):
        """
        Atualiza um perfil e não muda a senha do usuário
        """
        # Colocando uma senha aleatória conhecida
        old_user_pass = uuid.uuid4()
        user = User.objects.get(email=self.data['email'])
        user.set_password(old_user_pass)
        user.save()

        # Removendo password dos valores do form
        del self.data['new_password1']
        del self.data['new_password2']

        # Salva demais dados e depois verifica se o password antigo continua
        form = self.get_form(data=self.data, password_required=False)
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.get(email=self.data['email'])
        self.assertTrue(user.check_password(old_user_pass))


class ProfileViewTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.data = {
            # Informações do perfil
            "name": "Luciana Silva Oliveira",
            "gender": "F",
            "email": "lucianasilva@gmail.com",
            "city": 5413,

            # Senha do usuário
            'new_password1': '123',
            'new_password2': '123',
        }

        self.url = reverse('gatheros_event:profile')

        user = User.objects.get(email=self.data['email'])
        self.client.force_login(user)

    def test_get(self):
        """
        Retorna página com form
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        """
        Atualiza o perfil
        """
        response = self.client.post(self.url, self.data, follow=True)
        self.assertContains(response, 'Perfil atualizado com sucesso')


class ProfileCreateFormTest(TestCase):
    def setUp(self):
        self.data = {
            # Informações do perfil
            "name": "João Das Couves",
            "gender": "M",
            "email": "joao-das-couves@gmail.com",
            "city": 5413,
        }

    def get_form(self, **kwargs):
        """
        Cria um form
        :param kwargs:
        :return:  ProfileCreateForm
        """
        return ProfileCreateForm(**kwargs)

    def test_form_is_valid(self):
        """
        Formulário é válido
        """
        form = self.get_form(data=self.data)
        self.assertTrue(form.is_valid())

    def test_init_with_user_without_data(self):
        """
        Checa campos obrigatórios
        """
        form = self.get_form(data={})
        self.assertFalse(form.is_valid())
        self.assertListEqual(
            sorted(list(form.errors.keys())),
            sorted(list(['name', 'email', 'gender', 'city']))
        )

    def test_account_success(self):
        """
        Save cria uma pessoa(perfil) e esta tem usuário vinculado
        """
        person_count = Person.objects.count()
        user_count = User.objects.count()
        form = self.get_form(data=self.data)
        form.is_valid()
        form.save(domain_override='127.0.0.1')

        # Verifica se criou uma pessoa
        self.assertEqual(Person.objects.count(), person_count + 1)

        # Verifica se criou um usuário
        self.assertEqual(User.objects.count(), user_count + 1)

        # Verifica se o usuário tem uma pessoa vinculada
        user = User.objects.get(email=self.data['email'])
        self.assertIsInstance(user.person, Person)

        # Verifica se enviou um email
        self.assertEqual(len(mail.outbox), 1)


class ProfileCreateViewTest(TestCase):
    def setUp(self):
        self.data = {
            "name": "João Das Couves",
            "gender": "M",
            "email": "joao-das-couves@gmail.com",
            "city": 5413,
        }

        self.url = reverse('gatheros_event:profile_create')

    def test_get(self):
        """
        Retorna página com form
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        """
        Cria o perfil
        """
        response = self.client.post(self.url, self.data, follow=True)
        self.assertContains(response, 'Informações registradas com sucesso')

    def test_post_error(self):
        """
        Verifica se post sem dados mostra campos obrigatórios
        """
        response = self.client.post(self.url, data={})
        self.assertContains(response, 'Este campo é obrigatório', 4)

    def test_follow_mail_link(self):
        """
        Verificando o link do email enviado
        """
        self.client.post(self.url, self.data)
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        url = message.body.split('http://testserver')[1].split('\n', 1)[0]

        # Get
        response = self.client.get(url, follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertContains(response, 'Nova senha')

        # Post
        data = {
            'new_password1': 'foo',
            'new_password2': 'foo'
        }
        response = self.client.post(last_url, data, follow=True)
        self.assertContains(response, "Sua senha foi definida")

        # Check passord
        user = User.objects.get(email=self.data['email'])
        self.assertTrue(user.check_password('foo'))


class ProfileResetPasswordViewTest(TestCase):
    fixtures = [
        '001_user',
        '003_occupation',
        '005_user',
        '006_person',
        '007_organization',
        '008_member',
    ]

    def setUp(self):
        self.data = {
            'email': "joao-das-couves@gmail.com"
        }
        self.url = reverse('password_reset')
        self.url_success = reverse('password_reset_done')

    def test_get(self):
        """
        Retorna página com form
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_post_success(self):
        """
        Cria o perfil
        """
        response = self.client.post(self.url, self.data, follow=True)
        self.assertContains(response, 'Redefinição de senha enviada')

    def test_post_error(self):
        """
        Verifica se post sem dados mostra campos obrigatórios
        """
        response = self.client.post(self.url, data={})
        self.assertContains(response, 'Este campo é obrigatório', 1)

    def test_follow_mail_link(self):
        """
        Verificando o link do email enviado
        """
        self.client.post(self.url, self.data, follow=True)
        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0]
        url = message.body.split('http://testserver')[1].split('\n', 1)[0]

        # Get
        response = self.client.get(url, follow=True)
        last_url, status_code = response.redirect_chain[-1]
        self.assertContains(response, 'Nova senha')

        # Post
        data = {
            'new_password1': 'foo',
            'new_password2': 'foo'
        }
        response = self.client.post(last_url, data, follow=True)
        self.assertContains(response, "Sua senha foi definida")

        # Check passord
        user = User.objects.get(email=self.data['email'])
        self.assertTrue(user.check_password('foo'))
