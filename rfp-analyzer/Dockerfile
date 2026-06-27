# Dockerfile for RFP Analyzer MCP Server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt mcp_requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r mcp_requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs uploads outputs/web

# Expose port
EXPOSE 8001

# Set environment variables
ENV MCP_SERVER_PORT=8001
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health').raise_for_status()"

# Run the MCP server
CMD ["python", "mcp_server.py"]