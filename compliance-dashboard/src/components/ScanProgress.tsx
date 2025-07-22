/**
 * Scan Progress Component
 * 
 * Displays real-time progress of active compliance scans
 * with progress bars and status indicators.
 */

import React, { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, Clock, Loader, Play, Pause } from 'lucide-react';
import { ComplianceScanResult } from '../types/compliance';
import complianceApi from '../services/complianceApi';

interface ScanProgressProps {
  scan: ComplianceScanResult;
  onScanComplete?: () => void;
}

const ScanProgress: React.FC<ScanProgressProps> = ({ scan: initialScan, onScanComplete }) => {
  const [scan, setScan] = useState(initialScan);
  const [loading, setLoading] = useState(false);

  /**
   * Fetch latest scan status
   */
  const updateScanStatus = async () => {
    try {
      setLoading(true);
      const updatedScan = await complianceApi.getScanStatus(scan.scan_id);
      setScan(updatedScan);
      
      if (updatedScan.status === 'completed' && onScanComplete) {
        onScanComplete();
      }
    } catch (error) {
      console.error('Failed to update scan status:', error);
    } finally {
      setLoading(false);
    }
  };

  // Auto-update scan status every 5 seconds for running scans
  useEffect(() => {
    if (scan.status === 'running') {
      const interval = setInterval(updateScanStatus, 5000);
      return () => clearInterval(interval);
    }
  }, [scan.status, scan.scan_id]);

  const getStatusIcon = () => {
    switch (scan.status) {
      case 'running':
        return <Loader className="w-4 h-4 animate-spin text-blue-600" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = () => {
    switch (scan.status) {
      case 'running':
        return 'border-blue-200 bg-blue-50';
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'failed':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const progressPercentage = scan.total_resources > 0 
    ? Math.round((scan.scanned_resources / scan.total_resources) * 100)
    : 0;

  return (
    <div className={`border-2 rounded-lg p-4 ${getStatusColor()}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <h3 className="font-medium text-gray-900">
            {scan.provider} Scan
          </h3>
        </div>
        <span className={`px-2 py-1 text-xs rounded-full font-medium ${
          scan.status === 'running' ? 'bg-blue-100 text-blue-800' :
          scan.status === 'completed' ? 'bg-green-100 text-green-800' :
          scan.status === 'failed' ? 'bg-red-100 text-red-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {scan.status.toUpperCase()}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Progress</span>
          <span>{progressPercentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all duration-300 ${
              scan.status === 'completed' ? 'bg-green-500' :
              scan.status === 'failed' ? 'bg-red-500' :
              'bg-blue-500'
            }`}
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Scan Statistics */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <span className="text-gray-500">Resources:</span>
          <div className="font-medium">
            {scan.scanned_resources.toLocaleString()} / {scan.total_resources.toLocaleString()}
          </div>
        </div>
        <div>
          <span className="text-gray-500">Violations:</span>
          <div className="font-medium">
            {scan.violations_count.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Violations Breakdown */}
      {scan.violations_count > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <div className="text-xs text-gray-600 mb-2">Violations by Severity</div>
          <div className="flex justify-between text-xs">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-red-500 rounded-full mr-1"></div>
              <span>Critical: {scan.violations_by_severity.CRITICAL}</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-1"></div>
              <span>High: {scan.violations_by_severity.HIGH}</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mr-1"></div>
              <span>Med: {scan.violations_by_severity.MEDIUM}</span>
            </div>
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1"></div>
              <span>Low: {scan.violations_by_severity.LOW}</span>
            </div>
          </div>
        </div>
      )}

      {/* Timing Information */}
      <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
        <div>Started: {new Date(scan.start_time).toLocaleString()}</div>
        {scan.end_time && (
          <div>Completed: {new Date(scan.end_time).toLocaleString()}</div>
        )}
        {scan.duration && (
          <div>Duration: {Math.round(scan.duration / 60)} minutes</div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-3 flex space-x-2">
        <button
          onClick={updateScanStatus}
          disabled={loading}
          className="flex items-center px-2 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
        >
          <Loader className={`w-3 h-3 mr-1 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
        
        {scan.status === 'completed' && (
          <button className="flex items-center px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">
            <Play className="w-3 h-3 mr-1" />
            View Results
          </button>
        )}
      </div>
    </div>
  );
};

export default ScanProgress;
