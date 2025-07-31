/**
 * Main Compliance Dashboard Component
 * 
 * This is the primary dashboard that displays compliance metrics,
 * policy violations, and trend analysis. It serves as the main
 * interface for monitoring cloud resource compliance.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement, BarElement } from 'chart.js';
import { Line, Doughnut, Bar } from 'react-chartjs-2';
import { AlertTriangle, Shield, TrendingUp, Filter, RefreshCw, Download, Calendar } from 'lucide-react';
import {
  ComplianceDashboardMetrics,
  PolicyViolation,
  DashboardFilters,
  ComplianceScanResult
} from '../types/compliance';
import complianceApi from '../services/complianceApi';
import ViolationsTable from './ViolationsTable';
import ScanProgress from './ScanProgress';
import FilterPanel from './FilterPanel';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  BarElement
);

interface ComplianceDashboardProps {
  /** Initial filters to apply */
  initialFilters?: Partial<DashboardFilters>;
  /** Refresh interval in milliseconds */
  refreshInterval?: number;
}

export const ComplianceDashboard: React.FC<ComplianceDashboardProps> = ({
  initialFilters = {},
  refreshInterval = 30000 // 30 seconds default
}) => {
  // State management
  const [metrics, setMetrics] = useState<ComplianceDashboardMetrics | null>(null);
  const [violations, setViolations] = useState<PolicyViolation[]>([]);
  const [activeScans, setActiveScans] = useState<ComplianceScanResult[]>([]);
  const [filters, setFilters] = useState<Partial<DashboardFilters>>(initialFilters);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  /**
   * Load dashboard data from API
   */
  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load metrics and violations in parallel
      const [metricsData, violationsData] = await Promise.all([
        complianceApi.getDashboardMetrics(filters),
        complianceApi.getViolations({ 
          filters, 
          page: 1, 
          page_size: 100,
          sort_by: 'severity',
          sort_order: 'desc'
        })
      ]);

      setMetrics(metricsData);
      setViolations(violationsData.violations);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load compliance data. Please check your connection.');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  /**
   * Initiate a new compliance scan
   */
  const startNewScan = useCallback(async (provider: 'AWS' | 'AZURE' | 'GCP') => {
    try {
      const scanResult = await complianceApi.startComplianceScan({
        provider,
        resource_types: ['S3_BUCKET', 'EC2_INSTANCE', 'RDS_DB_INSTANCE'],
        policy_bundle: 'security_baseline',
        compliance_frameworks: ['SOC2', 'PCI_DSS']
      });

      console.log(`Started compliance scan: ${scanResult.scan_id}`);
      
      // Refresh dashboard to show new scan
      setTimeout(() => loadDashboardData(), 2000);
    } catch (err) {
      console.error('Failed to start compliance scan:', err);
      setError('Failed to start compliance scan. Please try again.');
    }
  }, [loadDashboardData]);

  // Load data on component mount and when filters change
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  // Set up auto-refresh interval
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(loadDashboardData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [loadDashboardData, refreshInterval]);

  // Prepare chart data
  const severityChartData = metrics ? {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [{
      data: [
        metrics.violations_by_severity.CRITICAL,
        metrics.violations_by_severity.HIGH,
        metrics.violations_by_severity.MEDIUM,
        metrics.violations_by_severity.LOW
      ],
      backgroundColor: ['#dc2626', '#ea580c', '#d97706', '#65a30d'],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  } : null;

  const complianceScoreData = metrics ? {
    labels: ['Compliant', 'Non-Compliant'],
    datasets: [{
      data: [metrics.compliance_score, 100 - metrics.compliance_score],
      backgroundColor: ['#16a34a', '#dc2626'],
      borderWidth: 2,
      borderColor: '#ffffff'
    }]
  } : null;

  const trendChartData = metrics ? {
    labels: metrics.compliance_trend.map(point => 
      new Date(point.date).toLocaleDateString()
    ),
    datasets: [{
      label: 'Compliance Score (%)',
      data: metrics.compliance_trend.map(point => point.compliance_score),
      borderColor: '#2563eb',
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      tension: 0.4
    }, {
      label: 'Violations Count',
      data: metrics.compliance_trend.map(point => point.violations_count),
      borderColor: '#dc2626',
      backgroundColor: 'rgba(220, 38, 38, 0.1)',
      yAxisID: 'y1',
      tension: 0.4
    }]
  } : null;

  if (loading && !metrics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center space-x-3">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
          <span className="text-lg">Loading compliance dashboard...</span>
        </div>
      </div>
    );
  }

  if (error && !metrics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Dashboard Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Cloud Compliance Dashboard
                </h1>
                <p className="text-sm text-gray-600">
                  Last updated: {lastRefresh.toLocaleTimeString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </button>
              
              <button
                onClick={loadDashboardData}
                disabled={loading}
                className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>

              <div className="flex space-x-2">
                <button
                  onClick={() => startNewScan('AWS')}
                  className="px-3 py-2 bg-orange-600 text-white text-sm rounded-md hover:bg-orange-700"
                >
                  Scan AWS
                </button>
                <button
                  onClick={() => startNewScan('AZURE')}
                  className="px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                >
                  Scan Azure
                </button>
                <button
                  onClick={() => startNewScan('GCP')}
                  className="px-3 py-2 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                >
                  Scan GCP
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Filter Panel */}
      {showFilters && (
        <FilterPanel
          filters={filters}
          onFiltersChange={setFilters}
          onClose={() => setShowFilters(false)}
        />
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Metrics Overview */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Compliance Score */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Compliance Score</h3>
                <Shield className="w-5 h-5 text-blue-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {metrics.compliance_score.toFixed(1)}%
              </div>
              <p className="text-sm text-gray-600">
                {metrics.compliant_resources} of {metrics.total_resources} resources
              </p>
            </div>

            {/* Critical Violations */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Critical Issues</h3>
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <div className="text-3xl font-bold text-red-600">
                {metrics.violations_by_severity.CRITICAL}
              </div>
              <p className="text-sm text-gray-600">
                Require immediate attention
              </p>
            </div>

            {/* Total Resources */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Total Resources</h3>
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <div className="text-3xl font-bold text-gray-900">
                {metrics.total_resources.toLocaleString()}
              </div>
              <p className="text-sm text-gray-600">
                Across all cloud providers
              </p>
            </div>

            {/* All Violations */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-medium text-gray-600">Total Violations</h3>
                <AlertTriangle className="w-5 h-5 text-orange-600" />
              </div>
              <div className="text-3xl font-bold text-orange-600">
                {Object.values(metrics.violations_by_severity).reduce((a, b) => a + b, 0)}
              </div>
              <p className="text-sm text-gray-600">
                Policy violations found
              </p>
            </div>
          </div>
        )}

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Compliance Score Pie Chart */}
          {complianceScoreData && (
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">Compliance Overview</h3>
              <div className="h-64">
                <Doughnut 
                  data={complianceScoreData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }}
                />
              </div>
            </div>
          )}

          {/* Violations by Severity */}
          {severityChartData && (
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">Violations by Severity</h3>
              <div className="h-64">
                <Doughnut 
                  data={severityChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }}
                />
              </div>
            </div>
          )}

          {/* Compliance Trend */}
          {trendChartData && (
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold mb-4">Compliance Trend</h3>
              <div className="h-64">
                <Line 
                  data={trendChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index' as const, intersect: false },
                    scales: {
                      y: { type: 'linear' as const, display: true, position: 'left' as const },
                      y1: { type: 'linear' as const, display: true, position: 'right' as const, grid: { drawOnChartArea: false } }
                    }
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Active Scans */}
        {activeScans.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">Active Scans</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {activeScans.map(scan => (
                <ScanProgress key={scan.scan_id} scan={scan} />
              ))}
            </div>
          </div>
        )}

        {/* Violations Table */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold">Recent Policy Violations</h2>
              <div className="flex items-center space-x-2">
                <button className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </button>
                <button className="flex items-center px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
                  <Calendar className="w-4 h-4 mr-2" />
                  Date Range
                </button>
              </div>
            </div>
          </div>
          
          <ViolationsTable 
            violations={violations}
            onViolationUpdate={() => loadDashboardData()}
          />
        </div>
      </main>
    </div>
  );
};

export default ComplianceDashboard;