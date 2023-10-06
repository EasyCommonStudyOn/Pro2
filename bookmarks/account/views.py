"""
Базовое представление входа в систему делает следующее.
При вызове представления user_login с запросом методом GET посредством
инструкции form = LoginForm() создается экземпляр новой формы входа. За-
тем эта форма передается в шаблон.
Когда пользователь передает форму методом POST, выполняются следую-
щие ниже действия:
• посредством инструкции form = LoginForm(request.POST) создается эк-
земпляр формы с переданными данными;
• форма валидируется методом form.is_valid(). Если она невалидна, то
ошибки формы будут выведены позже в шаблоне (например, если поль-
зователь не заполнил одно из полей);
• если переданные на обработку данные валидны, то пользователь аутен-
тифицируется по базе данных методом authenticate(). Указанный метод
принимает объект request, параметры username и password и возвращает
объект User, если пользователь был успешно аутентифицирован, либо
None в противном случае. Если пользователь не был успешно аутенти-
фицирован, то возвращается сырой ответ HttpResponse с сообщением
Invalid login (Недопустимый логин);
• если пользователь успешно аутентифицирован, то статус пользователя
проверяется путем обращения к атрибуту is_active. Указанный атрибут
принадлежит модели User веб-фреймворка Django. Если пользователь
не активен, то возвращается HttpResponse с сообщением Disabled account
(Отключенная учетная запись);
• если пользователь активен, то он входит в систему. Пользователь зада-
ется в сеансе путем вызова метода login(). При этом возвращается сооб-
щение Authenticated successfully (Аутентификация прошла успешно).

Django предоставляет следующие представления на основе классов для
работы с аутентификацией. Все они расположены в django.contrib.auth.views:
• LoginView: оперирует формой входа и регистрирует вход пользователя;
• LogoutView: регистрирует выход пользователя.
Django предоставляет следующие ниже представления для оперирования
сменой пароля:
• PasswordChangeView: оперирует формой для смены пароля пользователя;
• PasswordChangeDoneView: представление страницы об успехе, на которую
пользователь перенаправляется после успешной смены пароля.
Django также содержит следующие ниже представления, позволяющие
пользователям сбрасывать свой пароль:
• PasswordResetView: позволяет пользователям сбрасывать свой пароль.
Генерирует одноразовую ссылку с токеном и отправляет ее на электрон-
ный ящик пользователя;
• PasswordResetDoneView: сообщает пользователям, что им было отправле-
но электронное письмо, содержащее ссылку на сброс пароля;
• PasswordResetConfirmView: позволяет пользователям устанавливать но-
вый пароль;
• PasswordResetCompleteView: представление страницы об успехе, на кото-
рую пользователь перенаправляется после успешного сброса пароля.

"""

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Contact
from actions.utils import create_action
from actions.models import Action


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        # Если пользователь подписан на других,
        # то извлечь только их действия
        actions = actions.select_related('user', 'user__profile')[:10].prefetch_related('target')[:10]
        """
        Аргумент user__profile используется для того, чтобы выполнять операцию
соединения на таблице Profile в одном SQL-запросе. Если вызвать select_related()
без передачи каких-либо аргументов, то он будет извлекать объекты
из всех взаимосвязей с внешними ключами ForeignKey. Следует всегда огра-
ничивать метод select_related() взаимосвязями, которые будут доступны
позже.Метод select_related() поможет повышать производительность при извле-
чении связанных объектов во взаимосвязях один-ко-многим. Однако он не
работает для взаимосвязей многие-ко-многим или многие-к-одному (поля
ManyToMany или обратного внешнего ключа ForeignKey). Django предлагает
другой QuerySet-метод под названием prefetch_related, который в допол-
нение к взаимосвязям, поддерживаемым методом select_related(), успеш-
но работает для взаимосвязей многие-ко-многим и многие-к-одному. Ме-
тод prefetch_related() выполняет отдельный поиск по каждой взаимосвязи
и соединяет результаты с по мощью Python. Этот метод также поддерживает
упреждающую выборку полей GenericRelation и GenericForeignKey."""
    actions = actions[:10]
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})


"""
Мы создали представление dashboard и применили к нему декоратор login_
required из фреймворка аутентификации. Декоратор login_required про-
веряет аутентификацию текущего пользователя.
Если пользователь аутентифицирован, то оно исполняет декорированное
представление; если пользователь не аутентифицирован, то оно перена-
правляет пользователя на URL-адрес входа с изначально запрошенным URL-
адресом в качестве GET-параметра с именем next.
При таком подходе представление входа перенаправляет пользователей
на URL-адрес, к которому они пытались обратиться после успешного входа.
Напомним, что с этой целью в шаблон входа был добавлен скрытый HTML-
элемент <input> с именем next.
Мы также определили переменную section. Эта переменная будет исполь-
зоваться для подсвечивания текущего раздела в главном меню сайта."""


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Создать новый объект пользователя,
            # но пока не сохранять его
            new_user = user_form.save(commit=False)
            # Установить выбранный пароль
            new_user.set_password(user_form.cleaned_data['password'])
            # Сохранить объект User
            new_user.save()
            # Создать профиль пользователя
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(
            instance=request.user.profile)
    return render(request,
                  'account/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


"""
Мы добавили новое представление edit, чтобы пользователи могли ре-
дактировать свою личную информацию. Мы добавили в него декоратор login_
required, поскольку только аутентифицированные пользователи могут
редактировать свои профили. В этом представлении используются две мо-
дельные формы: UserEditForm для хранения данных во встроенной модели
User и ProfileEditForm для хранения дополнительных персональных данных
в конкретно-прикладной модели Profile. В целях валидации переданных
данных вызывается метод is_valid() обеих форм. Если обе формы содержат
валидные данные, то обе формы сохраняются путем вызова метода save(),
чтобы обновить соответствующие объекты в базе данных."""


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  'account/user/list.html',
                  {'section': 'people',
                   'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    return render(request,
                  'account/user/detail.html',
                  {'section': 'people',
                   'user': user})


"""
Это простые представления списка и детальной информации для объ-
ектов User. Представление user_list получает всех активных пользователей.
Модель User содержит флаг is_active, который маркирует, считается учетная
запись пользователя активной или нет. Запрос фильтруется по параметру
is_active=True, чтобы возвращать только активных пользователей. Это пред-
ставление возвращает все результаты, но его можно улучшить, добавив по-
страничную разбивку так же, как это делалось для представления image_list.
В представлении user_detail используется функция сокращенного доступа
get_object_or_404(), чтобы извлекать активного пользователя с переданным
пользовательским именем (username). Данное представление возвращает
HTTP-ответ 404, если активный пользователь с переданным пользователь-
ским именем не найден."""


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
