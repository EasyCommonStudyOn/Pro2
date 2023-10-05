from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True)

    def __str__(self):
        return f'Profile of {self.user.username}'


"""
Профиль пользователя будет содержать дату рождения пользователя и его
фотографию.
Поле user со взаимосвязью один-к-одному будет использоваться для
ассоциирования профилей с пользователями. С по мощью параметра on_
delete=models.CASCADE мы принудительно удаляем связанный объект Profile
при удалении объекта User. Поле date_of_birth является экземпляром класса DateField. Мы сделали
это поле опциональным посредством blank=True, и мы разрешаем нулевые
значения посредством null=True.
Поле photo является экземпляром класса ImageField. Мы сделали это поле
опциональным посредством blank=True. Класс ImageField управляет хране-
нием файлов изображений. Он проверяет, что предоставленный файл яв-
ляется валидным изображением, сохраняет файл изображения в каталоге,
указанном параметром upload_to, и сохраняет относительный путь к файлу
в связанном поле базы данных. Класс ImageField по умолчанию транслирует-
ся в столбец VARHAR(100) в базе данных. Если значение оставлено пустым, то
будет сохранена пустая строка."""


class Contact(models.Model):
    user_from = models.ForeignKey(
        User,
        related_name='rel_from_set',
        on_delete=models.CASCADE
    )
    user_to = models.ForeignKey(
        User,
        related_name='rel_to_set',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'

    """
    В приведенном выше исходном коде показана модель Contact, которая
будет использоваться для взаимосвязей пользователей. Она содержит сле-
дующие поля:
• user_from: внешний ключ (ForeignKey) для пользователя, который созда-
ет взаимосвязь;
• user_to: внешний ключ (ForeignKey) для пользователя, на которого есть
подписка;
• created: поле DateTimeField с параметром auto_now_add=True для хранения
времени создания взаимосвязи."""


user_model = get_user_model()
user_model.add_to_class('following',
                        models.ManyToManyField('self',
                                               through=Contact,
                                               related_name='followers',
                                               symmetrical=False))
"""
Здесь модель User извлекается встроенной в Django типовой функцией
get_user_model(). Метод add_to_class() моделей Django применяется для того,
чтобы динамически подправлять модель User.
Имейте в виду, что использование метода add_to_class() не является реко-
мендуемым способом добавления полей в модели. Тем не менее в данном слу-
чае его можно использовать, чтобы избежать создания конкретно-прикладной
модели User, сохраняя все преимущества встроенной в Django модели User."""