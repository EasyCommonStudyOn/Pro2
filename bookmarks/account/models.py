from django.db import models
from django.conf import settings


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

