from django.urls import path
from .views import*
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include
from django.urls import path, include
from myapp import views
from .views import page_detail
from .views import camera_list_view, search_camera


urlpatterns=[
    path('camera/',views.CameraView.as_view()),
    path('get_camera_data/<int:camera_id>/', get_camera_data, name='get_camera_data'),
    path('camerafil/', camera_list_view, name='camera-list'),
    path('search/', search_camera, name='search_camera'),
    path('page',views.PageView.as_view()),
    path('page/<int:page_id>/', views.page_detail, name='page_detail'),
    path('reserve/<int:page_id>/', views.reserve_parking, name='reserve_parking'),

]


urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
urlpatterns=format_suffix_patterns(urlpatterns)