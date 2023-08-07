import string
from random import choice, randint


def generate_invite_code() -> str:
    """
    Генерация рандомного инвайт-кода.
    """
    letters = string.ascii_lowercase
    digits = string.digits
    values = letters + digits
    invite_code = ''.join(choice(values) for value in range(6))
    return invite_code


def generate_auth_code() -> str:
    """
    Генерация кода авторизации
    """
    auth_code = str(randint(1000, 9999))
    return auth_code
