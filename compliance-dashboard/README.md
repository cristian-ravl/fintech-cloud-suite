# FinTech Cloud Compliance Dashboard

A real-time React-based dashboard for monitoring cloud compliance across AWS, Azure, and GCP environments. Built with TypeScript, Chart.js, and Tailwind CSS.

## 🚀 Features

### 📊 **Real-time Compliance Monitoring**
- **Live Metrics**: Auto-refreshing compliance scores and violation counts
- **Multi-Cloud Support**: Unified view across AWS, Azure, and GCP
- **Severity-based Alerting**: Critical, High, Medium, Low violation levels
- **Historical Trends**: Time-series compliance data with interactive charts

### 🔍 **Advanced Filtering & Search**
- **Provider Filtering**: Filter by specific cloud providers
- **Severity Levels**: Focus on critical issues or view all violations
- **Status Tracking**: Monitor violation remediation progress
- **Date Range Selection**: Analyze compliance over specific time periods

### 📈 **Interactive Visualizations**
- **Chart.js Integration**: Responsive charts for trend analysis
- **Compliance Score Doughnuts**: Visual compliance percentage breakdowns
- **Violation Severity Bars**: Distribution of violation types
- **Timeline Charts**: Historical compliance trends over time

### 📋 **Violation Management**
- **Detailed Violation Table**: Sortable, filterable violation listings
- **Remediation Tracking**: Update violation statuses (Open → In Progress → Resolved)
- **Bulk Actions**: Process multiple violations simultaneously
- **Export Capabilities**: Generate compliance reports for auditors

## 🛠️ **Technology Stack**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend Framework** | React 18 + TypeScript | Type-safe component development |
| **Build Tool** | Vite | Fast development and optimized builds |
| **Styling** | Tailwind CSS | Utility-first responsive design |
| **Charts** | Chart.js + react-chartjs-2 | Interactive data visualizations |
| **Icons** | Lucide React | Consistent, customizable icon set |
| **API Client** | Axios | HTTP requests with interceptors |
| **Routing** | React Router v6 | Client-side routing |

## 📁 **Project Structure**

```
compliance-dashboard/
├── src/
│   ├── components/
│   │   ├── ComplianceDashboard.tsx   # Main dashboard component
│   │   ├── ViolationsTable.tsx       # Detailed violations table
│   │   ├── FilterPanel.tsx           # Advanced filtering interface
│   │   └── ScanProgress.tsx          # Real-time scan progress
│   ├── services/
│   │   └── complianceApi.ts          # API service layer
│   ├── types/
│   │   └── compliance.ts             # TypeScript type definitions
│   ├── styles/
│   │   └── globals.css               # Global styles and utilities
│   ├── App.tsx                       # Root application component
│   └── main.tsx                      # Application entry point
├── public/                           # Static assets
├── index.html                        # HTML template
├── package.json                      # Dependencies and scripts
├── tsconfig.json                     # TypeScript configuration
├── tailwind.config.js                # Tailwind CSS configuration
└── vite.config.ts                    # Vite build configuration
```

## 🚦 **Getting Started**

### Prerequisites
- **Node.js**: Version 16 or higher
- **npm**: Version 8 or higher
- **Backend API**: Cloud Governance FastAPI service running on port 8000

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cristian-ravl/fintech-cloud-suite.git
   cd fintech-cloud-suite/compliance-dashboard
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   # Create .env file
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_API_KEY=your-api-key-here
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

5. **Open browser**: Navigate to `http://localhost:3000`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test

# Type checking
npm run type-check
```

## 🔧 **Configuration**

### API Configuration
The dashboard connects to the FastAPI backend via configurable endpoints:

```typescript
// Default configuration in complianceApi.ts
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Available endpoints:
- GET /dashboard/metrics     # Compliance metrics
- GET /violations           # Policy violations
- PATCH /violations/:id     # Update violation status
- POST /scan               # Start compliance scan
- GET /scan/:id/status     # Check scan progress
```

### Chart Configuration
Customize chart appearance in `ComplianceDashboard.tsx`:

```typescript
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom' }
  }
};
```

## 🎨 **Customization**

### Styling
- **Theme Colors**: Modify `tailwind.config.js` for custom color schemes
- **Component Styles**: Use Tailwind utility classes for styling
- **Global Styles**: Add custom CSS in `src/styles/globals.css`

### Components
- **Dashboard Layout**: Customize metric cards and chart arrangements
- **Table Columns**: Add/remove columns in `ViolationsTable.tsx`
- **Filters**: Extend filter options in `FilterPanel.tsx`

## 📊 **API Integration**

### Data Flow
1. **Dashboard Load**: Fetch metrics and recent violations
2. **Auto-refresh**: Update data every 30 seconds
3. **User Actions**: Filter, sort, and update violation statuses
4. **Scan Management**: Start scans and monitor progress

### Type Safety
All API responses are typed using TypeScript interfaces:

```typescript
interface PolicyViolation {
  violation_id: string;
  policy_name: string;
  resource: CloudResource;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'ACCEPTED';
  // ... additional fields
}
```

## 🧪 **Testing**

### Running Tests
```bash
# Unit tests
npm run test

# Coverage report
npm run test:coverage

# Interactive test UI
npm run test:ui
```

### Test Structure
- **Component Tests**: React Testing Library for component behavior
- **API Tests**: Mock API responses for service testing
- **Type Tests**: Ensure TypeScript type correctness

## 🚀 **Deployment**

### Docker Deployment
```bash
# Build Docker image
docker build -t compliance-dashboard .

# Run container
docker run -p 3000:3000 compliance-dashboard
```

### Environment Configuration
- **Development**: `http://localhost:8000` (local FastAPI)
- **Staging**: `https://api-staging.yourcompany.com`
- **Production**: `https://api.yourcompany.com`

## 📋 **Usage Examples**

### Starting a Compliance Scan
```typescript
// Trigger AWS compliance scan
await complianceApi.startComplianceScan({
  provider: 'AWS',
  resource_types: ['S3_BUCKET', 'EC2_INSTANCE'],
  policy_bundle: 'security_baseline',
  compliance_frameworks: ['SOC2', 'PCI_DSS']
});
```

### Updating Violation Status
```typescript
// Mark violation as resolved
await complianceApi.updateViolationStatus(
  'violation_0001',
  'RESOLVED',
  'Applied encryption configuration'
);
```

## 🔍 **Troubleshooting**

### Common Issues

**API Connection Errors**:
- Verify backend service is running on port 8000
- Check CORS configuration in FastAPI
- Validate API key configuration

**Chart Rendering Issues**:
- Ensure Chart.js is properly registered
- Check data format matches chart expectations
- Verify container dimensions for responsive charts

**Type Errors**:
- Run `npm run type-check` for detailed errors
- Ensure API responses match TypeScript interfaces
- Update type definitions when API changes

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/dashboard-enhancement`
3. **Make changes**: Follow TypeScript and React best practices
4. **Add tests**: Ensure new features are tested
5. **Submit PR**: Include description of changes and test results

## 📄 **License**

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 📞 **Support**

- **Email**: cristian@ravl.ai
- **GitHub Issues**: [Create an issue](https://github.com/cristian-ravl/fintech-cloud-suite/issues)
- **Documentation**: [API Docs](http://localhost:8000/docs)
