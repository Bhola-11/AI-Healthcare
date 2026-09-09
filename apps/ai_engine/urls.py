from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('triage/', views.triage_view, name='triage'),
]
