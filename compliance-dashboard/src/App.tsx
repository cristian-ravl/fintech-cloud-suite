/**
 * Main React Application Entry Point
 * 
 * Sets up routing, global providers, and the root application layout
 * for the FinTech Cloud Compliance Dashboard.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ComplianceDashboard from './components/ComplianceDashboard';
import './styles/globals.css';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        {/* Main dashboard route */}
        <Route path="/" element={<ComplianceDashboard />} />
        
        {/* Dashboard with filters */}
        <Route path="/dashboard" element={<ComplianceDashboard />} />
        
        {/* Redirect any unknown routes to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;
