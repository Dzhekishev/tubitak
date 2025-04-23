from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import *
from django.contrib import messages
from .serializers import *
from django.db.models.functions import Lower
from rest_framework.response import *
from django.http import Http404, JsonResponse
from rest_framework.decorators import api_view
from rest_framework import filters
import django_filters
from rest_framework import permissions
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required  # Если нужно ограничить для авторизованных


class CameraView(generics.ListCreateAPIView):
    queryset = Camera.objects.all()
    serializer_class = Camera_Serializers
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['id', 'title']


def camera_list_view(request):
    search_query = request.GET.get('title', '')
    cameras = Camera.objects.filter(Q(title__icontains=search_query)) if search_query else Camera.objects.all()
    return render(request, 'myapp/page_detail.html', {'cameras': cameras})


def search_camera(request):
    query = request.GET.get('query', '').strip()
    if query:
        cameras = Camera.objects.annotate(lower_title=Lower('title')) \
            .filter(lower_title__icontains=query.lower())
        results = []
        for camera in cameras:
            pages = camera.page_set.all()
            for page in pages:
                results.append({
                    'camera_id': camera.id,
                    'camera_title': camera.title,
                    'page_id': page.id,
                    'free': page.free,
                    'full': page.full,
                    'rezervation': page.rezervation
                })
    else:
        results = []
    return JsonResponse({'results': results})


def search_page(request):
    return render(request, 'myapp/search.html')


class PageView(generics.ListCreateAPIView):
    queryset = Page.objects.all()
    serializer_class = Page_Serializers


def page_detail(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    cameras = page.camera.all()

    # Добавляем сообщения в контекст
    message = None
    if 'booking_message' in request.session:
        message = request.session.pop('booking_message')

    return render(request, 'page_detail.html', {
        'page': page,
        'cameras': cameras,
        'message': message
    })


def get_camera_data(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    pages = camera.page_set.all()

    if pages.exists():
        page = pages.first()
        return JsonResponse({
            'free': page.free,
            'full': page.full,
            'rezervation': page.rezervation
        })
    return JsonResponse({'error': 'Нет связанных страниц для этой камеры'}, status=404)


@csrf_exempt
@require_POST  # Гарантируем, что это POST-запрос
def reserve_parking(request, page_id):
    page = get_object_or_404(Page, id=page_id)

    try:
        # Проверяем, есть ли свободные места
        if page.free <= 0:
            raise ValidationError('Нет свободных мест для бронирования')

        # Обновляем данные
        page.free -= 1
        page.rezervation += 1
        page.save()

        # Для AJAX-запросов возвращаем JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'free': page.free,
                'reserved': page.rezervation,
                'full': page.full
            })

        # Для обычных запросов используем сессию для сообщения
        request.session['booking_message'] = 'Место успешно забронировано!'
        return redirect('page_detail', page_id=page.id)

    except ValidationError as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

        request.session['booking_message'] = str(e)
        return redirect('page_detail', page_id=page.id)


# Новая функция для обработки бронирования через форму
@login_required  # Опционально, если нужно только для авторизованных
def reserve_spot(request, page_id):
    if request.method == 'POST':
        return reserve_parking(request, page_id)
    return redirect('page_detail', page_id=page_id)