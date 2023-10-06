from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actions.utils import create_action
import redis
from django.conf import settings

# соединить с redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


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
        create_action(request.user, 'bookmarked image', new_image)
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
    # увеличить общее число просмотров изображения на 1
    total_views = r.incr(f'image:{image.id}:views')
    r.zincrby('image_ranking', 1,
              image.id)  # Команда zincrby() используется для сохранения просмотров изображений в сортированном множестве с ключом image:ranking.
    return render(request, 'images/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})


@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом,
        # то доставить первую страницу
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # Если AJAX-запрос и страница вне диапазона,
            # то вернуть пустую страницу
            return HttpResponse('')
        # Если страница вне диапазона,
        # то вернуть последнюю страницу результатов
        images = paginator.page(paginator.num_pages)
    if images_only:
        return render(request,
                      'images/image/list_images.html',
                      {'section': 'images',
                       'images': images})
    return render(request,
                  'images/image/list.html',
                  {'section': 'images',
                   'images': images})


"""
В этом представлении создается набор запросов QuerySet, чтобы извлекать
все изображения из базы данных. Затем формируется объект Paginator, чтобы
разбивать результаты на страницы, беря по восемь изображений на стра-
ницу. Извлекается HTTP GET-параметр page, чтобы получить запрошенный
номер страницы. Извлекается HTTP GET-параметр images_only, чтобы узнать,
должна ли прорисовываться вся страница целиком или же только новые
изображения. Мы будем прорисовывать всю страницу целиком, когда она
запрашивается браузером. Однако мы будем прорисовывать HTML только
с новыми изображениями в случае запросов Fetch API, поскольку мы будем
добавлять их в существующую HTML-страницу.
Исключение EmptyPage будет вызываться в случае, если запрошенная стра-
ница находится вне допустимого диапазона. Если это так и нужно прори-
совывать только изображения, то будет возвращаться пустой HttpResponse.
Такой подход позволит останавливать AJAX-ориентированное постраничное
разбиение на стороне клиента при достижении последней страницы. Резуль-
таты прорисовываются с использованием двух разных шаблонов:
• в случае HTTP-запросов на JavaScript, которые будут содержать пара-
метр images_only, будет прорисовываться шаблон list_images.html. Этот
шаблон будет содержать изображения только запрошенной страницы;
• в случае браузерных запросов будет прорисовываться шаблон list.html.
Этот шаблон будет расширять шаблон base.html, чтобы отображать всю
страницу целиком, и будет вставлять шаблон list_images.html, который
будет вставлять список изображений."""


@login_required
def image_ranking(request):
    # получить словарь рейтинга изображений
    image_ranking = r.zrange('image_ranking', 0, -1,
                             desc=True)[:10]
    image_ranking_ids = [int(id) for id in image_ranking]
    # получить наиболее просматриваемые изображения
    most_viewed = list(Image.objects.filter(
        id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    return render(request,
                  'images/image/ranking.html',
                  {'section': 'images',
                   'most_viewed': most_viewed})
