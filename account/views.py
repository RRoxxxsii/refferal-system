from random import randint
from time import sleep

from django.contrib.auth import login
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sms import send_sms

from account.models import User
from account.serializers import (AuthCodeInputSerializer,
                                 InviteCodeInputSerializer,
                                 ListUserEnteredCode,
                                 PhoneNumberInputSerializer)
from account.utils import generate_auth_code, generate_invite_code


class PhoneNumberInputAPIView(CreateAPIView):
    """
    Запрос на ввод номера телефона, отправка кода авторизации.
    Запись пользователя в БД, если его первая авторизация.
    """
    serializer_class = PhoneNumberInputSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            mobile = request.data.get('mobile')
            user, created = User.objects.get_or_create(mobile=mobile)
            if created:
                # Генерируем инвайт-код
                invite_code = generate_invite_code()
                user.invite_code = invite_code

            # Генерируем код авторизации
            auth_code = generate_auth_code()

            # Имитация задержки на сервере и отправки сообщения
            sleep(randint(1, 2))
            send_sms(f'Ваш код авторизации: {auth_code}', '+12065550100',
                     [mobile], fail_silently=False)

            user.auth_code = auth_code
            user.save()
            return Response(data={'message': 'Вам был отправлен код авторизации.'})

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthCodeInputAPIView(APIView):
    """
    Запрос на ввод кода авторизации.
    """
    serializer_class = AuthCodeInputSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            auth_code = serializer.data.get('auth_code')
            try:
                user = User.objects.get(auth_code=auth_code)
            except User.DoesNotExist:
                return Response(data={'message': 'Код авторизации, введенный вами,'
                                                 ' оказался некорректным'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                login(request=request, user=user)
                return Response(data={'message': 'Вы успешно авторизованы'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InputInviteCode(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = InviteCodeInputSerializer(data=request.data)
        if serializer.is_valid():
            invite_code = request.data.get('invite_code')

            # Пытаемся получить объект пользователя
            try:
                user = User.objects.get(invite_code=invite_code)

            except User.DoesNotExist:
                return Response({'message': 'Пользователь с таким инвайт-кодом не найден.'},
                                status=status.HTTP_404_NOT_FOUND)

            else:
                request_user = request.user
                # Если пользователь вводит собственный код, то возбуждаем исключение
                if user == request_user:
                    return Response(data={'message': 'Вы не можете использовать свой собственный инвайт-код.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                activated_code = request_user.activated_code
                # Если пользователь уже активировал код, возвращаем его
                if activated_code:
                    return Response(data={'message': f'Вы уже вводили код, вот он: {activated_code}'},
                                    status=status.HTTP_400_BAD_REQUEST)
                # Если не активирован, присваиваем
                else:
                    request_user.activated_code = invite_code
                    request_user.save()
                return Response(data={'message': 'Вы успешно активировали инвайт-код!'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Список пользователей, которые ввели инвайт текущего пользователя
        user_invite = request.user.invite_code
        users = User.objects.filter(activated_code=user_invite)
        serializer = ListUserEnteredCode(users, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
