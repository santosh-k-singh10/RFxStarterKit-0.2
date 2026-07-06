# Docker Deployment Guide

This guide explains how to deploy RFxStarterKit using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM available for containers
- API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)

## Quick Start

### 1. Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Access Services

- **RFP Analyzer**: http://localhost:8080
- **Scoping Architect**: http://localhost:8001

### 4. Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Service Architecture

```
┌─────────────────────────────────────────┐
│         Docker Compose Stack            │
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────┐    │
│  │   RFP Analyzer                 │    │
│  │   Port: 8080                   │    │
│  │   Health: /health              │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Scoping Architect            │    │
│  │   Port: 8001                   │    │
│  │   Health: /api/health          │    │
│  └────────────────────────────────┘    │
│                                         │
│  ┌────────────────────────────────┐    │
│  │   Shared Volumes               │    │
│  │   - outputs/                   │    │
│  │   - logs/                      │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## Docker Commands

### Build Services

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build rfp-analyzer
docker-compose build scoping-architect

# Build without cache
docker-compose build --no-cache
```

### Start Services

```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up rfp-analyzer

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f rfp-analyzer
```

### Stop Services

```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop rfp-analyzer

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Service Management

```bash
# Restart services
docker-compose restart

# Restart specific service
docker-compose restart rfp-analyzer

# View running containers
docker-compose ps

# View service logs
docker-compose logs rfp-analyzer
docker-compose logs scoping-architect

# Execute command in container
docker-compose exec rfp-analyzer bash
docker-compose exec scoping-architect python --version
```

## Environment Variables

Configure these in your `.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional
GOOGLE_API_KEY=your_google_key
LOG_LEVEL=INFO
MIN_CONFIDENCE=0.0
ENABLE_SAP_MAPPING=true
ENABLE_RISK_ASSESSMENT=true
```

## Volume Mounts

### Default Volumes

- `./outputs` → `/app/outputs` - Analysis outputs
- `./logs` → `/app/logs` - Application logs
- `./sample-rfps` → `/app/sample-rfps` - Sample data (read-only)

### Custom Volumes

Modify `docker-compose.yml` to add custom volumes:

```yaml
volumes:
  - ./my-rfps:/app/my-rfps:ro
  - ./custom-config:/app/config:ro
```

## Health Checks

Both services include health checks:

```bash
# Check RFP Analyzer health
curl http://localhost:8080/health

# Check Scoping Architect health
curl http://localhost:8001/api/health

# View health status
docker-compose ps
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs rfp-analyzer

# Check container status
docker-compose ps

# Rebuild without cache
docker-compose build --no-cache rfp-analyzer
```

### Port Already in Use

```bash
# Change ports in docker-compose.yml
ports:
  - "8081:8080"  # Use different host port
```

### Permission Issues

```bash
# Fix volume permissions
sudo chown -R $USER:$USER outputs/ logs/
```

### Out of Memory

```bash
# Increase Docker memory limit
# Docker Desktop: Settings → Resources → Memory
# Or add to docker-compose.yml:
services:
  rfp-analyzer:
    mem_limit: 4g
```

### API Key Not Working

```bash
# Verify .env file exists
ls -la .env

# Check environment variables in container
docker-compose exec rfp-analyzer env | grep API_KEY

# Restart services after changing .env
docker-compose restart
```

## Production Deployment

### Security Considerations

1. **Use secrets management**
   ```yaml
   secrets:
     openai_key:
       file: ./secrets/openai_key.txt
   ```

2. **Limit container resources**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2'
         memory: 4G
   ```

3. **Use read-only file systems where possible**
   ```yaml
   read_only: true
   tmpfs:
     - /tmp
   ```

### Scaling

```bash
# Scale services
docker-compose up --scale rfp-analyzer=3

# Use load balancer (nginx, traefik)
# See docs/LOAD_BALANCING.md
```

### Monitoring

```bash
# View resource usage
docker stats

# View container logs
docker-compose logs --tail=100 -f

# Export logs
docker-compose logs > logs/docker-logs.txt
```

## Advanced Configuration

### Custom Dockerfile

Create `docker-compose.override.yml`:

```yaml
version: '3.8'
services:
  rfp-analyzer:
    build:
      context: .
      dockerfile: Dockerfile.custom
    environment:
      - CUSTOM_VAR=value
```

### Multi-stage Builds

For smaller images, use multi-stage builds:

```dockerfile
FROM python:3.10-slim as builder
# Build dependencies

FROM python:3.10-slim
# Copy only necessary files
```

### Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml rfx-stack

# View services
docker service ls

# Scale service
docker service scale rfx-stack_rfp-analyzer=3
```

## Backup and Restore

### Backup Volumes

```bash
# Backup outputs
docker run --rm -v rfxstarterkit_outputs:/data -v $(pwd):/backup \
  alpine tar czf /backup/outputs-backup.tar.gz /data

# Backup logs
docker run --rm -v rfxstarterkit_logs:/data -v $(pwd):/backup \
  alpine tar czf /backup/logs-backup.tar.gz /data
```

### Restore Volumes

```bash
# Restore outputs
docker run --rm -v rfxstarterkit_outputs:/data -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/outputs-backup.tar.gz --strip 1"
```

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify health: `docker-compose ps`
3. Review documentation
4. Open