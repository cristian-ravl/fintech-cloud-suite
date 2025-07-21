"""
Data models for Cloud Governance Platform
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    """Supported cloud providers"""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class ResourceType(str, Enum):
    """Common resource types across cloud providers"""
    S3_BUCKET = "aws_s3_bucket"
    EC2_INSTANCE = "aws_ec2_instance"
    RDS_INSTANCE = "aws_rds_instance"
    IAM_ROLE = "aws_iam_role"
    STORAGE_ACCOUNT = "azure_storage_account"
    VIRTUAL_MACHINE = "azure_virtual_machine"
    SQL_SERVER = "azure_sql_server"
    GCS_BUCKET = "gcp_storage_bucket"
    COMPUTE_INSTANCE = "gcp_compute_instance"
    CLOUD_SQL = "gcp_cloud_sql"


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks"""
    SOC2 = "SOC2"
    PCI_DSS = "PCI-DSS"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    ISO27001 = "ISO27001"


class Severity(str, Enum):
    """Policy violation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ResourceInventory(BaseModel):
    """Normalized cloud resource model"""
    resource_id: str
    resource_name: str
    resource_type: ResourceType
    cloud_provider: CloudProvider
    region: str
    account_id: str
    tags: Dict[str, str] = Field(default_factory=dict)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    
    # Additional metadata
    compliance_metadata: Dict[str, Any] = Field(default_factory=dict)
    security_groups: List[str] = Field(default_factory=list)
    encryption_status: Optional[Dict[str, Any]] = None


class PolicyViolation(BaseModel):
    """Policy violation details"""
    policy_id: str
    policy_name: str
    severity: Severity
    message: str
    remediation: str
    compliance_frameworks: List[ComplianceFramework] = Field(default_factory=list)
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class PolicyResult(BaseModel):
    """Result of policy evaluation for a resource"""
    resource_id: str
    resource_type: ResourceType
    cloud_provider: CloudProvider
    region: str
    account_id: str
    
    # Policy evaluation results
    compliant: bool
    policy_id: str
    policy_name: str
    evaluation_time: datetime = Field(default_factory=datetime.utcnow)
    
    # Violation details (if not compliant)
    violation: Optional[PolicyViolation] = None
    
    # Additional context
    resource_tags: Dict[str, str] = Field(default_factory=dict)
    evaluation_metadata: Dict[str, Any] = Field(default_factory=dict)


class PolicySummary(BaseModel):
    """Summary of policy evaluation results"""
    total_resources: int
    compliant_resources: int
    non_compliant_resources: int
    
    # Breakdown by severity
    violations_by_severity: Dict[Severity, int] = Field(default_factory=dict)
    
    # Breakdown by cloud provider
    results_by_provider: Dict[CloudProvider, Dict[str, int]] = Field(default_factory=dict)
    
    # Breakdown by policy
    results_by_policy: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    evaluation_time: datetime = Field(default_factory=datetime.utcnow)


class OPAPolicyInput(BaseModel):
    """Input format for OPA policy evaluation"""
    resource_id: str
    resource_type: str
    cloud_provider: str
    region: str
    account_id: str
    configuration: Dict[str, Any]
    tags: Dict[str, str] = Field(default_factory=dict)
    
    # Additional context for policy evaluation
    server_side_encryption_configuration: Optional[List[Dict[str, Any]]] = None
    security_groups: List[str] = Field(default_factory=list)
    iam_policies: List[Dict[str, Any]] = Field(default_factory=list)


class ScanRequest(BaseModel):
    """Request model for resource scanning"""
    cloud_providers: List[CloudProvider] = Field(default_factory=lambda: list(CloudProvider))
    resource_types: List[ResourceType] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    account_ids: List[str] = Field(default_factory=list)
    tag_filters: Dict[str, str] = Field(default_factory=dict)
