from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('invoices/', views.invoice_list, name='invoices'),
    path('invoices/<uuid:invoice_id>/', views.invoice_detail, name='detail'),
    path('invoices/<uuid:invoice_id>/pay/', views.process_payment, name='pay'),
]
