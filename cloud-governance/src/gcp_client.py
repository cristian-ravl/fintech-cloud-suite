"""
Google Cloud Platform Asset Inventory Integration
Connects to GCP Asset Inventory for resource scanning and compliance
"""

import logging
import json
from typing import List, Dict, Any, Optional
from google.cloud import asset_v1
from google.cloud import storage
from google.oauth2 import service_account
from .models import CloudResource, ResourceMetadata

logger = logging.getLogger(__name__)


class GCPClient:
    """Client for integrating with GCP Asset Inventory and resource APIs"""
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """
        Initialize GCP clients
        
        Args:
            project_id: GCP project ID to scan
            credentials_path: Path to service account credentials file (optional)
        """
        self.project_id = project_id
        self.parent = f"projects/{project_id}"
        
        try:
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.asset_client = asset_v1.AssetServiceClient(credentials=credentials)
                self.storage_client = storage.Client(
                    project=project_id, 
                    credentials=credentials
                )
            else:
                # Use default credentials (ADC)
                self.asset_client = asset_v1.AssetServiceClient()
                self.storage_client = storage.Client(project=project_id)
                
        except Exception as e:
            logger.error(f"Failed to initialize GCP clients: {str(e)}")
            raise

    async def get_storage_buckets(self) -> List[CloudResource]:
        """
        Retrieve all GCS buckets with their configuration
        
        Returns:
            List of CloudResource objects representing GCS buckets
        """
        try:
            resources = []
            
            # Use Asset Inventory to get bucket resources
            request = asset_v1.ListAssetsRequest(
                parent=self.parent,
                asset_types=["storage.googleapis.com/Bucket"],
                content_type=asset_v1.ContentType.RESOURCE,
            )
            
            assets = self.asset_client.list_assets(request=request)
            
            for asset in assets:
                bucket_name = asset.resource.data.get('name', '')
                bucket_config = await self._get_bucket_configuration(bucket_name)
                
                cloud_resource = CloudResource(
                    resource_id=asset.name,
                    resource_type="gcp_storage_bucket",
                    cloud_provider="gcp",
                    region=asset.resource.location,
                    metadata=ResourceMetadata(
                        account_id=self.project_id,
                        tags=self._convert_gcp_labels(asset.resource.data.get('labels', {})),
                        compliance_status="unknown"
                    ),
                    configuration=bucket_config
                )
                resources.append(cloud_resource)
                
            logger.info(f"Retrieved {len(resources)} GCS buckets from Asset Inventory")
            return resources
            
        except Exception as e:
            logger.error(f"Error retrieving GCS buckets: {str(e)}")
            # Fallback to direct Storage API
            return await self._get_buckets_direct()

    async def _get_buckets_direct(self) -> List[CloudResource]:
        """Fallback method to get GCS buckets directly from Storage API"""
        try:
            resources = []
            
            for bucket in self.storage_client.list_buckets():
                bucket_config = await self._get_bucket_configuration(bucket.name)
                
                cloud_resource = CloudResource(
                    resource_id=f"projects/{self.project_id}/buckets/{bucket.name}",
                    resource_type="gcp_storage_bucket",
                    cloud_provider="gcp",
                    region=bucket.location,
                    metadata=ResourceMetadata(
                        account_id=self.project_id,
                        tags=self._convert_gcp_labels(bucket.labels or {}),
                        created_date=bucket.time_created,
                        compliance_status="unknown"
                    ),
                    configuration=bucket_config
                )
                resources.append(cloud_resource)
                
            logger.info(f"Retrieved {len(resources)} GCS buckets from Storage API")
            return resources
            
        except Exception as e:
            logger.error(f"Error retrieving GCS buckets directly: {str(e)}")
            return []

    async def _get_bucket_configuration(self, bucket_name: str) -> Dict[str, Any]:
        """
        Get detailed configuration for a GCS bucket
        
        Args:
            bucket_name: Name of the GCS bucket
            
        Returns:
            Dictionary containing bucket configuration
        """
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.reload()
            
            config = {
                "name": bucket.name,
                "location": bucket.location,
                "location_type": bucket.location_type,
                "storage_class": bucket.storage_class,
                "encryption": {
                    "default_kms_key_name": bucket.default_kms_key_name,
                    "encryption_configuration": {}
                },
                "versioning": {
                    "enabled": bucket.versioning_enabled
                },
                "lifecycle": {
                    "rules": [rule._properties for rule in bucket.lifecycle_rules] if bucket.lifecycle_rules else []
                },
                "logging": {
                    "log_bucket": bucket.log_bucket,
                    "log_object_prefix": bucket.log_object_prefix
                },
                "cors": [cors._properties for cors in bucket.cors] if bucket.cors else [],
                "iam_configuration": {
                    "uniform_bucket_level_access": {
                        "enabled": bucket.iam_configuration.uniform_bucket_level_access_enabled,
                        "locked_time": bucket.iam_configuration.uniform_bucket_level_access_locked_time
                    } if bucket.iam_configuration else {}
                },
                "public_access_prevention": bucket.public_access_prevention,
                "labels": bucket.labels or {},
                "requester_pays": bucket.requester_pays,
                "retention_policy": {
                    "retention_period": bucket.retention_period,
                    "effective_time": bucket.retention_policy_effective_time,
                    "is_locked": bucket.retention_policy_locked
                } if bucket.retention_period else {}
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting configuration for bucket {bucket_name}: {str(e)}")
            return {
                "name": bucket_name,
                "error": str(e)
            }

    async def get_compute_instances(self) -> List[CloudResource]:
        """
        Retrieve all Compute Engine instances
        
        Returns:
            List of CloudResource objects representing compute instances
        """
        try:
            resources = []
            
            # Use Asset Inventory to get compute instances
            request = asset_v1.ListAssetsRequest(
                parent=self.parent,
                asset_types=["compute.googleapis.com/Instance"],
                content_type=asset_v1.ContentType.RESOURCE,
            )
            
            assets = self.asset_client.list_assets(request=request)
            
            for asset in assets:
                cloud_resource = CloudResource(
                    resource_id=asset.name,
                    resource_type="gcp_compute_instance",
                    cloud_provider="gcp",
                    region=asset.resource.location,
                    metadata=ResourceMetadata(
                        account_id=self.project_id,
                        tags=self._convert_gcp_labels(asset.resource.data.get('labels', {})),
                        compliance_status="unknown"
                    ),
                    configuration={
                        "name": asset.resource.data.get('name', ''),
                        "machine_type": asset.resource.data.get('machineType', ''),
                        "status": asset.resource.data.get('status', ''),
                        "zone": asset.resource.data.get('zone', ''),
                        "network_interfaces": asset.resource.data.get('networkInterfaces', []),
                        "disks": asset.resource.data.get('disks', []),
                        "metadata": asset.resource.data.get('metadata', {}),
                        "labels": asset.resource.data.get('labels', {}),
                        "service_accounts": asset.resource.data.get('serviceAccounts', [])
                    }
                )
                resources.append(cloud_resource)
                
            logger.info(f"Retrieved {len(resources)} GCP Compute instances")
            return resources
            
        except Exception as e:
            logger.error(f"Error retrieving GCP compute instances: {str(e)}")
            return []

    def _convert_gcp_labels(self, labels: Dict[str, str]) -> Dict[str, str]:
        """Convert GCP labels to standard tag format"""
        return labels or {}

    async def get_all_resources(self) -> List[CloudResource]:
        """
        Get all supported GCP resources
        
        Returns:
            List of all CloudResource objects
        """
        all_resources = []
        
        # Get storage buckets
        storage_resources = await self.get_storage_buckets()
        all_resources.extend(storage_resources)
        
        # Get compute instances
        compute_resources = await self.get_compute_instances()
        all_resources.extend(compute_resources)
        
        # TODO: Add other resource types (SQL instances, Cloud Functions, etc.)
        
        logger.info(f"Retrieved {len(all_resources)} total GCP resources")
        return all_resources
