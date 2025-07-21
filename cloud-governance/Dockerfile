# Cloud Governance Policy Scanner - Production Container
# 
# This Dockerfile creates a secure, optimized container for running the
# cloud governance policy scanner service. It implements security best
# practices including non-root user execution, minimal attack surface,
# and comprehensive health monitoring.
#
# Build Command:
#   docker build -t cloud-governance-scanner:latest .
#
# Run Command:
#   docker run -p 8080:8080 cloud-governance-scanner:latest
#
# Multi-stage build considerations:
#   This is a single-stage build optimized for clarity and maintainability.
#   For production, consider multi-stage builds to reduce image size.

# Base Image Selection:
# - python:3.11-slim provides Python 3.11 with minimal OS footprint
# - Debian-based for stability and security patch availability
# - Slim variant reduces image size and attack surface
# - Pin to specific version for reproducible builds in production
FROM python:3.11-slim

# Working Directory:
# - Standardized application directory for consistency
# - All subsequent commands execute from this directory
# - Simplifies path management and deployment scripts
WORKDIR /app

# System Dependencies Installation:
# - Update package lists for latest security patches
# - Install curl for health checks and debugging
# - Clean package cache to reduce image size
# - Use single RUN command to minimize layers
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python Dependencies Installation:
# - Copy requirements first for Docker layer caching optimization
# - Install dependencies before copying source code
# - Use --no-cache-dir to reduce image size
# - Separate layer enables caching when only source code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code Deployment:
# - Copy source code and policies into container
# - Structured layout matches development environment
# - Policies directory contains Rego policy definitions
# - Source code includes all Python modules and dependencies
COPY src/ ./src/
COPY policies/ ./policies/

# Security Hardening:
# - Create dedicated non-root user for application execution
# - UID 1000 follows container security best practices
# - Change ownership of application files to scanner user
# - Prevents privilege escalation and reduces attack surface
RUN useradd -m -u 1000 scanner && chown -R scanner:scanner /app
USER scanner

# Container Health Monitoring:
# - HTTP health check against service endpoint
# - 30-second intervals for regular monitoring
# - 10-second timeout prevents hanging checks
# - 5-second startup grace period for service initialization
# - 3 retries before marking container unhealthy
# - Enables container orchestrator health management
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Network Configuration:
# - Expose port 8080 for HTTP API traffic
# - Matches FastAPI default configuration
# - Required for container orchestration port mapping
# - Documented for deployment and networking setup
EXPOSE 8080

# Application Startup:
# - Execute main module using Python module syntax
# - Enables proper module resolution and imports
# - Starts FastAPI server with uvicorn
# - Configured for production deployment with proper logging
CMD ["python", "-m", "src.main"]
