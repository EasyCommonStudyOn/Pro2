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
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard'})


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
