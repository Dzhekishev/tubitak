from .views import*
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path, include
from myapp import views
from django.contrib.auth import views as auth_views



urlpatterns=[
    path('camera/',views.Camera_View.as_view()),
    path('page',views.Page_View.as_view()),
    path('', views.index, name='index'),
    path('cameras/', views.camera_list, name='camera_list'),
    path('pages/', views.page_list, name='page_list'),
    path('reserve/<int:page_id>/<int:camera_id>/', views.reserve_camera, name='reserve_camera'),
    path('ajax/reserve/', views.ajax_reserve_camera, name='ajax_reserve_camera'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]


urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
urlpatterns=format_suffix_patterns(urlpatterns)