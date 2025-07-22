"""
Data Models for Cloud Governance Platform

This module defines the core data structures used throughout the cloud governance
platform for policy evaluation, compliance reporting, and resource management.
All models are built using Pydantic for data validation, serialization, and
automatic API documentation.

Key Model Categories:
1. Enumerations: Standardized values for providers, resources, and compliance
2. Resource Models: Structures for cloud resource representation
3. Policy Models: Data structures for policy evaluation and results
4. Request/Response Models: API endpoint data contracts
5. Configuration Models: Settings and preferences

Design Principles:
- Type safety with Python type hints and Pydantic validation
- Immutable data structures for consistency
- Clear separation of concerns between different model types
- Comprehensive field documentation for API generation
- Extensible design for adding new cloud providers and resource types

Usage Example:
    ```python
    from models import CloudResource, PolicyResult, Severity
    
    # Create a cloud resource
    resource = CloudResource(
        resource_id="s3-bucket-example",
        resource_type=ResourceType.S3_BUCKET,
        provider=CloudProvider.AWS,
        region="us-east-1",
        metadata={"encryption": True}
    )
    
    # Create policy result
    result = PolicyResult(
        policy_name="aws_s3_encryption",
        resource_id=resource.resource_id,
        compliant=True,
        severity=Severity.HIGH
    )
    ```

Dependencies:
- pydantic: Data validation and serialization
- datetime: Timestamp handling for audit trails
- enum: Type-safe enumeration definitions
- typing: Generic type annotations for collections
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class CloudProvider(str, Enum):
    """
    Enumeration of supported cloud service providers
    
    This enum defines the cloud platforms supported by the governance
    platform. Each value corresponds to a specific cloud provider
    implementation with dedicated client libraries and resource mappings.
    
    Values:
        AWS: Amazon Web Services - world's largest cloud platform
        AZURE: Microsoft Azure - enterprise-focused cloud platform
        GCP: Google Cloud Platform - Google's cloud infrastructure
        
    Usage:
        Use these values to specify which cloud provider a resource
        belongs to or which provider should be scanned during compliance
        evaluations.
        
    Extension:
        Add new providers by extending this enum and implementing
        corresponding client classes in the cloud client modules.
    """
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class ResourceType(str, Enum):
    """
    Enumeration of cloud resource types across providers
    
    This enum standardizes resource type identification across different
    cloud providers. Each value uses a provider-specific prefix to avoid
    naming conflicts and ensure clear resource identification.
    
    AWS Resources:
        S3_BUCKET: Simple Storage Service buckets for object storage
        EC2_INSTANCE: Elastic Compute Cloud virtual machines
        RDS_INSTANCE: Relational Database Service managed databases
        IAM_ROLE: Identity and Access Management roles for permissions
        
    Azure Resources:
        STORAGE_ACCOUNT: Azure Storage accounts for various storage types
        VIRTUAL_MACHINE: Azure Virtual Machines for compute workloads
        SQL_SERVER: Azure SQL Database managed database service
        
    GCP Resources:
        GCS_BUCKET: Google Cloud Storage buckets for object storage
        COMPUTE_INSTANCE: Google Compute Engine virtual machines
        CLOUD_SQL: Google Cloud SQL managed database service
        
    Design Notes:
        - Use provider prefixes (aws_, azure_, gcp_) for clarity
        - Map to actual cloud provider resource types in client code
        - Extensible for adding new resource types as needed
        - Consistent naming patterns across providers where possible
    """
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
    """
    Enumeration of supported compliance and regulatory frameworks
    
    This enum defines the compliance standards and regulatory frameworks
    that the governance platform can evaluate against. Each framework
    represents a specific set of security and operational requirements.
    
    Frameworks:
        SOC2: Service Organization Control 2 - trust services criteria
        PCI_DSS: Payment Card Industry Data Security Standard
        GDPR: General Data Protection Regulation (EU privacy law)
        HIPAA: Health Insurance Portability and Accountability Act
        ISO27001: International standard for information security management
        
    Usage in Policies:
        Policies can be tagged with applicable frameworks to enable
        framework-specific compliance reporting and audit trails.
        
    Reporting:
        Scan results can be filtered and grouped by compliance framework
        to generate targeted reports for auditors and compliance teams.
        
    Extension:
        Add new frameworks by extending this enum and updating policy
        metadata to include framework mappings.
    """
    SOC2 = "SOC2"
    PCI_DSS = "PCI-DSS"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    ISO27001 = "ISO27001"


class Severity(str, Enum):
    """
    Enumeration of policy violation severity levels
    
    This enum defines the severity classification system for policy
    violations, enabling risk-based prioritization of remediation efforts.
    Severity levels are ordered from most critical to least critical.
    
    Levels (highest to lowest priority):
        CRITICAL: Immediate security or compliance risk requiring urgent action
        HIGH: Significant risk that should be addressed within 24-48 hours
        MEDIUM: Moderate risk that should be addressed within a week
        LOW: Minor risk or best practice violation for eventual remediation
        INFO: Informational findings that don't require immediate action
        
    Risk Assessment:
        - CRITICAL: Public data exposure, unencrypted sensitive data
        - HIGH: Missing access controls, weak encryption
        - MEDIUM: Outdated configurations, missing monitoring
        - LOW: Documentation gaps, non-standard naming
        - INFO: Optimization opportunities, usage statistics
        
    Remediation SLAs:
        Organizations typically establish different SLA requirements
        based on severity levels for tracking and compliance purposes.
        
    Automation:
        Higher severity violations may trigger automated alerts,
        while lower severity findings might only appear in reports.
    """
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
    """Request model for resource scanning with API versioning support.
    
    This model defines the structure for requesting cloud resource scans
    across multiple providers. Includes API versioning for future compatibility
    and comprehensive filtering options.
    
    Attributes:
        cloud_providers: List of cloud providers to scan (defaults to all)
        resource_types: Specific resource types to include in scan
        regions: Geographic regions to limit scanning scope
        account_ids: Specific cloud account identifiers to scan
        tag_filters: Key-value pairs for resource tag-based filtering
        api_version: API version for request compatibility and evolution
    """
    cloud_providers: List[CloudProvider] = Field(
        default_factory=lambda: list(CloudProvider),
        description="Cloud providers to scan for resources"
    )
    resource_types: List[ResourceType] = Field(
        default_factory=list,
        description="Specific resource types to include (empty = all types)"
    )
    regions: List[str] = Field(
        default_factory=list,
        description="Geographic regions to scan (empty = all regions)"
    )
    account_ids: List[str] = Field(
        default_factory=list,
        description="Cloud account IDs to scan (empty = all accessible accounts)"
    )
    tag_filters: Dict[str, str] = Field(
        default_factory=dict,
        description="Resource tag filters as key-value pairs"
    )
    api_version: str = Field(
        default="v1",
        description="API version for request compatibility and schema evolution"
    )
    
    class Config:
        """Pydantic configuration with comprehensive example"""
        schema_extra = {
            "example": {
                "cloud_providers": ["aws", "azure"],
                "resource_types": ["aws_s3_bucket", "azure_storage_account"],
                "regions": ["us-east-1", "eastus"],
                "account_ids": ["123456789012"],
                "tag_filters": {"Environment": "production", "Team": "security"},
                "api_version": "v1"
            }
        }
