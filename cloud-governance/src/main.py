"""
Cloud Governance & Compliance Platform
Policy Engine with multi-cloud resource scanning and OPA integration
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any

import structlog
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .cloud_scanners import AWSScanner, AzureScanner, GCPScanner
from .opa_client import OPAClient
from .models import PolicyResult, ResourceInventory


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class PolicyEvaluationRequest(BaseModel):
    """Request model for policy evaluation"""
    cloud_providers: List[str] = ["aws", "azure", "gcp"]
    policy_ids: List[str] = []
    resource_types: List[str] = []


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    opa_connection: bool
    cloud_connections: Dict[str, bool]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Cloud Governance Policy Engine")
    
    # Initialize OPA client
    opa_url = os.getenv("OPA_URL", "http://localhost:8181")
    app.state.opa_client = OPAClient(opa_url)
    
    # Initialize cloud scanners
    app.state.aws_scanner = AWSScanner()
    app.state.azure_scanner = AzureScanner()
    app.state.gcp_scanner = GCPScanner()
    
    # Test connections
    try:
        await app.state.opa_client.health_check()
        logger.info("OPA connection established")
    except Exception as e:
        logger.error("Failed to connect to OPA", error=str(e))
    
    yield
    
    logger.info("Shutting down Cloud Governance Policy Engine")


# Initialize FastAPI app
app = FastAPI(
    title="Cloud Governance & Compliance Platform",
    description="Multi-cloud policy engine with OPA integration",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        opa_healthy = await app.state.opa_client.health_check()
        
        # Test cloud scanner connections
        cloud_connections = {
            "aws": await app.state.aws_scanner.test_connection(),
            "azure": await app.state.azure_scanner.test_connection(),
            "gcp": await app.state.gcp_scanner.test_connection(),
        }
        
        return HealthResponse(
            status="healthy",
            opa_connection=opa_healthy,
            cloud_connections=cloud_connections
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/evaluate", response_model=List[PolicyResult])
async def evaluate_policies(request: PolicyEvaluationRequest):
    """
    Evaluate compliance policies across cloud resources
    
    This endpoint:
    1. Scans resources from specified cloud providers
    2. Normalizes resource data into common schema
    3. Evaluates resources against OPA policies
    4. Returns policy results with remediation guidance
    """
    try:
        logger.info("Starting policy evaluation", 
                   cloud_providers=request.cloud_providers,
                   policy_ids=request.policy_ids)
        
        # Collect resources from all cloud providers
        all_resources = []
        
        for provider in request.cloud_providers:
            if provider == "aws":
                resources = await app.state.aws_scanner.scan_resources(request.resource_types)
                all_resources.extend(resources)
            elif provider == "azure":
                resources = await app.state.azure_scanner.scan_resources(request.resource_types)
                all_resources.extend(resources)
            elif provider == "gcp":
                resources = await app.state.gcp_scanner.scan_resources(request.resource_types)
                all_resources.extend(resources)
        
        logger.info("Collected resources", count=len(all_resources))
        
        # Evaluate policies with OPA
        policy_results = []
        for resource in all_resources:
            results = await app.state.opa_client.evaluate_policies(
                resource, 
                policy_ids=request.policy_ids
            )
            policy_results.extend(results)
        
        logger.info("Policy evaluation completed", 
                   total_results=len(policy_results),
                   violations=len([r for r in policy_results if not r.compliant]))
        
        return policy_results
        
    except Exception as e:
        logger.error("Policy evaluation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.get("/resources", response_model=List[ResourceInventory])
async def get_resource_inventory(
    cloud_provider: str = None,
    resource_type: str = None
):
    """Get cloud resource inventory"""
    try:
        providers = [cloud_provider] if cloud_provider else ["aws", "azure", "gcp"]
        resource_types = [resource_type] if resource_type else []
        
        all_resources = []
        
        for provider in providers:
            if provider == "aws":
                resources = await app.state.aws_scanner.scan_resources(resource_types)
                all_resources.extend(resources)
            elif provider == "azure":
                resources = await app.state.azure_scanner.scan_resources(resource_types)
                all_resources.extend(resources)
            elif provider == "gcp":
                resources = await app.state.gcp_scanner.scan_resources(resource_types)
                all_resources.extend(resources)
        
        return all_resources
        
    except Exception as e:
        logger.error("Resource inventory failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Inventory failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    port = int(os.getenv("PORT", "8080"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        reload=False
    )
