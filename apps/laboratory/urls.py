from django.urls import path
from . import views

app_name = 'laboratory'

urlpatterns = [
    path('report/<uuid:order_id>/', views.lab_report_print, name='report_print'),
    path('orders/', views.lab_order_list, name='orders'),
    path('orders/<uuid:order_id>/', views.lab_order_detail, name='detail'),
    path('orders/<uuid:order_id>/signoff/', views.pathologist_signoff, name='signoff'),
]
