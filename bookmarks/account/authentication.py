"""
authenticate(): извлекается пользователь с данным адресом электрон-
ной почты, а пароль проверяется посредством встроенного метода
check_password() модели пользователя. Указанный метод хеширует па-
роль, чтобы сравнить данный пароль с паролем, хранящимся в базе
данных. Отлавливаются два разных исключения, относящихся к набору
запросов QuerySet: DoesNotExist и MultipleObjectsReturned. Исключение
DoesNotExist возникает, если пользователь с данным адресом электрон-
ной почты не найден. Исключение MultipleObjectsReturned возникает,
если найдено несколько пользователей с одним и тем же адресом элект-
ронной почты. Позже мы видоизменим представления регистрации
и редактирования, чтобы предотвратить использование пользователя-
ми существующего адреса электронной почты;
• get_user(): пользователь извлекается по его ИД, указанному в парамет-
ре user_id. Django использует аутентифицировавший пользователя
бэкенд, чтобы извлечь объект User на время сеанса пользователя. pk
(сокращение от primary key) является уникальным идентификатором
каждой записи в базе данных. Каждая модель Django имеет поле, кото-
рое служит ее первичным ключом. По умолчанию первичным ключом
является автоматически генерируемое поле id. Во встроенном в Django
ORM-преобразователе первичный ключ тоже может называться pk.
"""

from django.contrib.auth.models import User
from account.models import Profile


class EmailAuthBackend:
    """
    Аутентифицировать посредством адреса электронной почты.
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def create_profile(backend, user, *args, **kwargs):
        """
        Создать профиль пользователя для социальной аутентификации
        """
        Profile.objects.get_or_create(user=user)
