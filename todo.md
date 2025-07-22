## 📌 Product Backlog: Multi-Product FinTech Cloud Suite

### ✅ Epic: Cloud Governance & Compliance Platform

#### ✅ Task: Set up policy engine (OPA) and integrate with cloud resource scanner - **COMPLETED**
- **Subtasks:**
  - [x] Install OPA in a containerized service ✅ (docker-compose.yml)
  - [x] Write example Rego policy: "S3 buckets must be encrypted" ✅ (policies/aws_s3_encryption.rego)
  - [x] Connect to AWS Config to retrieve resource inventory ✅ (aws_client.py)
  - [x] Connect to Azure Policy and GCP Asset Inventory ✅ (azure_client.py, gcp_client.py)
  - [x] Normalize resources into a common schema for OPA ✅ (models.py)
  - [x] Return policy pass/fail results via API ✅ (FastAPI /evaluate endpoint)
- **Acceptance Criteria:**
  - ✅ Test run of policy evaluation returns results for at least 20 resources
  - ✅ Results show pass/fail + suggested remediation
- **Status:** ✅ **COMPLETED** - PR #7 ready for merge
- **Branch:** `feature/opa-policy-engine` | **PR:** [#7](https://github.com/cristian-ravl/fintech-cloud-suite/pull/7)
- **GitHub Project:** [FinTech Cloud Suite Development](https://github.com/users/cristian-ravl/projects/2)

#### 🔧 Task: Build compliance dashboard with policy results
- **Subtasks:**
  - [ ] Build frontend React module with table + chart views
  - [ ] Group violations by policy name, cloud account, severity
  - [ ] Use Chart.js or D3 for visual charts
  - [ ] Link each violation to remediation documentation
  - [ ] Display historical compliance trend over time
- **Acceptance Criteria:**
  - Dashboard renders policy results for 3 sample rules
  - UI includes filtering by cloud account and severity

---

### ✅ Epic: DevOps Automation Platform

#### 🔧 Task: Create CI/CD pipeline templates for regulated environments
- **Subtasks:**
  - [ ] Draft GitHub Actions and GitLab CI templates
  - [ ] Include steps for tfsec, Trivy, Checkov, and Snyk
  - [ ] Add workflow for Terraform plan + apply approval gate
  - [ ] Write test repo with mock IaC files to validate templates
- **Acceptance Criteria:**
  - Pipelines execute successfully in test repo with all security steps passing

#### 🔧 Task: Develop reusable Terraform modules with compliance defaults
- **Subtasks:**
  - [ ] Create Terraform module: S3 with encryption and logging enabled
  - [ ] Create Terraform module: IAM roles with least privilege
  - [ ] Create Terraform module: RDS with audit logging
  - [ ] Write unit tests using Terratest or Checkov
  - [ ] Publish modules to GitHub with documentation
- **Acceptance Criteria:**
  - Each module deploys in test environment and passes validation
  - README includes example usage and compliance notes

---

### ✅ Epic: Banking-as-a-Service Platform

#### 🔧 Task: Design API Gateway layer for 500+ banking APIs
- **Subtasks:**
  - [ ] Set up Kong Gateway with Postgres backend
  - [ ] Add route definitions for 10 sample APIs (accounts, KYC, payments)
  - [ ] Define OpenAPI specs (Swagger) for each endpoint
  - [ ] Enable API key-based authentication
  - [ ] Implement rate limiting and logging plugins
- **Acceptance Criteria:**
  - 10 APIs available via gateway with key-based access and rate limits
  - Swagger UI shows documented endpoints

#### 🔧 Task: Implement identity & fraud detection API
- **Subtasks:**
  - [ ] Design API endpoint for identity onboarding (upload ID)
  - [ ] Integrate with Veriff or Trulioo for ID verification
  - [ ] Return response with verification status and risk score
  - [ ] Log each transaction with metadata (timestamp, user ID, result)
  - [ ] Store audit trail in compliant format (e.g., hashed logs)
- **Acceptance Criteria:**
  - New identity onboarding runs through verification and logs result
  - Risk score and provider decision are exposed via internal API

---
