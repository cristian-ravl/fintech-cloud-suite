"""
Azure Resource Management Integration
Connects to Azure Resource Graph and Policy services for compliance scanning
"""

import logging
import json
from typing import List, Dict, Any, Optional
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest
from .models import CloudResource, ResourceMetadata

logger = logging.getLogger(__name__)


class AzureClient:
    """Client for integrating with Azure Resource Graph and Policy services"""
    
    def __init__(self, subscription_id: str):
        """
        Initialize Azure clients
        
        Args:
            subscription_id: Azure subscription ID to scan
        """
        self.subscription_id = subscription_id
        
        try:
            self.credential = DefaultAzureCredential()
            self.resource_client = ResourceManagementClient(
                self.credential, 
                subscription_id
            )
            self.resource_graph_client = ResourceGraphClient(self.credential)
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure clients: {str(e)}")
            raise

    async def get_storage_accounts(self) -> List[CloudResource]:
        """
        Retrieve all Azure Storage Accounts with their configuration
        
        Returns:
            List of CloudResource objects representing storage accounts
        """
        try:
            # Query Azure Resource Graph for storage accounts
            query = """
            Resources
            | where type == "microsoft.storage/storageaccounts"
            | project id, name, location, resourceGroup, subscriptionId, 
                      properties, tags, kind
            """
            
            request = QueryRequest(
                subscriptions=[self.subscription_id],
                query=query
            )
            
            response = self.resource_graph_client.resources(request)
            resources = []
            
            for item in response.data:
                # Get detailed storage account configuration
                storage_config = await self._get_storage_account_details(
                    item['resourceGroup'], 
                    item['name']
                )
                
                cloud_resource = CloudResource(
                    resource_id=item['id'],
                    resource_type="azure_storage_account",
                    cloud_provider="azure",
                    region=item['location'],
                    metadata=ResourceMetadata(
                        account_id=item['subscriptionId'],
                        tags=item.get('tags', {}),
                        resource_group=item['resourceGroup'],
                        compliance_status="unknown"
                    ),
                    configuration=storage_config
                )
                resources.append(cloud_resource)
                
            logger.info(f"Retrieved {len(resources)} Azure Storage Accounts")
            return resources
            
        except Exception as e:
            logger.error(f"Error retrieving Azure Storage Accounts: {str(e)}")
            return []

    async def _get_storage_account_details(self, resource_group: str, storage_account_name: str) -> Dict[str, Any]:
        """
        Get detailed configuration for an Azure Storage Account
        
        Args:
            resource_group: Resource group name
            storage_account_name: Storage account name
            
        Returns:
            Dictionary containing storage account configuration
        """
        try:
            # Get storage account properties
            storage_account = self.resource_client.resources.get(
                resource_group_name=resource_group,
                resource_provider_namespace='Microsoft.Storage',
                parent_resource_path='',
                resource_type='storageAccounts',
                resource_name=storage_account_name,
                api_version='2021-04-01'
            )
            
            config = {
                "name": storage_account_name,
                "resource_group": resource_group,
                "kind": storage_account.kind,
                "sku": storage_account.sku.dict() if storage_account.sku else {},
                "encryption": storage_account.properties.get('encryption', {}),
                "network_rule_set": storage_account.properties.get('networkAcls', {}),
                "https_traffic_only": storage_account.properties.get('supportsHttpsTrafficOnly', False),
                "minimum_tls_version": storage_account.properties.get('minimumTlsVersion', 'TLS1_0'),
                "allow_blob_public_access": storage_account.properties.get('allowBlobPublicAccess', True),
                "tags": storage_account.tags or {}
            }
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting storage account details for {storage_account_name}: {str(e)}")
            return {
                "name": storage_account_name,
                "resource_group": resource_group,
                "error": str(e)
            }

    async def get_virtual_machines(self) -> List[CloudResource]:
        """
        Retrieve all Azure Virtual Machines
        
        Returns:
            List of CloudResource objects representing VMs
        """
        try:
            query = """
            Resources
            | where type == "microsoft.compute/virtualmachines"
            | project id, name, location, resourceGroup, subscriptionId, 
                      properties, tags
            """
            
            request = QueryRequest(
                subscriptions=[self.subscription_id],
                query=query
            )
            
            response = self.resource_graph_client.resources(request)
            resources = []
            
            for item in response.data:
                cloud_resource = CloudResource(
                    resource_id=item['id'],
                    resource_type="azure_virtual_machine",
                    cloud_provider="azure",
                    region=item['location'],
                    metadata=ResourceMetadata(
                        account_id=item['subscriptionId'],
                        tags=item.get('tags', {}),
                        resource_group=item['resourceGroup'],
                        compliance_status="unknown"
                    ),
                    configuration={
                        "name": item['name'],
                        "resource_group": item['resourceGroup'],
                        "vm_properties": item.get('properties', {}),
                        "tags": item.get('tags', {})
                    }
                )
                resources.append(cloud_resource)
                
            logger.info(f"Retrieved {len(resources)} Azure Virtual Machines")
            return resources
            
        except Exception as e:
            logger.error(f"Error retrieving Azure VMs: {str(e)}")
            return []

    async def get_policy_compliance(self) -> Dict[str, Any]:
        """
        Get Azure Policy compliance status
        
        Returns:
            Dictionary containing policy compliance information
        """
        try:
            # This would integrate with Azure Policy API
            # For now, return a placeholder
            return {
                "subscription_id": self.subscription_id,
                "compliance_summary": {
                    "compliant_resources": 0,
                    "non_compliant_resources": 0,
                    "total_resources": 0
                },
                "policies": []
            }
            
        except Exception as e:
            logger.error(f"Error retrieving Azure policy compliance: {str(e)}")
            return {}

    async def get_all_resources(self) -> List[CloudResource]:
        """
        Get all supported Azure resources
        
        Returns:
            List of all CloudResource objects
        """
        all_resources = []
        
        # Get storage accounts
        storage_resources = await self.get_storage_accounts()
        all_resources.extend(storage_resources)
        
        # Get virtual machines
        vm_resources = await self.get_virtual_machines()
        all_resources.extend(vm_resources)
        
        # TODO: Add other resource types (SQL databases, Key Vaults, etc.)
        
        logger.info(f"Retrieved {len(all_resources)} total Azure resources")
        return all_resources
