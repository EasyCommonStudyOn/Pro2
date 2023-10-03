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
"""

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .forms import LoginForm


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
