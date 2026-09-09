import os

apps = [
    ('accounts', 'Accounts', 'User Accounts, Roles and Authentication'),
    ('audit', 'Audit', 'System Security and Audit Logging'),
    ('facilities', 'Facilities', 'Hospitals, Clinics, Wards and Beds'),
    ('doctors', 'Doctors', 'Physicians, Specialties and Rostering'),
    ('patients', 'Patients', 'Patient Demographics and Vitals'),
    ('appointments', 'Appointments', 'Scheduling and Queue Management'),
    ('clinical_records', 'ClinicalRecords', 'EMR, Encounters and SOAP Notes'),
    ('prescriptions', 'Prescriptions', 'Digital Rx and Dosing Orders'),
    ('pharmacy', 'Pharmacy', 'Formulary, Stock and Dispensation'),
    ('laboratory', 'Laboratory', 'Diagnostic Orders, Pathology and Results'),
    ('billing', 'Billing', 'Invoices, Tariff Schedules and Payments'),
    ('insurance', 'Insurance', 'Policies, Pre-Auth and Claims Processing'),
    ('notifications', 'Notifications', 'Multi-channel Alerts and Reminders'),
    ('analytics', 'Analytics', 'Clinical and Operational Performance KPIs'),
    ('ai_engine', 'AIEngine', 'Clinical Decision Support and Triage'),
    ('api', 'API', 'REST API ViewSets and OpenAPI Schemas'),
]

for app_name, verbose_class, doc in apps:
    app_dir = os.path.join('apps', app_name)
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(os.path.join(app_dir, 'migrations'), exist_ok=True)
    
    # apps.py
    apps_py = f"""from django.apps import AppConfig

class {verbose_class}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
    verbose_name = '{doc}'
"""
    with open(os.path.join(app_dir, 'apps.py'), 'w', encoding='utf-8') as f:
        f.write(apps_py)

    # __init__.py
    with open(os.path.join(app_dir, '__init__.py'), 'w', encoding='utf-8') as f:
        f.write(f"default_app_config = 'apps.{app_name}.apps.{verbose_class}Config'\n")

    # migrations/__init__.py
    with open(os.path.join(app_dir, 'migrations', '__init__.py'), 'w', encoding='utf-8') as f:
        f.write("# Migrations package\n")

    # urls.py
    urls_py = f"""from django.urls import path

app_name = '{app_name}'

urlpatterns = [
]
"""
    urls_path = os.path.join(app_dir, 'urls.py')
    if not os.path.exists(urls_path):
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(urls_py)

    # models.py
    models_path = os.path.join(app_dir, 'models.py')
    if not os.path.exists(models_path):
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(f'"""Models for {app_name} domain."""\nfrom django.db import models\n')

    # views.py
    views_path = os.path.join(app_dir, 'views.py')
    if not os.path.exists(views_path):
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(f'"""Views for {app_name} domain."""\nfrom django.shortcuts import render\n')

    # admin.py
    admin_path = os.path.join(app_dir, 'admin.py')
    if not os.path.exists(admin_path):
        with open(admin_path, 'w', encoding='utf-8') as f:
            f.write(f'"""Admin configuration for {app_name}."""\nfrom django.contrib import admin\n')

print("All 16 app structures successfully generated.")
