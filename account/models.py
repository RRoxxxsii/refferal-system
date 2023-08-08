from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, mobile, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Суперпользователь должен быть is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен быть is_superuser=True.')

        return self.create_user(mobile, password, superuser=True, **other_fields)

    def create_user(self, mobile, password=None, superuser=False,  **other_fields):
        if not mobile:
            raise ValueError('Необходимо предоставить номер телефона')
        user = self.model(mobile=mobile, **other_fields)

        if superuser:
            user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    mobile = PhoneNumberField(verbose_name='Мобильный телефон', unique=True)

    invite_code = models.CharField(max_length=6, verbose_name='Инвайт-код', null=True, unique=True)
    activated_code = models.CharField(max_length=6, verbose_name='Использованный инвайт-код', null=True, blank=True)

    auth_code = models.CharField(verbose_name='Код авторизации', null=True, max_length=4)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomAccountManager()
    USERNAME_FIELD = 'mobile'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.pk}, {self.mobile}'
