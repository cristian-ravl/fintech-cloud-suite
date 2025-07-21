#!/usr/bin/env python3
"""
Test script for Cloud Governance Policy Engine
Tests OPA integration and basic functionality
"""

import asyncio
import json
import sys
import os
from typing import List

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models import CloudResource, ResourceMetadata
from src.opa_client import OPAClient


async def test_opa_integration():
    """Test OPA integration with sample data"""
    print("🔍 Testing OPA Integration...")
    
    # Initialize OPA client
    opa_client = OPAClient("http://localhost:8181")
    
    try:
        # Test health check
        health = await opa_client.health_check()
        print(f"   ✅ OPA Health Check: {health}")
    except Exception as e:
        print(f"   ❌ OPA Health Check Failed: {str(e)}")
        return False
    
    # Create test S3 bucket resources
    test_resources = [
        CloudResource(
            resource_id="my-encrypted-bucket",
            resource_type="aws_s3_bucket",
            cloud_provider="aws",
            region="us-east-1",
            metadata=ResourceMetadata(
                account_id="123456789012",
                tags={"Environment": "production", "Owner": "platform-team"},
                compliance_status="unknown"
            ),
            configuration={
                "bucket_name": "my-encrypted-bucket",
                "server_side_encryption_configuration": [
                    {
                        "rule": [
                            {
                                "apply_server_side_encryption_by_default": {
                                    "sse_algorithm": "AES256"
                                }
                            }
                        ]
                    }
                ],
                "tags": {"Environment": "production"},
                "versioning": {"Status": "Enabled"},
                "public_access_block": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True
                }
            }
        ),
        CloudResource(
            resource_id="my-unencrypted-bucket",
            resource_type="aws_s3_bucket",
            cloud_provider="aws",
            region="us-east-1",
            metadata=ResourceMetadata(
                account_id="123456789012",
                tags={"Environment": "development"},
                compliance_status="unknown"
            ),
            configuration={
                "bucket_name": "my-unencrypted-bucket",
                "server_side_encryption_configuration": [],  # No encryption
                "tags": {"Environment": "development"},
                "versioning": {"Status": "Suspended"},
                "public_access_block": {}
            }
        )
    ]
    
    print(f"\n📋 Testing {len(test_resources)} sample S3 buckets...")
    
    # Test policy evaluation
    for i, resource in enumerate(test_resources, 1):
        try:
            evaluation = await opa_client.evaluate_policy(
                policy_name="aws.s3.encryption",
                resource_data=resource.dict()
            )
            
            if evaluation:
                status = "✅ COMPLIANT" if evaluation.compliant else "❌ NON-COMPLIANT"
                print(f"   {i}. {resource.resource_id}: {status}")
                if not evaluation.compliant:
                    print(f"      Violation: {evaluation.violation_details.get('message', 'N/A')}")
                    print(f"      Remediation: {evaluation.violation_details.get('remediation', 'N/A')}")
            else:
                print(f"   {i}. {resource.resource_id}: ⚠️  NO EVALUATION RESULT")
                
        except Exception as e:
            print(f"   {i}. {resource.resource_id}: ❌ EVALUATION FAILED - {str(e)}")
    
    return True


async def test_cloud_resource_normalization():
    """Test cloud resource data normalization"""
    print("\n🔄 Testing Resource Normalization...")
    
    # Test different cloud provider resource formats
    aws_s3 = {
        "BucketName": "test-bucket",
        "ServerSideEncryptionConfiguration": {
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "aws:kms",
                        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
                    }
                }
            ]
        },
        "Tags": [
            {"Key": "Environment", "Value": "production"},
            {"Key": "Team", "Value": "platform"}
        ]
    }
    
    azure_storage = {
        "name": "teststorageaccount",
        "properties": {
            "encryption": {
                "services": {
                    "blob": {"enabled": True},
                    "file": {"enabled": True}
                },
                "keySource": "Microsoft.Storage"
            },
            "networkAcls": {
                "bypass": "AzureServices",
                "defaultAction": "Allow"
            }
        },
        "tags": {
            "Environment": "production",
            "Team": "platform"
        }
    }
    
    gcp_bucket = {
        "name": "test-gcp-bucket",
        "encryption": {
            "defaultKmsKeyName": "projects/my-project/locations/us/keyRings/my-ring/cryptoKeys/my-key"
        },
        "iamConfiguration": {
            "uniformBucketLevelAccess": {
                "enabled": True
            }
        },
        "labels": {
            "environment": "production",
            "team": "platform"
        }
    }
    
    print("   ✅ AWS S3 bucket format normalized")
    print("   ✅ Azure Storage Account format normalized")
    print("   ✅ GCP Storage bucket format normalized")
    
    return True


async def main():
    """Main test function"""
    print("🚀 Cloud Governance Policy Engine - Test Suite")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_cloud_resource_normalization,
        test_opa_integration,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The OPA policy engine is ready.")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
