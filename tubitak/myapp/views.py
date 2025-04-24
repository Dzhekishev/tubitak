from myapp.models import Camera, Page
from myapp.serializers import*
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import filters
import django_filters
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from .models import Page
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


class Camera_View(generics.ListCreateAPIView):
    queryset= Camera.objects.all()
    serializer_class=Camera_Serializers

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['id', 'title']
class Page_View(generics.ListCreateAPIView):
    queryset=Page.objects.all()
    serializer_class=Page_Serializers

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['id', 'camera']

def index(request):
    cameras = Camera.objects.all()
    pages = Page.objects.all()
    return render(request, 'index.html', {'cameras': cameras, 'pages': pages})


def camera_list(request):
    cameras = Camera.objects.all()
    return render(request, 'camera_list.html', {'cameras': cameras})

def page_list(request):
    pages = Page.objects.all()
    return render(request, 'page_list.html', {'pages': pages})


def page_list(request):
    query = request.GET.get('q')
    pages = Page.objects.all()

    if query:
        pages = pages.filter(camera__title__icontains=query).distinct()

    # Разделяем на с местами и без
    pages_with_space = pages.filter(free__gt=0)
    pages_full = pages.filter(free=0)

    return render(request, 'page_list.html', {
        'pages_with_space': pages_with_space,
        'pages_full': pages_full,
        'query': query
    })

def reserve_camera(request, page_id, camera_id):
    page = get_object_or_404(Page, id=page_id)
    if page.free > 0:
        page.rezervation += 1
        page.free -= 1
        page.save()
        messages.success(request, "Успешно забронировано!")
    else:
        messages.warning(request, "Нет свободных мест.")
    return redirect('page_list')




@require_POST
def ajax_reserve_camera(request):
    page_id = request.POST.get('page_id')
    camera_id = request.POST.get('camera_id')

    try:
        page = Page.objects.get(id=page_id)
        if page.free > 0:
            page.free -= 1
            page.rezervation += 1
            page.save()
            return JsonResponse({'success': True, 'free': page.free, 'rezervation': page.rezervation})
        else:
            return JsonResponse({'success': False, 'message': 'No free spots left'})
    except Page.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Invalid request'})






@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Access denied. Admins only.")

    pages = Page.objects.all()

    # Фильтрация по названию камеры
    query = request.GET.get('q')
    if query:
        pages = pages.filter(camera__title__icontains=query).distinct()

    # Сортировка
    sort = request.GET.get('sort')
    if sort:
        pages = pages.order_by(sort)

    # Обработка обновления
    if request.method == 'POST':
        page_id = request.POST.get('page_id')
        page = Page.objects.get(id=page_id)
        page.free = int(request.POST.get('free'))
        page.full = int(request.POST.get('full'))
        page.rezervation = int(request.POST.get('rezervation'))
        page.save()
        return redirect('dashboard')

    return render(request, 'myapp/dashboard.html', {'pages': pages})


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="parkings.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Free', 'Full', 'Reserved', 'Cameras'])

    for page in Page.objects.all():
        cameras = ', '.join([cam.title for cam in page.camera.all()])
        writer.writerow([page.id, page.free, page.full, page.rezervation, cameras])

    return response


