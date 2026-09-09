from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('search/', views.audit_search_view, name='search'),
    path('export/', views.audit_export_csv, name='export_csv'),
]
