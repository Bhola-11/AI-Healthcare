from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('<uuid:patient_id>/timeline/', views.clinical_timeline, name='timeline'),
    path('', views.patient_list, name='list'),
    path('<uuid:patient_id>/', views.patient_detail, name='detail'),
    path('<uuid:patient_id>/vitals/', views.record_vitals, name='record_vitals'),
]
