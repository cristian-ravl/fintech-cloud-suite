/**
 * TypeScript definitions for FinTech Cloud Compliance Dashboard
 * 
 * These types define the data structures used throughout the compliance
 * dashboard application for policy evaluation results, scan status,
 * and visualization components.
 */

export interface CloudResource {
  /** Unique identifier for the cloud resource */
  id: string;
  /** Display name of the resource */
  name: string;
  /** Type of cloud resource (S3_BUCKET, EC2_INSTANCE, etc.) */
  type: string;
  /** Cloud provider (AWS, AZURE, GCP) */
  provider: 'AWS' | 'AZURE' | 'GCP';
  /** AWS region, Azure location, or GCP zone */
  region: string;
  /** Cloud account ID or subscription ID */
  account_id: string;
  /** Resource configuration data for policy evaluation */
  configuration: Record<string, any>;
  /** Resource tags/labels */
  tags: Record<string, string>;
  /** Timestamp when resource was discovered */
  discovered_at: string;
}

export interface PolicyViolation {
  /** Unique violation identifier */
  violation_id: string;
  /** Policy that was violated */
  policy_name: string;
  /** Resource that violated the policy */
  resource: CloudResource;
  /** Severity level of the violation */
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  /** Detailed violation description */
  description: string;
  /** Suggested remediation steps */
  remediation: string;
  /** Compliance frameworks affected */
  frameworks: ComplianceFramework[];
  /** When violation was detected */
  detected_at: string;
  /** Current status of the violation */
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'ACCEPTED';
}

export interface ComplianceFramework {
  /** Framework identifier (SOC2, PCI_DSS, GDPR, etc.) */
  id: string;
  /** Human-readable framework name */
  name: string;
  /** Specific control or requirement violated */
  control_id: string;
  /** Control description */
  control_description: string;
}

export interface ComplianceScanResult {
  /** Unique scan identifier */
  scan_id: string;
  /** Scan execution status */
  status: 'running' | 'completed' | 'failed';
  /** Cloud provider that was scanned */
  provider: 'AWS' | 'AZURE' | 'GCP';
  /** Total number of resources evaluated */
  total_resources: number;
  /** Number of resources scanned so far */
  scanned_resources: number;
  /** Total violations found */
  violations_count: number;
  /** Violations grouped by severity */
  violations_by_severity: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
    CRITICAL: number;
  };
  /** Individual policy violation details */
  violations: PolicyViolation[];
  /** When scan was initiated */
  start_time: string;
  /** When scan completed (if applicable) */
  end_time?: string;
  /** Scan execution duration in seconds */
  duration?: number;
}

export interface ComplianceDashboardMetrics {
  /** Overall compliance score (0-100%) */
  compliance_score: number;
  /** Total number of cloud resources */
  total_resources: number;
  /** Number of compliant resources */
  compliant_resources: number;
  /** Number of resources with violations */
  non_compliant_resources: number;
  /** Violations grouped by severity level */
  violations_by_severity: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
    CRITICAL: number;
  };
  /** Violations grouped by cloud provider */
  violations_by_provider: {
    AWS: number;
    AZURE: number;
    GCP: number;
  };
  /** Compliance status by framework */
  compliance_by_framework: Array<{
    framework: ComplianceFramework;
    compliance_percentage: number;
    violations_count: number;
  }>;
  /** Historical compliance trend data */
  compliance_trend: Array<{
    date: string;
    compliance_score: number;
    violations_count: number;
  }>;
}

export interface DashboardFilters {
  /** Filter by cloud provider */
  providers: ('AWS' | 'AZURE' | 'GCP')[];
  /** Filter by violation severity */
  severities: ('LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL')[];
  /** Filter by specific cloud accounts */
  account_ids: string[];
  /** Filter by compliance frameworks */
  frameworks: string[];
  /** Filter by violation status */
  statuses: ('OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'ACCEPTED')[];
  /** Date range filter */
  date_range: {
    start_date: string;
    end_date: string;
  };
}

export interface ApiResponse<T> {
  /** Response data */
  data: T;
  /** Response status message */
  message: string;
  /** Response timestamp */
  timestamp: string;
  /** Request tracing ID */
  request_id: string;
}

export interface ApiError {
  /** Error code */
  code: string;
  /** Error message */
  message: string;
  /** Additional error details */
  details?: Record<string, any>;
  /** Request tracing ID */
  request_id: string;
}