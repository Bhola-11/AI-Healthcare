from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('', views.facility_list, name='list'),
    path('create/', views.facility_create, name='create'),
    path('<uuid:facility_id>/', views.facility_detail, name='detail'),
]
