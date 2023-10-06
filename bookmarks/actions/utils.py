from django.contrib.contenttypes.models import ContentType
from .models import Action
import datetime
from django.utils import timezone


def create_action(user, verb, target=None):
    # Проверяем, не было ли каких-либо аналогичных действий,
    # совершенных за последнюю минуту
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=60)
    similar_actions = Action.objects.filter(user=user,
                                            verb=verb,
                                            created__gte=last_minute)
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(target_content_type=target_ct,
                                                 target_object_id=target.id)
    if not similar_actions.exists():
        # Никаких существующих действий не найдено, создаем новое действие
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True
    return False


"""
Функция create_action() была изменена, чтобы избегать сохранения по-
вторяющихся действий и возвращать булево значение, сообщающее о том,
не было ли действие сохранено. Вот как игнорируются повторы:
1) сначала берется текущее время. Это делается с по мощью встроенного
в Django метода timezone.now(). Указанный метод делает то же самое,
что и datetime.datetime.now(), но возвращает объект с учетом часового
пояса. Django предоставляет настроечный параметр USE_TZ, которым
активируется либо деактивируется поддержка часового пояса. Стан-
дартный файл settings.py, созданный с по мощью команды startproject,
содержит USE_TZ=True;
2) переменная last_minute используется для хранения даты/времени дав-
ностью одна минута назад и для получения любых идентичных дей-
ствий, выполненных пользователем с тех пор;
3) если за последнюю минуту не было идентичного действия, то создается
объект Action. При этом возвращается True, если объект Action был соз-
дан, либо False в противном случае."""


