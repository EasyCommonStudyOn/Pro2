from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image


@login_required
def image_create(request):
    if request.method == 'POST':
        # форма отправлена
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():  # данные в форме валидны
            cd = form.cleaned_data
            new_image = form.save(commit=False)
        # назначить текущего пользователя элементу
        new_image.user = request.user
        new_image.save()
        messages.success(request,
                         'Image added successfully')
        # перенаправить к представлению детальной
        # информации о только что созданном элементе
        return redirect(new_image.get_absolute_url())

    else:
        # скомпоновать форму с данными,
        # предоставленными букмарклетом методом GET
        form = ImageCreateForm(data=request.GET)
    return render(request,
                  'images/image/create.html',
                  {'section': 'images',
                   'form': form})


"""
Здесь мы создали представление хранения изображений на сайте. В пред-
ставление image_create был добавлен декоратор login_required, чтобы предот-
вращать доступ неаутентифицированных пользователей. Вот как это пред-
ставление работает.
1. Для создания экземпляра формы необходимо предоставить начальные
данные через HTTP-запрос методом GET. Эти данные будут состоять
из атрибутов url и title изображения с внешнего веб-сайта. Оба па-
раметра будут заданы в запросе GET букмарклетом JavaScript, который
мы создадим позже. Пока же можно допустить, что эти данные будут
иметься в запросе.
2. После того как форма передана на обработку с по мощью HTTP-запроса
методом POST, она валидируется методом form.is_valid(). Если данные
в форме валидны, то создается новый экземпляр Image путем сохране-
ния формы методом form.save(commit=False). Новый экземпляр в базе
данных не сохраняется, если commit=False.
3. В новый экземпляр изображения добавляется связь с текущим пользо-
вателем, который выполняет запрос: new_image.user = request.user. Так
мы будем знать, кто закачивал каждое изображение.
4. Объект Image сохраняется в базе данных.
5. Наконец, с по мощью встроенного в Django фреймворка сообщений
создается сообщение об успехе, и пользователь перенаправляется на
канонический URL-адрес нового изображения."""


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request, 'images/image/detail.html',
                  {'section': 'images',
                   'image': image})
