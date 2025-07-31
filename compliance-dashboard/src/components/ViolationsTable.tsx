/**
 * Policy Violations Table Component
 * 
 * Displays detailed policy violations in a sortable, filterable table format.
 * Supports remediation status tracking and violation management.
 */

import React, { useState } from 'react';
import { AlertTriangle, Shield, ExternalLink, ChevronUp, ChevronDown, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { PolicyViolation } from '../types/compliance';
import complianceApi from '../services/complianceApi';

interface ViolationsTableProps {
  violations: PolicyViolation[];
  onViolationUpdate?: () => void;
}

type SortField = 'detected_at' | 'severity' | 'policy_name' | 'resource.name' | 'status';
type SortDirection = 'asc' | 'desc';

const ViolationsTable: React.FC<ViolationsTableProps> = ({ violations, onViolationUpdate }) => {
  const [sortField, setSortField] = useState<SortField>('detected_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [selectedViolations, setSelectedViolations] = useState<Set<string>>(new Set());
  const [expandedViolation, setExpandedViolation] = useState<string | null>(null);

  /**
   * Handle sorting of violations table
   */
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  /**
   * Get sorted violations based on current sort configuration
   */
  const sortedViolations = [...violations].sort((a, b) => {
    let aValue: any, bValue: any;
    
    switch (sortField) {
      case 'detected_at':
        aValue = new Date(a.detected_at).getTime();
        bValue = new Date(b.detected_at).getTime();
        break;
      case 'severity':
        const severityOrder = { CRITICAL: 4, HIGH: 3, MEDIUM: 2, LOW: 1 };
        aValue = severityOrder[a.severity];
        bValue = severityOrder[b.severity];
        break;
      case 'policy_name':
        aValue = a.policy_name.toLowerCase();
        bValue = b.policy_name.toLowerCase();
        break;
      case 'resource.name':
        aValue = a.resource.name.toLowerCase();
        bValue = b.resource.name.toLowerCase();
        break;
      case 'status':
        aValue = a.status;
        bValue = b.status;
        break;
      default:
        return 0;
    }

    if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  /**
   * Update violation status with optimistic UI updates
   */
  const updateViolationStatus = async (
    violationId: string, 
    newStatus: 'IN_PROGRESS' | 'RESOLVED' | 'ACCEPTED'
  ) => {
    try {
      await complianceApi.updateViolationStatus(violationId, newStatus);
      onViolationUpdate?.();
    } catch (error) {
      console.error('Failed to update violation status:', error);
    }
  };

  /**
   * Get severity badge styling
   */
  const getSeverityBadge = (severity: string) => {
    const styles = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-200',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
      MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      LOW: 'bg-green-100 text-green-800 border-green-200'
    };
    return styles[severity as keyof typeof styles] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  /**
   * Get status badge styling and icon
   */
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OPEN':
        return { 
          className: 'bg-red-100 text-red-800 border-red-200', 
          icon: <XCircle className="w-3 h-3" /> 
        };
      case 'IN_PROGRESS':
        return { 
          className: 'bg-blue-100 text-blue-800 border-blue-200', 
          icon: <Clock className="w-3 h-3" /> 
        };
      case 'RESOLVED':
        return { 
          className: 'bg-green-100 text-green-800 border-green-200', 
          icon: <CheckCircle className="w-3 h-3" /> 
        };
      case 'ACCEPTED':
        return { 
          className: 'bg-gray-100 text-gray-800 border-gray-200', 
          icon: <AlertCircle className="w-3 h-3" /> 
        };
      default:
        return { 
          className: 'bg-gray-100 text-gray-800 border-gray-200', 
          icon: <AlertCircle className="w-3 h-3" /> 
        };
    }
  };

  /**
   * Render sortable table header
   */
  const SortableHeader: React.FC<{ field: SortField; children: React.ReactNode }> = ({ field, children }) => (
    <th 
      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-50"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center space-x-1">
        <span>{children}</span>
        {sortField === field && (
          sortDirection === 'asc' ? 
            <ChevronUp className="w-4 h-4" /> : 
            <ChevronDown className="w-4 h-4" />
        )}
      </div>
    </th>
  );

  if (violations.length === 0) {
    return (
      <div className="text-center py-12">
        <Shield className="w-12 h-12 text-green-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Policy Violations Found</h3>
        <p className="text-gray-600">All scanned resources are compliant with the applied policies.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="relative w-12 px-6 sm:w-16 sm:px-8">
                <input
                  type="checkbox"
                  className="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-blue-600"
                  checked={selectedViolations.size === violations.length && violations.length > 0}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedViolations(new Set(violations.map(v => v.violation_id)));
                    } else {
                      setSelectedViolations(new Set());
                    }
                  }}
                />
              </th>
              
              <SortableHeader field="severity">Severity</SortableHeader>
              <SortableHeader field="policy_name">Policy</SortableHeader>
              <SortableHeader field="resource.name">Resource</SortableHeader>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Provider
              </th>
              <SortableHeader field="status">Status</SortableHeader>
              <SortableHeader field="detected_at">Detected</SortableHeader>
              <th className="relative px-6 py-3">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedViolations.map((violation) => (
              <React.Fragment key={violation.violation_id}>
                {/* Main Row */}
                <tr className={`hover:bg-gray-50 ${selectedViolations.has(violation.violation_id) ? 'bg-blue-50' : ''}`}>
                  <td className="relative w-12 px-6 sm:w-16 sm:px-8">
                    <input
                      type="checkbox"
                      className="absolute left-4 top-1/2 -mt-2 h-4 w-4 rounded border-gray-300 text-blue-600"
                      checked={selectedViolations.has(violation.violation_id)}
                      onChange={(e) => {
                        const newSelected = new Set(selectedViolations);
                        if (e.target.checked) {
                          newSelected.add(violation.violation_id);
                        } else {
                          newSelected.delete(violation.violation_id);
                        }
                        setSelectedViolations(newSelected);
                      }}
                    />
                  </td>
                  
                  {/* Severity */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getSeverityBadge(violation.severity)}`}>
                      {violation.severity === 'CRITICAL' && <AlertTriangle className="w-3 h-3 mr-1" />}
                      {violation.severity}
                    </span>
                  </td>
                  
                  {/* Policy Name */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {violation.policy_name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {violation.frameworks.map(f => f.name).join(', ')}
                    </div>
                  </td>
                  
                  {/* Resource */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {violation.resource.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {violation.resource.type}
                    </div>
                  </td>
                  
                  {/* Provider */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                      {violation.resource.provider}
                    </span>
                  </td>
                  
                  {/* Status */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getStatusBadge(violation.status).className}`}>
                        {getStatusBadge(violation.status).icon}
                        <span className="ml-1">{violation.status}</span>
                      </span>
                    </div>
                  </td>
                  
                  {/* Detected Date */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(violation.detected_at).toLocaleDateString()}
                  </td>
                  
                  {/* Actions */}
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setExpandedViolation(
                          expandedViolation === violation.violation_id ? null : violation.violation_id
                        )}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        {expandedViolation === violation.violation_id ? 'Hide' : 'Details'}
                      </button>
                      
                      {violation.status === 'OPEN' && (
                        <select
                          className="text-sm border-gray-300 rounded"
                          onChange={(e) => {
                            if (e.target.value) {
                              updateViolationStatus(violation.violation_id, e.target.value as any);
                            }
                          }}
                          value=""
                        >
                          <option value="">Update Status</option>
                          <option value="IN_PROGRESS">Mark In Progress</option>
                          <option value="RESOLVED">Mark Resolved</option>
                          <option value="ACCEPTED">Accept Risk</option>
                        </select>
                      )}
                    </div>
                  </td>
                </tr>
                
                {/* Expanded Details Row */}
                {expandedViolation === violation.violation_id && (
                  <tr>
                    <td colSpan={8} className="px-6 py-4 bg-gray-50">
                      <div className="space-y-4">
                        {/* Description */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Violation Details</h4>
                          <p className="text-sm text-gray-700">{violation.description}</p>
                        </div>
                        
                        {/* Remediation */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Recommended Remediation</h4>
                          <p className="text-sm text-gray-700 mb-2">{violation.remediation}</p>
                          <a 
                            href="#" 
                            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-900"
                          >
                            View Documentation <ExternalLink className="w-3 h-3 ml-1" />
                          </a>
                        </div>
                        
                        {/* Resource Details */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Resource Information</h4>
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium">Account:</span> {violation.resource.account_id}
                            </div>
                            <div>
                              <span className="font-medium">Region:</span> {violation.resource.region}
                            </div>
                            <div className="col-span-2">
                              <span className="font-medium">Tags:</span>{' '}
                              {Object.entries(violation.resource.tags).map(([key, value]) => (
                                <span key={key} className="inline-block bg-gray-200 rounded px-2 py-1 text-xs mr-2 mb-1">
                                  {key}: {value}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        
                        {/* Compliance Frameworks */}
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Affected Compliance Frameworks</h4>
                          <div className="space-y-2">
                            {violation.frameworks.map((framework, idx) => (
                              <div key={idx} className="text-sm">
                                <span className="font-medium">{framework.name}</span> - {framework.control_id}: {framework.control_description}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Bulk Actions */}
      {selectedViolations.size > 0 && (
        <div className="bg-blue-50 px-6 py-3 border-t border-blue-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-700">
              {selectedViolations.size} violation{selectedViolations.size !== 1 ? 's' : ''} selected
            </span>
            <div className="space-x-2">
              <button className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                Mark In Progress
              </button>
              <button className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700">
                Mark Resolved
              </button>
              <button className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700">
                Accept Risk
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ViolationsTable;