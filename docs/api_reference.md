# HealthSphere REST API Specification & Interoperability

## Overview
All HealthSphere programmatic interfaces follow RESTful design principles and provide OpenAPI 3.0 compliant schema documentation available interactively at `/api/docs/` and `/api/redoc/`.

## Endpoints Summary
- `GET /api/v1/health/`: System health probe.
- `GET /api/v1/patients/`: Patient directory and clinical summaries.
- `GET /api/v1/appointments/`: Appointment booking and scheduling.
- `GET /api/v1/prescriptions/`: Electronic prescription issuance.
- `GET /api/v1/laboratory/`: Lab orders, specimen collection, and results.
- `GET /api/v1/billing/`: Invoices and payments.
- `GET /api/v1/analytics/`: Executive KPIs and clinical quality indicators.
