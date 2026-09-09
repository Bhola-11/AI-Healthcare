from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('<uuid:appointment_id>/checkin/', views.check_in_patient, name='checkin'),
    path('', views.appointment_list, name='list'),
    path('book/', views.book_appointment, name='book'),
]
