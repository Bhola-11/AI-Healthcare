from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('calendar/', views.calendar_schedule_view, name='calendar'),
    path('<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel'),
    path('queue/', views.live_queue_board, name='queue'),
    path('<uuid:appointment_id>/checkin/', views.check_in_patient, name='checkin'),
    path('', views.appointment_list, name='list'),
    path('book/', views.book_appointment, name='book'),
]
