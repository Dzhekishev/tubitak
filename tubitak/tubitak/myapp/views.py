from myapp.models import Camera, Page, Reservation
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
from django.views.decorators.http import require_POST
from .models import Page
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import qrcode
import io
import base64
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Page, Camera, Reservation
from django.utils import timezone
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime



# View for камеры
class Camera_View(generics.ListCreateAPIView):
    queryset= Camera.objects.all()
    serializer_class=Camera_Serializers

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['id', 'title']

# View for page
class Page_View(generics.ListCreateAPIView):
    queryset=Page.objects.all()
    serializer_class=Page_Serializers

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['id', 'camera']


#main page
def index(request):
    cameras = Camera.objects.all()
    pages = Page.objects.all()
    return render(request, 'index.html', {'pages': pages})

def index(request):
    query = request.GET.get('q')
    pages = Page.objects.all()

    if query:
        pages = pages.filter(camera__title__icontains=query).distinct()

    # Разделяем на с местами и без
    pages_with_space = pages.filter(free__gt=0)
    pages_full = pages.filter(free=0)

    return render(request, 'index.html', {
        'pages_with_space': pages_with_space,
        'pages_full': pages_full,
        'query': query
    })


# view for camera html
def camera_list(request):
    cameras = Camera.objects.all()
    return render(request, 'camera_list.html', {'cameras': cameras})


# view for page html
def page_list(request):
    pages = Page.objects.all()
    return render(request, 'page_list.html', {'pages': pages})

# filtr free full
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


#reservation
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



# increase reservation




@csrf_exempt
def ajax_reserve_camera(request):
    if request.method == 'POST' and request.user.is_authenticated:
        page_id = request.POST.get('page_id')
        camera_id = request.POST.get('camera_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            page = Page.objects.get(id=page_id)
            camera = Camera.objects.get(id=camera_id)

            # Проверка свободных мест
            if page.free <= 0:
                return JsonResponse({'success': False, 'message': 'No free spots left.'})

            # Сохраняем бронирование
            start_dt = parse_datetime(start_time)
            end_dt = parse_datetime(end_time)

            # Проверка: есть ли бронирования, которые пересекаются
            conflict = Reservation.objects.filter(
                camera=camera,
                end_time__gt=start_dt,
                start_time__lt=end_dt
            ).exists()

            if conflict:
                return JsonResponse({
                    'success': False,
                    'message': 'This time slot is already reserved.'
                })

            reservation = Reservation.objects.create(
                user=request.user,
                page=page,
                camera=camera,
                start_time=start_dt,
                end_time=end_dt
            )

            # Обновляем статистику
            page.free -= 1
            page.rezervation += 1
            page.save()

            return JsonResponse({
                'success': True,
                'redirect_url': f"/reservation/qr/{page.id}/{camera.id}/"
            })

        except (Page.DoesNotExist, Camera.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Page or camera not found.'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})

#page with statistic(admin panel)
@staff_member_required
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



    reservations = Reservation.objects.select_related('user', 'camera', 'page').order_by('-created_at')

    context = {
            'pages': pages,
            'reservations': reservations,
        }
    return render(request, 'dashboard.html', {
        'pages': pages,
        'reservations': reservations
    })

# export info to exel
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="parkings.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Free', 'Full', 'Reserved', 'Cameras'])

    for page in Page.objects.all():
        cameras = ', '.join([cam.title for cam in page.camera.all()])
        writer.writerow([page.id, page.free, page.full, page.rezervation, cameras])

    return response


# qr code
def reservation_qr(request, page_id, camera_id):
    data = f"Reservation | Page: {page_id}, Camera: {camera_id}"

    qr = qrcode.make(data)
    buffer = io.BytesIO()
    qr.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'myapp/qr_page.html', {'img_data': img_str, 'data': data})


# registration



# 🔧 Кастомная форма регистрации
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            login(request, user)
            return redirect('page_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})



#administration
class AdminLoginView(LoginView):
    template_name = 'admin_login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse_lazy('dashboard')
        return reverse_lazy('index')