from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse


class Image(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='images_created',
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    url = models.URLField(max_length=2000)
    image = models.ImageField(upload_to='images/%Y/%m/%d/')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True)
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='images_liked',
                                        blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('images:detail', args=[self.id,
                                              self.slug])


"""
Это модель, которая будет использоваться для хранения изображений на
платформе. Давайте посмотрим на поля данной модели:
• user: здесь указывается объект User, который сделал закладку на это
изображение. Это поле является внешним ключом, поскольку оно опре-
деляет взаимосвязь один-ко-многим: пользователь может отправлять
несколько изображений, но каждое изображение отправляется одним
пользователем. Мы использовали CASCADE для параметра on_delete, что-
бы связанные изображения удалялись при удалении пользователя;
• title: заголовок изображения;
• slug: короткое обозначение, содержащее только буквы, цифры, под-
черкивания или дефисы, которое будет использоваться для создания
красивых дружественных для поисковой оптимизации URL-адресов;
• url: изначальный URL-адрес этого изображения. Мы используем max_
length, чтобы определить максимальную длину, равную 2000 символов;
• image: файл изображения;
• description: опциональное описание изображения;
• created: дата и время, когда объект был создан в базе данных. Мы до-
бавили auto_now_add, чтобы устанавливать текущее время/дату автома-
тически при создании объекта.
В Meta-классе модели мы определили индекс базы данных в убывающем по-
рядке по полю created. Мы также добавили атрибут ordering, сообщая Django,
что по умолчанию он должен сортировать результаты по созданному полю.
Мы указываем убывающий порядок, используя дефис перед именем поля,
например -created, с тем чтобы новые изображения отображались первыми.Мы переопределим метод save() модели Image, чтобы автоматически гене-
рировать поля slug на основе значения поля title."""
