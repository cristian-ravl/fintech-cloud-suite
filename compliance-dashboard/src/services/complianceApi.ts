/**
 * Compliance API Service
 * 
 * This service provides methods to interact with the FastAPI backend
 * for retrieving compliance scan results, policy violations, and
 * dashboard metrics. Includes error handling and request retries.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  ComplianceScanResult,
  ComplianceDashboardMetrics,
  PolicyViolation,
  DashboardFilters,
  ApiResponse,
  ApiError
} from '../types/compliance';

class ComplianceApiService {
  private apiClient: AxiosInstance;
  private baseURL: string;

  constructor() {
    // Use environment variable or default to local development
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    
    this.apiClient = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 second timeout for compliance scans
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    // Request interceptor for logging and authentication
    this.apiClient.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        
        // Add API key if available (for production deployment)
        const apiKey = process.env.REACT_APP_API_KEY;
        if (apiKey) {
          config.headers.Authorization = `Bearer ${apiKey}`;
        }
        
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.apiClient.interceptors.response.use(
      (response) => {
        console.log(`[API] ${response.status} ${response.config.url}`);
        return response;
      },
      (error: AxiosError) => {
        console.error('[API] Response error:', error.response?.data || error.message);
        return Promise.reject(this.handleApiError(error));
      }
    );
  }

  /**
   * Handle API errors and convert to standardized format
   */
  private handleApiError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      const responseData = error.response.data as any;
      return {
        code: responseData.code || `HTTP_${error.response.status}`,
        message: responseData.message || error.message,
        details: responseData.details,
        request_id: responseData.request_id || 'unknown'
      };
    } else if (error.request) {
      // Network error
      return {
        code: 'NETWORK_ERROR',
        message: 'Unable to connect to compliance service',
        request_id: 'unknown'
      };
    } else {
      // Request configuration error
      return {
        code: 'REQUEST_ERROR',
        message: error.message,
        request_id: 'unknown'
      };
    }
  }

  /**
   * Check if the compliance service is healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.apiClient.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  /**
   * Initiate a new compliance scan
   */
  async startComplianceScan(scanRequest: {
    provider: 'AWS' | 'AZURE' | 'GCP';
    resource_types: string[];
    policy_bundle: string;
    compliance_frameworks: string[];
  }): Promise<{ scan_id: string; status: string; message: string }> {
    const response = await this.apiClient.post<ApiResponse<any>>('/scan', scanRequest);
    return response.data.data;
  }

  /**
   * Get status of a running compliance scan
   */
  async getScanStatus(scanId: string): Promise<ComplianceScanResult> {
    const response = await this.apiClient.get<ApiResponse<ComplianceScanResult>>(
      `/scan/${scanId}/status`
    );
    return response.data.data;
  }

  /**
   * Get detailed results of a completed compliance scan
   */
  async getScanResults(scanId: string): Promise<ComplianceScanResult> {
    const response = await this.apiClient.get<ApiResponse<ComplianceScanResult>>(
      `/scan/${scanId}/results`
    );
    return response.data.data;
  }

  /**
   * Get dashboard metrics and summary statistics
   */
  async getDashboardMetrics(filters?: Partial<DashboardFilters>): Promise<ComplianceDashboardMetrics> {
    const params = filters ? { filters: JSON.stringify(filters) } : {};
    const response = await this.apiClient.get<ApiResponse<ComplianceDashboardMetrics>>(
      '/dashboard/metrics',
      { params }
    );
    return response.data.data;
  }

  /**
   * Get list of policy violations with filtering and pagination
   */
  async getViolations(options?: {
    filters?: Partial<DashboardFilters>;
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<{
    violations: PolicyViolation[];
    total_count: number;
    page: number;
    page_size: number;
    total_pages: number;
  }> {
    const params = {
      page: options?.page || 1,
      page_size: options?.page_size || 50,
      sort_by: options?.sort_by || 'detected_at',
      sort_order: options?.sort_order || 'desc',
      ...(options?.filters && { filters: JSON.stringify(options.filters) })
    };

    const response = await this.apiClient.get<ApiResponse<any>>('/violations', { params });
    return response.data.data;
  }

  /**
   * Get available OPA policies for display in the dashboard
   */
  async getPolicies(): Promise<Array<{
    name: string;
    description: string;
    frameworks: string[];
    resource_types: string[];
  }>> {
    const response = await this.apiClient.get<ApiResponse<any>>('/policies');
    return response.data.data;
  }

  /**
   * Update violation status (for remediation tracking)
   */
  async updateViolationStatus(
    violationId: string, 
    status: 'IN_PROGRESS' | 'RESOLVED' | 'ACCEPTED',
    notes?: string
  ): Promise<void> {
    await this.apiClient.patch(`/violations/${violationId}/status`, {
      status,
      notes
    });
  }

  /**
   * Get compliance trend data for historical analysis
   */
  async getComplianceTrend(options: {
    start_date: string;
    end_date: string;
    provider?: 'AWS' | 'AZURE' | 'GCP';
    framework?: string;
  }): Promise<Array<{
    date: string;
    compliance_score: number;
    violations_count: number;
    scanned_resources: number;
  }>> {
    const response = await this.apiClient.get<ApiResponse<any>>('/dashboard/trend', {
      params: options
    });
    return response.data.data;
  }
}

// Create singleton instance
export const complianceApi = new ComplianceApiService();
export default complianceApi;