"""
Cloud Governance Policy Scanner API
FastAPI application for multi-cloud compliance scanning with OPA integration
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import CloudResource, PolicyEvaluation, ComplianceReport
from .opa_client import OPAClient
from .aws_client import AWSConfigClient
from .azure_client import AzureClient
from .gcp_client import GCPClient

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Cloud Governance Policy Scanner",
    description="Multi-cloud compliance scanning with OPA policy engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
opa_client = OPAClient(
    opa_url=os.getenv("OPA_URL", "http://localhost:8181")
)

# Cloud clients will be initialized per request based on credentials
aws_region = os.getenv("AWS_REGION", "us-east-1")
azure_subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
gcp_project_id = os.getenv("GCP_PROJECT_ID")


class ScanRequest(BaseModel):
    """Request model for compliance scanning"""
    cloud_providers: List[str] = ["aws", "azure", "gcp"]
    resource_types: Optional[List[str]] = None
    policies: Optional[List[str]] = None


class ScanStatus(BaseModel):
    """Response model for scan status"""
    scan_id: str
    status: str  # "running", "completed", "failed"
    total_resources: int
    scanned_resources: int
    violations: int
    start_time: str
    end_time: Optional[str] = None


# In-memory storage for scan results (use database in production)
scan_results = {}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check OPA connectivity
        opa_status = await opa_client.health_check()
        return {
            "status": "healthy",
            "opa_connected": opa_status,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/scan", response_model=Dict[str, str])
async def start_compliance_scan(
    scan_request: ScanRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a compliance scan across specified cloud providers
    """
    try:
        scan_id = f"scan_{int(asyncio.get_event_loop().time())}"
        
        # Initialize scan status
        scan_results[scan_id] = ScanStatus(
            scan_id=scan_id,
            status="running",
            total_resources=0,
            scanned_resources=0,
            violations=0,
            start_time=asyncio.get_event_loop().time()
        )
        
        # Start background scan task
        background_tasks.add_task(
            perform_compliance_scan,
            scan_id,
            scan_request
        )
        
        return {
            "scan_id": scan_id,
            "status": "started",
            "message": "Compliance scan started successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to start scan: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start compliance scan")


@app.get("/scan/{scan_id}/status", response_model=ScanStatus)
async def get_scan_status(scan_id: str):
    """Get the status of a compliance scan"""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return scan_results[scan_id]


@app.get("/scan/{scan_id}/results")
async def get_scan_results(scan_id: str):
    """Get the results of a completed compliance scan"""
    if scan_id not in scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    status = scan_results[scan_id]
    if status.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Scan is {status.status}, results not available"
        )
    
    # Return detailed results (stored separately in production)
    return {
        "scan_id": scan_id,
        "status": status,
        "detailed_results": scan_results.get(f"{scan_id}_details", [])
    }


@app.post("/evaluate", response_model=List[PolicyEvaluation])
async def evaluate_resources(
    resources: List[CloudResource],
    policies: Optional[List[str]] = None
):
    """
    Evaluate a list of resources against specified policies
    """
    try:
        if not resources:
            raise HTTPException(status_code=400, detail="No resources provided")
        
        evaluations = []
        
        for resource in resources:
            # Get applicable policies for resource type
            applicable_policies = await opa_client.get_policies_for_resource_type(
                resource.resource_type
            )
            
            if policies:
                # Filter to requested policies
                applicable_policies = [p for p in applicable_policies if p in policies]
            
            # Evaluate each policy
            for policy in applicable_policies:
                evaluation = await opa_client.evaluate_policy(
                    policy_name=policy,
                    resource_data=resource.dict()
                )
                
                if evaluation:
                    evaluations.append(evaluation)
        
        logger.info(f"Evaluated {len(resources)} resources against {len(set(p.policy_name for p in evaluations))} policies")
        return evaluations
        
    except Exception as e:
        logger.error(f"Policy evaluation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Policy evaluation failed")


async def perform_compliance_scan(scan_id: str, scan_request: ScanRequest):
    """
    Background task to perform compliance scanning
    """
    try:
        all_resources = []
        
        # Collect resources from requested cloud providers
        if "aws" in scan_request.cloud_providers:
            aws_client = AWSConfigClient(region=aws_region)
            aws_resources = await aws_client.get_all_resources()
            all_resources.extend(aws_resources)
            logger.info(f"Collected {len(aws_resources)} AWS resources")
        
        if "azure" in scan_request.cloud_providers and azure_subscription_id:
            azure_client = AzureClient(subscription_id=azure_subscription_id)
            azure_resources = await azure_client.get_all_resources()
            all_resources.extend(azure_resources)
            logger.info(f"Collected {len(azure_resources)} Azure resources")
        
        if "gcp" in scan_request.cloud_providers and gcp_project_id:
            gcp_client = GCPClient(project_id=gcp_project_id)
            gcp_resources = await gcp_client.get_all_resources()
            all_resources.extend(gcp_resources)
            logger.info(f"Collected {len(gcp_resources)} GCP resources")
        
        # Filter by resource types if specified
        if scan_request.resource_types:
            all_resources = [
                r for r in all_resources 
                if r.resource_type in scan_request.resource_types
            ]
        
        # Update scan status
        scan_results[scan_id].total_resources = len(all_resources)
        
        # Evaluate policies
        evaluations = await evaluate_resources(all_resources, scan_request.policies)
        violations = [e for e in evaluations if not e.compliant]
        
        # Update final status
        scan_results[scan_id].status = "completed"
        scan_results[scan_id].scanned_resources = len(all_resources)
        scan_results[scan_id].violations = len(violations)
        scan_results[scan_id].end_time = asyncio.get_event_loop().time()
        
        # Store detailed results
        scan_results[f"{scan_id}_details"] = [e.dict() for e in evaluations]
        
        logger.info(f"Scan {scan_id} completed: {len(all_resources)} resources, {len(violations)} violations")
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {str(e)}")
        scan_results[scan_id].status = "failed"
        scan_results[scan_id].end_time = asyncio.get_event_loop().time()


@app.get("/policies")
async def list_policies():
    """List all available policies in OPA"""
    try:
        policies = await opa_client.list_policies()
        return {"policies": policies}
    except Exception as e:
        logger.error(f"Failed to list policies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve policies")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Cloud Governance Policy Scanner",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "scan": "/scan",
            "evaluate": "/evaluate",
            "policies": "/policies"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
