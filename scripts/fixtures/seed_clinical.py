import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
import django
django.setup()

from apps.clinical_records.models import ICD10DiagnosisCode, Encounter, SOAPNote
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile
from apps.facilities.models import Facility

def seed():
    codes = [
        ("I10", "Essential (primary) hypertension", 9, "Diseases of the circulatory system", "I10-I16", True, True),
        ("I25.10", "Atherosclerotic heart disease of native coronary artery", 9, "Diseases of the circulatory system", "I20-I25", True, True),
        ("I50.9", "Heart failure, unspecified", 9, "Diseases of the circulatory system", "I50", True, True),
        ("E11.9", "Type 2 diabetes mellitus without complications", 4, "Endocrine, nutritional and metabolic diseases", "E08-E13", True, True),
        ("E11.65", "Type 2 diabetes mellitus with hyperglycemia", 4, "Endocrine, nutritional and metabolic diseases", "E08-E13", True, True),
        ("E03.9", "Hypothyroidism, unspecified", 4, "Endocrine, nutritional and metabolic diseases", "E00-E07", True, True),
        ("J45.909", "Unspecified asthma, uncomplicated", 10, "Diseases of the respiratory system", "J40-J47", True, True),
        ("J44.9", "Chronic obstructive pulmonary disease, unspecified", 10, "Diseases of the respiratory system", "J40-J47", True, True),
        ("J18.9", "Pneumonia, unspecified organism", 10, "Diseases of the respiratory system", "J09-J18", True, False),
        ("K21.9", "Gastro-esophageal reflux disease without esophagitis", 11, "Diseases of the digestive system", "K20-K31", True, True),
        ("N18.3", "Chronic kidney disease, stage 3 (moderate)", 14, "Diseases of the genitourinary system", "N17-N19", True, True),
        ("M54.5", "Low back pain", 13, "Diseases of the musculoskeletal system", "M50-M54", True, False),
        ("F41.1", "Generalized anxiety disorder", 5, "Mental, Behavioral and Neurodevelopmental disorders", "F40-F48", True, True),
        ("F32.9", "Major depressive disorder, single episode, unspecified", 5, "Mental, Behavioral and Neurodevelopmental disorders", "F30-F39", True, True),
        ("R05", "Cough", 18, "Symptoms, signs and abnormal clinical findings", "R00-R09", True, False),
        ("R50.9", "Fever, unspecified", 18, "Symptoms, signs and abnormal clinical findings", "R50-R69", True, False),
    ]

    for code, desc, ch_num, ch_title, cat, billable, chronic in codes:
        ICD10DiagnosisCode.objects.get_or_create(
            code=code,
            defaults={
                'description': desc,
                'chapter_number': ch_num,
                'chapter_title': ch_title,
                'category_code': cat,
                'is_billable': billable,
                'is_chronic': chronic
            }
        )

    # Seed sample encounter
    patient = PatientProfile.objects.first()
    doctor = DoctorProfile.objects.first()
    facility = Facility.objects.first()

    if patient and doctor and facility:
        enc, _ = Encounter.objects.get_or_create(
            encounter_number="ENC-DEMO-2026-001",
            defaults={'patient': patient, 'doctor': doctor, 'facility': facility}
        )
        SOAPNote.objects.get_or_create(
            encounter=enc,
            defaults={
                'subjective': "Patient presents for routine follow-up of hypertension and diabetic management.",
                'objective': "Vitals: BP 128/82 mmHg, HR 74 bpm. Heart regular rate and rhythm.",
                'assessment': "1. Essential hypertension - well-controlled.\n2. Type 2 Diabetes Mellitus.",
                'plan': "Continue Amlodipine 5mg daily, Metformin 500mg BID. Repeat HbA1c in 3 months.",
                'is_signed': True
            }
        )

    print("ICD-10 clinical registry and sample encounter seeded.")

if __name__ == '__main__':
    seed()
