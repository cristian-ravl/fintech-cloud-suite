/**
 * Advanced Filter Panel Component
 * 
 * Provides comprehensive filtering options for the compliance dashboard
 * including cloud providers, severity levels, compliance frameworks,
 * date ranges, and violation status.
 */

import React, { useState } from 'react';
import { X, Calendar, Filter, RotateCcw } from 'lucide-react';
import { DashboardFilters } from '../types/compliance';

interface FilterPanelProps {
  filters: Partial<DashboardFilters>;
  onFiltersChange: (filters: Partial<DashboardFilters>) => void;
  onClose: () => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFiltersChange, onClose }) => {
  const [localFilters, setLocalFilters] = useState<Partial<DashboardFilters>>(filters);

  /**
   * Apply filters and close panel
   */
  const applyFilters = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  /**
   * Reset all filters to default state
   */
  const resetFilters = () => {
    const emptyFilters: Partial<DashboardFilters> = {
      providers: [],
      severities: [],
      account_ids: [],
      frameworks: [],
      statuses: [],
      date_range: {
        start_date: '',
        end_date: ''
      }
    };
    setLocalFilters(emptyFilters);
  };

  /**
   * Update a specific filter field
   */
  const updateFilter = <K extends keyof DashboardFilters>(
    field: K, 
    value: DashboardFilters[K]
  ) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  /**
   * Toggle a multi-select filter value
   */
  const toggleFilterValue = <K extends keyof DashboardFilters>(
    field: K,
    value: any
  ) => {
    const currentValues = (localFilters[field] as any[]) || [];
    const isSelected = currentValues.includes(value);
    
    updateFilter(field, isSelected 
      ? currentValues.filter((v: any) => v !== value)
      : [...currentValues, value]
    );
  };

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Filter className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Filter Compliance Data</h2>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={resetFilters}
              className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              Reset
            </button>
            
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Filter Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {/* Cloud Providers */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Cloud Providers
            </label>
            <div className="space-y-2">
              {[
                { value: 'AWS' as const, label: 'Amazon Web Services', color: 'bg-orange-100 text-orange-800' },
                { value: 'AZURE' as const, label: 'Microsoft Azure', color: 'bg-blue-100 text-blue-800' },
                { value: 'GCP' as const, label: 'Google Cloud Platform', color: 'bg-green-100 text-green-800' }
              ].map(({ value, label, color }) => (
                <label key={value} className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 rounded border-gray-300"
                    checked={(localFilters.providers || []).includes(value)}
                    onChange={() => toggleFilterValue('providers', value)}
                  />
                  <span className="ml-2 text-sm text-gray-700">{label}</span>
                  <span className={`ml-auto px-2 py-1 text-xs rounded-full ${color}`}>
                    {value}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Severity Levels */}
          <div>
            <label className="block text// filepath: /Users/cristian/Documents/dev/Ravl/AIProductDev/compliance-dashboard/src/components/FilterPanel.tsx
/**
 * Advanced Filter Panel Component
 * 
 * Provides comprehensive filtering options for the compliance dashboard
 * including cloud providers, severity levels, compliance frameworks,
 * date ranges, and violation status.
 */

import React, { useState } from 'react';
import { X, Calendar, Filter, RotateCcw } from 'lucide-react';
import { DashboardFilters } from '../types/compliance';

interface FilterPanelProps {
  filters: Partial<DashboardFilters>;
  onFiltersChange: (filters: Partial<DashboardFilters>) => void;
  onClose: () => void;
}

const FilterPanel: React.FC<FilterPanelProps> = ({ filters, onFiltersChange, onClose }) => {
  const [localFilters, setLocalFilters] = useState<Partial<DashboardFilters>>(filters);

  /**
   * Apply filters and close panel
   */
  const applyFilters = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  /**
   * Reset all filters to default state
   */
  const resetFilters = () => {
    const emptyFilters: Partial<DashboardFilters> = {
      providers: [],
      severities: [],
      account_ids: [],
      frameworks: [],
      statuses: [],
      date_range: {
        start_date: '',
        end_date: ''
      }
    };
    setLocalFilters(emptyFilters);
  };

  /**
   * Update a specific filter field
   */
  const updateFilter = <K extends keyof DashboardFilters>(
    field: K, 
    value: DashboardFilters[K]
  ) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  /**
   * Toggle a multi-select filter value
   */
  const toggleFilterValue = <K extends keyof DashboardFilters>(
    field: K,
    value: any
  ) => {
    const currentValues = (localFilters[field] as any[]) || [];
    const isSelected = currentValues.includes(value);
    
    updateFilter(field, isSelected 
      ? currentValues.filter((v: any) => v !== value)
      : [...currentValues, value]
    );
  };

  return (
    <div className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Filter className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-900">Filter Compliance Data</h2>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={resetFilters}
              className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-900"
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              Reset
            </button>
            
            <button
              onClick={onClose}
              className="p-1 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Filter Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
          {/* Cloud Providers */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Cloud Providers
            </label>
            <div className="space-y-2">
              {[
                { value: 'AWS' as const, label: 'Amazon Web Services', color: 'bg-orange-100 text-orange-800' },
                { value: 'AZURE' as const, label: 'Microsoft Azure', color: 'bg-blue-100 text-blue-800' },
                { value: 'GCP' as const, label: 'Google Cloud Platform', color: 'bg-green-100 text-green-800' }
              ].map(({ value, label, color }) => (
                <label key={value} className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 rounded border-gray-300"
                    checked={(localFilters.providers || []).includes(value)}
                    onChange={() => toggleFilterValue('providers', value)}
                  />
                  <span className="ml-2 text-sm text-gray-700">{label}</span>
                  <span className={`ml-auto px-2 py-1 text-xs rounded-full ${color}`}>
                    {value}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Severity Levels */}
          <div>
            <label className="block text