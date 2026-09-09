from django.urls import path
from . import views

app_name = 'facilities'

urlpatterns = [
    path('bed-board/', views.bed_board_view, name='bed_board'),
    path('<uuid:facility_id>/bed-board/', views.bed_board_view, name='facility_bed_board'),
    path('', views.facility_list, name='list'),
    path('create/', views.facility_create, name='create'),
    path('<uuid:facility_id>/', views.facility_detail, name='detail'),
]
