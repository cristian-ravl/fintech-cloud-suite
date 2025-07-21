# FinTech Cloud Suite - Multi-Product Cloud Platform

A comprehensive cloud governance, DevOps automation, and banking-as-a-service platform designed for regulated financial environments.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    FinTech Cloud Suite                         │
├─────────────────────────────────────────────────────────────────┤
│  🔐 Cloud Governance & Compliance Platform                     │
│  ├── OPA Policy Engine (Open Policy Agent)                    │
│  ├── Multi-Cloud Resource Scanner (AWS/Azure/GCP)             │
│  ├── Compliance Dashboard (React + Chart.js)                  │
│  └── Policy Results API (FastAPI)                             │
├─────────────────────────────────────────────────────────────────┤
│  ⚙️ DevOps Automation Platform                                 │
│  ├── CI/CD Pipeline Templates (GitHub Actions/GitLab CI)      │
│  ├── Security Scanning (tfsec, Trivy, Checkov, Snyk)         │
│  ├── Terraform Modules (S3, IAM, RDS with compliance)        │
│  └── Infrastructure Testing (Terratest)                       │
├─────────────────────────────────────────────────────────────────┤
│  🏦 Banking-as-a-Service Platform                              │
│  ├── API Gateway (Kong + Postgres)                            │
│  ├── Identity & Fraud Detection (Veriff/Trulioo)             │
│  ├── Core Banking APIs (Accounts, KYC, Payments)             │
│  └── Compliance Logging & Audit Trail                         │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for dashboard development)
- Cloud credentials (AWS/Azure/GCP) configured

### Start the Cloud Governance Platform

```bash
# Clone the repository
git clone https://github.com/cristian-ravl/fintech-cloud-suite.git
cd fintech-cloud-suite

# Start OPA and Policy Scanner services
docker-compose up -d

# Verify services are running
curl http://localhost:8181/health    # OPA Health Check
curl http://localhost:8080/health    # Policy Scanner Health Check

# View API documentation
open http://localhost:8080/docs      # Swagger UI
```

### Run a Compliance Scan

```bash
# Start a multi-cloud compliance scan
curl -X POST "http://localhost:8080/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "cloud_providers": ["aws", "azure", "gcp"],
    "resource_types": ["aws_s3_bucket", "azure_storage_account"],
    "policies": ["s3-encryption-required"]
  }'

# Check scan status
curl http://localhost:8080/scan/{scan_id}/status

# Get detailed results
curl http://localhost:8080/scan/{scan_id}/results
```

## 📊 Features & Components

### 🔐 Cloud Governance & Compliance Platform ✅ **COMPLETED**

**OPA Policy Engine with Multi-Cloud Scanning**

- **Open Policy Agent Integration**: Containerized OPA server with health monitoring
- **Rego Policies**: Production-ready policies for compliance frameworks (SOC2, PCI-DSS, GDPR, HIPAA, ISO27001)
- **Multi-Cloud Resource Scanning**: 
  - AWS Config API integration for resource inventory
  - Azure Resource Manager and Policy Insights APIs
  - Google Cloud Asset Inventory API
- **RESTful API**: FastAPI service with async operations and background scanning
- **Compliance Reporting**: Detailed violation reports with remediation guidance

**Key Endpoints:**
- `GET /health` - Service health and OPA connectivity
- `POST /scan` - Start compliance scan across cloud providers
- `GET /scan/{id}/status` - Real-time scan progress
- `GET /scan/{id}/results` - Detailed compliance results
- `POST /evaluate` - Direct policy evaluation for resources
- `GET /policies` - List available OPA policies

### ⚙️ DevOps Automation Platform 🔨 **IN PROGRESS**

**CI/CD Pipeline Templates for Regulated Environments**

- GitHub Actions and GitLab CI templates with security scanning
- Integrated security tools: tfsec, Trivy, Checkov, Snyk
- Terraform plan/apply approval gates for production deployments
- Automated compliance validation in CI/CD pipelines

**Reusable Terraform Modules**

- S3 module with encryption and access logging enabled by default
- IAM roles with least privilege principle enforcement
- RDS modules with audit logging and encryption
- Comprehensive testing with Terratest and Checkov

### 🏦 Banking-as-a-Service Platform 📋 **PLANNED**

**API Gateway Layer**

- Kong Gateway with PostgreSQL backend for 500+ banking APIs
- OpenAPI specifications for all endpoints
- API key-based authentication and rate limiting
- Comprehensive logging and monitoring

**Identity & Fraud Detection**

- Integration with Veriff and Trulioo for identity verification
- Risk scoring and fraud detection algorithms
- Compliant audit trail with encrypted logging
- Real-time decision APIs for identity onboarding
