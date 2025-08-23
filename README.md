# PrawoAsystent AI

This repository contains the full source code for the PrawoAsystent AI application, an AI-powered legal document assistant.

## Project Structure

- `app/`: Contains the backend FastAPI application.
- `frontend/`: Contains frontend components and hooks (React/TypeScript).
- `k8s/`: Contains Kubernetes deployment configurations.
- `monitoring/`: Contains Grafana dashboards and Prometheus alert configurations.
- `tests/`: Contains the Pytest test suite.
- `.github/workflows`: Contains the CI/CD pipeline configuration.
- `Dockerfile`: For containerizing the backend application.
- `requirements.txt`: Python dependencies.

## Setup and Installation

1.  **Install dependencies and download models:**
    ```bash
    ./setup.sh
    ```

2.  **Set up environment variables:**
    Create a `.env` file in the root directory and populate it with the necessary variables (see `app/core/config.py`).

3.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

## Production Deployment Checklist

This checklist is taken from section 20 of the project's architectural plan.

### 🔒 SECURITY:
- [ ] Strong secret keys generated (min 32 chars)
- [ ] Database credentials secured in K8s secrets
- [ ] API keys encrypted and rotated
- [ ] HTTPS enforced with valid SSL certificates
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation and sanitization
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection headers
- [ ] CSRF protection implemented
- [ ] Password hashing with Argon2
- [ ] Account lockout after failed attempts
- [ ] Audit logging enabled

### 🏗️ INFRASTRUCTURE:
- [ ] Multi-zone Kubernetes deployment
- [ ] Horizontal Pod Autoscaler configured
- [ ] Pod Disruption Budgets set
- [ ] Resource limits and requests defined
- [ ] Health checks implemented
- [ ] Liveness and readiness probes
- [ ] Network policies for security
- [ ] Persistent volumes for data
- [ ] Load balancer configured
- [ ] CDN for static assets

### 💾 DATABASE:
- [ ] Connection pooling optimized
- [ ] Database indexes created
- [ ] Backup strategy implemented
- [ ] Point-in-time recovery enabled
- [ ] Read replicas for scaling
- [ ] Connection limits configured
- [ ] Query performance monitoring
- [ ] Data retention policies

### 📊 MONITORING:
- [ ] Prometheus metrics collection
- [ ] Grafana dashboards created
- [ ] Alert rules configured
- [ ] Log aggregation (ELK/Loki)
- [ ] Error tracking (Sentry)
- [ ] APM tracing
- [ ] Uptime monitoring
- [ ] Performance monitoring

### 🔧 OPERATIONS:
- [ ] CI/CD pipeline implemented
- [ ] Blue-green deployment strategy
- [ ] Rollback procedures tested
- [ ] Disaster recovery plan
- [ ] Backup verification
- [ ] Incident response procedures
- [ ] On-call rotation setup
- [ ] Documentation complete

### 📋 COMPLIANCE:
- [ ] GDPR compliance implemented
- [ ] Data export functionality
- [ ] Data deletion (right to be forgotten)
- [ ] Privacy policy updated
- [ ] Terms of service updated
- [ ] Cookie consent implemented
- [ ] Data processing agreements
- [ ] Security audit completed

### 🧪 TESTING:
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Load testing completed
- [ ] Security testing (OWASP)
- [ ] Penetration testing
- [ ] User acceptance testing
- [ ] Performance benchmarking
