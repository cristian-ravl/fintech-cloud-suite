"""
OPA (Open Policy Agent) Client
Handles communication with OPA server for policy evaluation
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
    """Client for interacting with Open Policy Agent server"""
    
    def __init__(self, opa_url: str = "http://localhost:8181"):
        self.opa_url = opa_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def health_check(self) -> bool:
        """Check if OPA server is healthy"""
        try:
            response = await self.client.get(f"{self.opa_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error("OPA health check failed", error=str(e))
            return False
    
    async def load_policies(self, policies: Dict[str, str]) -> bool:
        """Load policies into OPA server"""
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
        Evaluate resource against OPA policies
        
        Args:
            resource: The cloud resource to evaluate
            policy_ids: Specific policies to evaluate (if None, evaluates all)
            
        Returns:
            List of policy evaluation results
        """
        try:
            # Convert resource to OPA input format
            opa_input = self._resource_to_opa_input(resource)
            
            # If no specific policies requested, evaluate all known policies
            if not policy_ids:
                policy_ids = await self._get_available_policies()
            
            results = []
            
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
