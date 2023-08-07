from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import User


class TestPhoneNumberInput(APITestCase):

    def setUp(self) -> None:
        self.url = reverse('auth')

    def test_send_request(self):
        response = self.client.post(self.url, data={'mobile': '+78005553535'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_new_user_created(self):
        """
        Проверка создания пользователя в БД при первой авторизации.
        """
        self.client.post(self.url, data={'mobile': '+78005553535'})
        user = User.objects.get(mobile='+78005553535')
        self.assertIsNotNone(user)
        self.assertIsNotNone(user.auth_code)
        self.assertIsNotNone(user.invite_code)

    def test_user_auth_second_time(self):
        """
        Проверка отправки запроса для пользователя, который был авторизован ранее.
        Новый пользователь с теми же данными не должен быть создан.
        """
        self.client.post(self.url, data={'mobile': '+78005553535'})
        User.objects.get(mobile='+78005553535')
        self.client.post(self.url, data={'mobile': '+78005553535'})
        users = User.objects.all()
        self.assertEqual(len(users), 1)

    def test_invite_code(self):
        """
        Проверка того, что invite-code при каждой авторизации не генерируется заново,
        а остается прежним.
        """
        self.client.post(self.url, data={'mobile': '+78005553535'})
        user = User.objects.get(mobile='+78005553535')
        invite_code_first_request = user.invite_code
        self.client.post(self.url, data={'mobile': '+78005553535'})
        user.refresh_from_db()
        user2 = User.objects.get(mobile='+78005553535')
        invite_code_second_request = user2.invite_code
        self.assertEqual(invite_code_first_request, invite_code_second_request)


class TestAuthCodeInput(APITestCase):

    def setUp(self) -> None:
        self.url = reverse('auth-code-input')

    def test_auth_code_input(self):
        """
        Отправка корректного кода авторизации.
        """
        self.client.post(reverse('auth'), data={'mobile': '+78005553535'})
        user = User.objects.get(mobile='+78005553535')
        auth_code = user.auth_code
        response = self.client.post(self.url, data={'auth_code': auth_code})
        self.assertEqual(response.status_code, 200)

    def test_user_is_authenticated(self):
        """
        Проверка, является ли пользователь аутентифицированным.
        """
        self.client.post(reverse('auth'), data={'mobile': '+78005553535'})
        User.objects.get(mobile='+78005553535')

    def test_auth_code_input_incorrect(self):
        """
        Отправка некорректного кода авторизации.
        """
        self.client.post(reverse('auth'), data={'mobile': '+78005553535'})
        User.objects.get(mobile='+78005553535')

        # Некорректный код авторизации
        auth_code = 0000
        response = self.client.post(self.url, data={'auth_code': auth_code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestActivateInviteCode(APITestCase):

    def setUp(self) -> None:
        self.url = reverse('profile')
        self.user1 = User.objects.create_user(mobile='+79005553529', invite_code='6a7a8z')
        self.user2 = User.objects.create_user(mobile='+79005153539', invite_code='6a7a8v')
        self.user3 = User.objects.create_user(mobile='+79005153530', invite_code='ga7a8v')

    def test_code_input_not_authenticated(self):
        """
        Пользователь неаутетифицирован. Активация инвайт-кода.
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_code_input(self):
        """
        Пользователь аутентифицрован. Активация инвайт-кода.
        """
        self.client.force_login(self.user1)
        response = self.client.post(self.url, data={'invite_code': '6a7a8v'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_code_input_if_already_used(self):
        """
        Пытаемся ввести инвайт-код при условии, что указывали код ранее
        """
        self.client.force_login(self.user1)
        self.client.post(self.url, data={'invite_code': '6a7a8v'})
        response = self.client.post(self.url, data={'invite_code': '6a7a8v'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_request(self):
        """
        Получаем список пользователей, которые ввели код текущего пользователя.
        """
        self.client.force_login(self.user1)
        self.client.post(self.url, data={'invite_code': '6a7a8v'})
        self.client.force_login(self.user3)
        self.client.post(self.url, data={'invite_code': '6a7a8v'})
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        # Пользователи, которые ввели код текущего пользователя
        users = eval(response.content.decode())
        self.assertEqual(len(users), 2)
