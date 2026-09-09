from django.urls import path
from . import views

app_name = 'pharmacy'

urlpatterns = [
    path('inventory/', views.pharmacy_inventory, name='inventory'),
    path('workbench/', views.dispensing_workbench, name='workbench'),
    path('dispense/<uuid:rx_id>/', views.dispense_rx, name='dispense'),
]
