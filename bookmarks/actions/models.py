from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Action(models.Model):
    user = models.ForeignKey('auth.User',
                             related_name='actions',
                             on_delete=models.CASCADE)
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    target_ct = models.ForeignKey(ContentType,
                                  blank=True,
                                  null=True,
                                  related_name='target_obj',
                                  on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=True,
                                            blank=True)
    target = GenericForeignKey('target_ct', 'target_id')

    class Meta:
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['target_ct', 'target_id']),
        ]
        ordering = ['-created']


"""
В приведенном выше исходном коде показана модель Action, которая бу-
дет использоваться для хранения действий пользователя. Поля этой модели
таковы:
• user: пользователь, выполнивший действие; это внешний ключ (ForeignKey)
для встроенной в Django модели User;
• verb: глагол, описывающий действие, которое выполнил пользователь;
• created: дата и время создания этого действия. Параметр auto_now_
add=True используется для того, чтобы автоматически устанавливать
текущую дату и время при первом сохранении объекта в базе данных.
В Meta-классе модели был определен индекс базы данных в убывающем
порядке по полю created. Кроме того, был добавлен атрибут ordering, чтобы
сообщать Django, что по умолчанию результаты следует сортировать по полю
created в убывающем порядке.
В этой базовой модели можно хранить только такие действия, как: пользо-
ватель X что-то сделал. Необходимо иметь дополнительное поле ForeignKey,
чтобы хранить действия, связанные с целевым объектом target, например
пользователь X пометил изображение Y закладкой или теперь пользователь
X подписан на пользователя Y. Как вы уже знаете, обычный внешний ключ
(ForeignKey) может указывать только на одну модель.
• target_ct: поле ForeignKey, указывающее на модель ContentType;
• target_id: PositiveIntegerField для хранения первичного ключа связан-
ного объекта;
• target: поле GenericForeignKey для связанного объекта на основе комби-
нации двух предыдущих полей.
Кроме того, был добавлен многопольный индекс, включающий поля target_
ct и target_id."""


