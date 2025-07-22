"""
AWS Config Integration for Cloud Resource Scanning
Retrieves AWS resources for compliance policy evaluation
"""

import boto3
import json
import logging
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from .models import CloudResource, ResourceMetadata

logger = logging.getLogger(__name__)


class AWSConfigClient:
    """Client for integrating with AWS Config to retrieve resource inventory"""
    
    def __init__(self, region: str = "us-east-1", profile: Optional[str] = None):
        """
        Initialize AWS Config client
        
        Args:
            region: AWS region to scan
            profile: AWS profile to use (optional)
        """
        self.region = region
        self.profile = profile
        
        try:
            if profile:
                session = boto3.Session(profile_name=profile)
                self.config_client = session.client('config', region_name=region)
                self.s3_client = session.client('s3', region_name=region)
            else:
                self.config_client = boto3.client('config', region_name=region)
                self.s3_client = boto3.client('s3', region_name=region)
                
        except NoCredentialsError:
            logger.error("AWS credentials not configured")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise

    async def get_s3_buckets(self) -> List[CloudResource]:
        """
        Retrieve all S3 buckets with their configuration
        
        Returns:
            List of CloudResource objects representing S3 buckets
        """
        try:
            resources = []
            
            # Get S3 buckets from Config
            response = self.config_client.list_aggregate_discovered_resources(
                ConfigurationAggregatorName='default',  # Will need to be configurable
                ResourceType='AWS::S3::Bucket'
            )
            
            # If no aggregator, fall back to direct S3 API
            if not response.get('ResourceIdentifiers'):
                return await self._get_s3_buckets_direct()
            
            for resource_id in response['ResourceIdentifiers']:
                bucket_name = resource_id['ResourceName']
                bucket_config = await self._get_bucket_configuration(bucket_name)
                
                if bucket_config:
                    cloud_resource = CloudResource(
                        resource_id=bucket_name,
                        resource_type="aws_s3_bucket",
                        cloud_provider="aws",
                        region=self.region,
                        metadata=ResourceMetadata(
                            account_id=resource_id.get('SourceAccountId'),
                            tags=bucket_config.get('tags', {}),
                            created_date=bucket_config.get('creation_date'),
                            compliance_status="unknown"
                        ),
                        configuration=bucket_config
                    )
                    resources.append(cloud_resource)
                    
            logger.info(f"Retrieved {len(resources)} S3 buckets from AWS Config")
            return resources
            
        except ClientError as e:
            logger.error(f"AWS Config error: {str(e)}")
            # Fallback to direct S3 API
            return await self._get_s3_buckets_direct()
        except Exception as e:
            logger.error(f"Error retrieving S3 buckets: {str(e)}")
            return []

    async def _get_s3_buckets_direct(self) -> List[CloudResource]:
        """Fallback method to get S3 buckets directly from S3 API"""
        try:
            response = self.s3_client.list_buckets()
            resources = []
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                bucket_config = await self._get_bucket_configuration(bucket_name)
                
                if bucket_config:
                    cloud_resource = CloudResource(
                        resource_id=bucket_name,
                        resource_type="aws_s3_bucket",
                        cloud_provider="aws",
                        region=self.region,
                        metadata=ResourceMetadata(
                            account_id="unknown",
                            tags=bucket_config.get('tags', {}),
                            created_date=bucket.get('CreationDate'),
                            compliance_status="unknown"
                        ),
                        configuration=bucket_config
                    )
                    resources.append(cloud_resource)
                    
            logger.info(f"Retrieved {len(resources)} S3 buckets from S3 API")
            return resources
            
        except Exception as e:
            logger.error(f"Error retrieving S3 buckets directly: {str(e)}")
            return []

    async def _get_bucket_configuration(self, bucket_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed configuration for an S3 bucket
        
        Args:
            bucket_name: Name of the S3 bucket
            
        Returns:
            Dictionary containing bucket configuration
        """
        try:
            config = {
                "bucket_name": bucket_name,
                "server_side_encryption_configuration": [],
                "tags": {},
                "versioning": {},
                "logging": {},
                "public_access_block": {}
            }
            
            # Get encryption configuration
            try:
                encryption_response = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                config["server_side_encryption_configuration"] = [
                    {"rule": encryption_response.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])}
                ]
            except ClientError as e:
                if e.response['Error']['Code'] != 'ServerSideEncryptionConfigurationNotFoundError':
                    logger.warning(f"Could not get encryption for bucket {bucket_name}: {str(e)}")
            
            # Get bucket tags
            try:
                tags_response = self.s3_client.get_bucket_tagging(Bucket=bucket_name)
                config["tags"] = {tag['Key']: tag['Value'] for tag in tags_response.get('TagSet', [])}
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchTagSet':
                    logger.warning(f"Could not get tags for bucket {bucket_name}: {str(e)}")
            
            # Get versioning configuration
            try:
                versioning_response = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                config["versioning"] = versioning_response
            except ClientError as e:
                logger.warning(f"Could not get versioning for bucket {bucket_name}: {str(e)}")
            
            # Get public access block
            try:
                pab_response = self.s3_client.get_public_access_block(Bucket=bucket_name)
                config["public_access_block"] = pab_response.get('PublicAccessBlockConfiguration', {})
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchPublicAccessBlockConfiguration':
                    logger.warning(f"Could not get public access block for bucket {bucket_name}: {str(e)}")
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting configuration for bucket {bucket_name}: {str(e)}")
            return None

    async def get_all_resources(self) -> List[CloudResource]:
        """
        Get all supported AWS resources
        
        Returns:
            List of all CloudResource objects
        """
        all_resources = []
        
        # Get S3 buckets
        s3_resources = await self.get_s3_buckets()
        all_resources.extend(s3_resources)
        
        # TODO: Add other resource types (EC2, RDS, IAM, etc.)
        # ec2_resources = await self.get_ec2_instances()
        # rds_resources = await self.get_rds_instances()
        # iam_resources = await self.get_iam_roles()
        
        logger.info(f"Retrieved {len(all_resources)} total AWS resources")
        return all_resources
