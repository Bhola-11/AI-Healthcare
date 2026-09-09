from django.urls import path
from . import views

app_name = 'insurance'

urlpatterns = [
    path('claims/', views.claim_list, name='claims'),
]
