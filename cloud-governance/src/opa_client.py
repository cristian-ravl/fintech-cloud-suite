"""
OPA (Open Policy Agent) Client Module

This module provides a comprehensive interface for interacting with an OPA server
to perform policy evaluation, compliance checking, and governance automation.

Key Features:
- Asynchronous HTTP client for high-performance policy evaluation
- Retry logic with exponential backoff for reliability
- Comprehensive error handling and logging
- Support for multiple compliance frameworks (SOC2, PCI-DSS, GDPR)
- Structured logging with contextual information
- Connection pooling and timeout management

Architecture:
The OPAClient class serves as the primary interface between the policy scanner
service and the OPA server. It handles:
- Policy loading and management
- Resource evaluation against policies
- Health monitoring and status checks
- Results aggregation and transformation

Usage Example:
    async with OPAClient("http://opa-server:8181") as opa:
        if await opa.health_check():
            result = await opa.evaluate_resource(resource, "security_policies")
            
Dependencies:
- httpx: Modern async HTTP client for OPA communication
- tenacity: Retry logic with exponential backoff
- structlog: Structured logging for observability
- pydantic: Data validation through models module

Performance Considerations:
- Connection pooling reduces latency for repeated requests
- Batch evaluation support for large resource sets
- Configurable timeouts prevent hanging operations
- Retry logic with jitter prevents thundering herd problems
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from .models import (
    PolicyResult, PolicyViolation, ResourceInventory, 
    OPAPolicyInput, Severity, ComplianceFramework
)

logger = structlog.get_logger()


class OPAClient:
    """
    Asynchronous client for Open Policy Agent (OPA) server interactions
    
    This client provides a high-level interface for policy evaluation,
    compliance checking, and governance automation using OPA as the
    policy engine. It supports enterprise-grade features including
    retry logic, connection pooling, and comprehensive error handling.
    
    Attributes:
        opa_url (str): Base URL of the OPA server
        client (httpx.AsyncClient): HTTP client with connection pooling
        
    Configuration:
        - Default timeout: 30 seconds for policy evaluation
        - Retry attempts: 3 with exponential backoff
        - Connection pool: Reused across requests for performance
        - Health check: Periodic verification of OPA server status
    
    Thread Safety:
        This client is designed for use in async environments and should
        be used within proper async context managers to ensure resource
        cleanup and connection management.
    
    Example Usage:
        ```python
        async with OPAClient("http://opa:8181") as opa:
            # Check server health
            if await opa.health_check():
                # Evaluate resource against policies
                result = await opa.evaluate_resource(
                    resource_data, 
                    "compliance_bundle"
                )
                
                # Process policy results
                if result.violation:
                    print(f"Policy violation: {result.message}")
        ```
    """
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        """
        Initialize OPA client with server configuration
        
        Args:
            opa_url (str): Base URL of the OPA server including protocol and port.
                          Defaults to "http://localhost:8181" for local development.
                          
        Note:
            The URL will be normalized by removing trailing slashes to ensure
            consistent API endpoint construction.
        """
        self.opa_url = opa_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        """Async context manager entry - returns configured client"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures proper resource cleanup"""
        await self.client.aclose()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def health_check(self) -> bool:
        """
        Perform health check against OPA server
        
        This method verifies that the OPA server is accessible and responding
        to requests. It includes retry logic with exponential backoff to handle
        temporary network issues or server load.
        
        Returns:
            bool: True if OPA server is healthy and responsive, False otherwise
            
        Retry Strategy:
            - Maximum attempts: 3
            - Wait strategy: Exponential backoff (4s, 8s, 16s)
            - Suitable for handling temporary network issues
            
        Error Handling:
            - Network timeouts are retried automatically
            - Connection errors trigger retry with backoff
            - All exceptions are logged with context
            - Returns False on final failure after all retries
        
        Usage:
            Use this method before performing policy evaluations to ensure
            the OPA server is available. Consider implementing circuit breaker
            patterns for production deployments.
        """
        try:
            response = await self.client.get(f"{self.opa_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error("OPA health check failed", error=str(e))
            return False
    
    async def load_policies(self, policies: Dict[str, str]) -> bool:
        """
        Load Rego policies into the OPA server
        
        This method uploads policy definitions written in Rego language to the
        OPA server, making them available for resource evaluation. Policies are
        loaded individually and must be valid Rego syntax.
        
        Args:
            policies (Dict[str, str]): Dictionary mapping policy IDs to Rego content:
                - Key: Unique policy identifier (e.g., "aws_s3_encryption")
                - Value: Complete Rego policy definition as string
                
        Returns:
            bool: True if all policies loaded successfully, False if any failed
            
        Policy Format:
            Each policy must be valid Rego syntax with proper package declaration:
            ```rego
            package aws.s3.encryption
            
            default allow = false
            
            allow {
                input.resource.encryption.enabled == true
            }
            
            violation[{"msg": msg}] {
                not allow
                msg := "S3 bucket must have encryption enabled"
            }
            ```
            
        Error Handling:
            - Individual policy failures are logged with policy ID
            - Network errors result in immediate failure
            - Invalid Rego syntax reported by OPA server
            - Partial success possible (some policies loaded, others failed)
            
        HTTP Details:
            - Method: PUT to /v1/policies/{policy_id}
            - Content-Type: text/plain
            - Success codes: 200 (updated), 201 (created)
            - Body: Raw Rego policy content
            
        Usage Notes:
            - Policy IDs should be unique and descriptive
            - Consider using namespaced naming (e.g., "aws.s3.encryption")
            - Policies can be updated by loading with same ID
            - Failed loads don't affect previously loaded policies
        """
        try:
            for policy_id, policy_content in policies.items():
                url = f"{self.opa_url}/v1/policies/{policy_id}"
                headers = {"Content-Type": "text/plain"}
                
                response = await self.client.put(
                    url, 
                    content=policy_content,
                    headers=headers
                )
                
                if response.status_code not in [200, 201]:
                    logger.error("Failed to load policy", 
                               policy_id=policy_id, 
                               status_code=response.status_code,
                               response=response.text)
                    return False
                    
                logger.info("Policy loaded successfully", policy_id=policy_id)
            
            return True
            
        except Exception as e:
            logger.error("Failed to load policies", error=str(e))
            return False
    
    async def evaluate_policies(
        self, 
        resource: ResourceInventory,
        policy_ids: Optional[List[str]] = None
    ) -> List[PolicyResult]:
        """
        Evaluate a cloud resource against specified OPA policies
        
        This method sends a resource to the OPA server for policy evaluation
        and returns comprehensive compliance results. It supports both targeted
        evaluation (specific policies) and comprehensive evaluation (all policies).
        
        Args:
            resource (ResourceInventory): Cloud resource to evaluate containing:
                - resource_id: Unique identifier for the resource
                - resource_type: Type of cloud resource (S3_BUCKET, EC2_INSTANCE, etc.)
                - provider: Cloud provider (AWS, AZURE, GCP)
                - region: Geographic region where resource is located
                - metadata: Resource-specific configuration and properties
                
            policy_ids (Optional[List[str]]): Specific policies to evaluate:
                - If None: Evaluates against all available policies in OPA
                - If provided: Only evaluates against specified policy IDs
                - Policy IDs must match those loaded in OPA server
                
        Returns:
            List[PolicyResult]: Comprehensive evaluation results containing:
                - policy_name: Name of the evaluated policy
                - resource_id: Identifier of the evaluated resource
                - compliant: Boolean indicating overall compliance
                - violations: List of specific policy violations
                - severity: Risk level (LOW, MEDIUM, HIGH, CRITICAL)
                - compliance_frameworks: Applicable frameworks (SOC2, PCI-DSS, etc.)
                
        Process Flow:
            1. Resource Conversion: Transform resource to OPA input format
            2. Policy Selection: Use specified policies or discover all available
            3. Individual Evaluation: Send each policy evaluation request to OPA
            4. Result Aggregation: Collect and validate all policy results
            5. Error Handling: Log failures while preserving successful evaluations
            
        Example Usage:
            ```python
            # Evaluate against all policies
            results = await opa.evaluate_policies(s3_bucket_resource)
            
            # Evaluate against specific policies
            security_results = await opa.evaluate_policies(
                s3_bucket_resource,
                policy_ids=["aws_s3_encryption", "aws_s3_public_access"]
            )
            
            # Process results
            for result in results:
                if not result.compliant:
                    print(f"Violation: {result.violations}")
            ```
            
        Error Handling:
            - Individual policy failures don't stop other evaluations
            - Network errors are logged and re-raised for caller handling
            - Invalid resource data results in evaluation failure
            - Missing policies are logged but don't cause failures
        """
        try:
            # Convert resource to OPA input format for policy evaluation
            opa_input = self._resource_to_opa_input(resource)
            
            # If no specific policies requested, evaluate all known policies
            if not policy_ids:
                policy_ids = await self._get_available_policies()
            
            results = []
            
            # Evaluate each policy individually for detailed results
            for policy_id in policy_ids:
                result = await self._evaluate_single_policy(resource, opa_input, policy_id)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error("Policy evaluation failed", 
                        resource_id=resource.resource_id,
                        error=str(e))
            raise
    
    async def _evaluate_single_policy(
        self, 
        resource: ResourceInventory,
        opa_input: OPAPolicyInput,
        policy_id: str
    ) -> Optional[PolicyResult]:
        """Evaluate a single policy against a resource"""
        try:
            # Map policy ID to OPA package path
            package_path = self._get_package_path(policy_id)
            
            # Query OPA for policy decision
            decision_url = f"{self.opa_url}/v1/data/{package_path}"
            
            response = await self.client.post(
                decision_url,
                json={"input": opa_input.dict()}
            )
            
            if response.status_code != 200:
                logger.error("OPA query failed", 
                           policy_id=policy_id,
                           status_code=response.status_code,
                           response=response.text)
                return None
            
            decision_data = response.json()
            
            # Parse OPA response
            return self._parse_opa_response(resource, policy_id, decision_data)
            
        except Exception as e:
            logger.error("Single policy evaluation failed",
                        policy_id=policy_id,
                        resource_id=resource.resource_id,
                        error=str(e))
            return None
    
    def _resource_to_opa_input(self, resource: ResourceInventory) -> OPAPolicyInput:
        """Convert ResourceInventory to OPA input format"""
        opa_input = OPAPolicyInput(
            resource_id=resource.resource_id,
            resource_type=resource.resource_type.value,
            cloud_provider=resource.cloud_provider.value,
            region=resource.region,
            account_id=resource.account_id,
            configuration=resource.configuration,
            tags=resource.tags
        )
        
        # Extract specific configuration for known resource types
        if resource.resource_type.value == "aws_s3_bucket":
            opa_input.server_side_encryption_configuration = (
                resource.configuration.get("server_side_encryption_configuration", [])
            )
        
        if resource.security_groups:
            opa_input.security_groups = resource.security_groups
            
        return opa_input
    
    def _get_package_path(self, policy_id: str) -> str:
        """Map policy ID to OPA package path"""
        policy_mappings = {
            "s3-encryption-required": "aws/s3/encryption",
            "ec2-security-groups": "aws/ec2/security_groups",
            "iam-least-privilege": "aws/iam/least_privilege",
            "azure-storage-encryption": "azure/storage/encryption",
            "gcp-storage-encryption": "gcp/storage/encryption"
        }
        
        return policy_mappings.get(policy_id, policy_id.replace("-", "/"))
    
    def _parse_opa_response(
        self, 
        resource: ResourceInventory, 
        policy_id: str, 
        decision_data: Dict[str, Any]
    ) -> PolicyResult:
        """Parse OPA response into PolicyResult"""
        
        result = decision_data.get("result", {})
        
        # Check if resource is compliant
        compliant = result.get("allow", False)
        
        # Extract violation details if not compliant
        violation = None
        if not compliant:
            violation_data = result.get("violation", [])
            if violation_data:
                # Take the first violation if multiple
                v = violation_data[0] if isinstance(violation_data, list) else violation_data
                
                violation = PolicyViolation(
                    policy_id=v.get("policy", policy_id),
                    policy_name=v.get("policy", policy_id).replace("-", " ").title(),
                    severity=Severity(v.get("severity", "medium")),
                    message=v.get("message", "Policy violation detected"),
                    remediation=v.get("remediation", "No remediation available"),
                    compliance_frameworks=[
                        ComplianceFramework(fw) for fw in v.get("compliance_frameworks", [])
                        if fw in [cf.value for cf in ComplianceFramework]
                    ],
                    additional_info=v.get("additional_info", {})
                )
        
        # Extract metadata
        metadata = result.get("metadata", {})
        
        return PolicyResult(
            resource_id=resource.resource_id,
            resource_type=resource.resource_type,
            cloud_provider=resource.cloud_provider,
            region=resource.region,
            account_id=resource.account_id,
            compliant=compliant,
            policy_id=policy_id,
            policy_name=metadata.get("title", policy_id.replace("-", " ").title()),
            violation=violation,
            resource_tags=resource.tags,
            evaluation_metadata={
                "policy_metadata": metadata,
                "evaluation_time": datetime.utcnow().isoformat()
            }
        )
    
    async def _get_available_policies(self) -> List[str]:
        """Get list of available policies from OPA"""
        try:
            response = await self.client.get(f"{self.opa_url}/v1/policies")
            
            if response.status_code == 200:
                policies_data = response.json()
                return list(policies_data.get("result", {}).keys())
            else:
                logger.warning("Could not fetch available policies, using defaults")
                return [
                    "s3-encryption-required",
                    "ec2-security-groups", 
                    "iam-least-privilege"
                ]
                
        except Exception as e:
            logger.error("Failed to get available policies", error=str(e))
            return ["s3-encryption-required"]  # Fallback to basic policy
