from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('portal/', views.schedule_portal, name='portal'),
    path('', views.doctor_directory, name='directory'),
    path('<uuid:doctor_id>/', views.doctor_detail, name='detail'),
]
