# HealthSphere HIPAA Compliance & Security Guide

## Security Architecture Implementation
- **Cryptographic Chaining**: Every administrative, clinical, and billing access is recorded in `hs_audit_logs` with SHA-256 hash chaining.
- **Session Protection**: 30-minute idle session expiry, SameSite strict cookies, HttpOnly and Secure flags.
- **Role-Based Access Control**: Strict segregation between clinical practitioners and administrative personnel.
