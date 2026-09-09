from django.urls import path
from . import views

app_name = 'clinical_records'

urlpatterns = [
    path('encounters/', views.encounter_list, name='encounters'),
    path('consultation/<uuid:encounter_id>/', views.consultation_workspace, name='consultation'),
    path('consultation/<uuid:encounter_id>/add-diagnosis/', views.add_diagnosis, name='add_diagnosis'),
]
