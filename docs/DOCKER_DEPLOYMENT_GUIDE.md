# FenixAI Docker Deployment Guide

## Overview

This guide covers deploying FenixAI to remote Docker environments, including self-hosted servers, NAS systems, and cloud platforms. Since FenixAI is a custom application, you'll need to build and distribute the Docker image.

## 🚀 Deployment Options

### Option 1: Docker Hub (Recommended for Easy Distribution)

Push your image to Docker Hub for easy deployment across multiple systems.

#### Step 1: Build and Tag Your Image

```bash
# Build with your Docker Hub username (example using adamcodes716)
docker build -t adamcodes716/fenixai-trading:latest .

# Tag with version (optional but recommended)
docker tag adamcodes716/fenixai-trading:latest adamcodes716/fenixai-trading:v1.0.0
```

#### Step 2: Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push the image
docker push adamcodes716/fenixai-trading:latest
docker push adamcodes716/fenixai-trading:v1.0.0
```

#### Step 3: Deploy on Remote System

```bash
# Pull and run on target system
docker pull adamcodes716/fenixai-trading:latest

# For production deployment (OMV/NAS systems)
docker-compose -f docker-compose.prod.yml up -d

# For development deployment
docker-compose up -d
```

### Option 2: Private Registry

For sensitive trading applications, use a private registry.

#### Setup Private Registry

```bash
# Run private registry
docker run -d -p 5000:5000 --name registry registry:2

# Tag for private registry
docker tag fenixai-trading:latest localhost:5000/fenixai-trading:latest

# Push to private registry
docker push localhost:5000/fenixai-trading:latest
```

### Option 3: Direct Image Transfer

For air-gapped systems or single deployments.

#### Export Image

```bash
# Save image to tar file
docker save fenixai-trading:latest -o fenixai-trading.tar

# Compress for transfer
gzip fenixai-trading.tar
```

#### Import on Target System

```bash
# Transfer file to target system, then:
gunzip fenixai-trading.tar.gz
docker load -i fenixai-trading.tar
```

## 📝 Deployment Configuration

### Multi-Environment Setup

FenixAI supports multiple deployment environments with separate configuration files:

- **`docker-compose.yml`**: Local Windows development environment
- **`docker-compose.prod.yml`**: Production deployment (OMV/NAS systems with host paths)
- **`docker-compose.omv.yml`**: OMV-specific configuration with UUID paths
- **`.env.development`**: Development environment variables
- **`.env.production`**: Production environment variables

### Production Docker Compose (OMV/NAS Systems)

The production configuration (`docker-compose.prod.yml`) is designed for OMV and NAS systems with host path mounting:

```yaml
version: '3.8'

services:
  fenixai:
    image: adamcodes716/fenixai-trading:latest
    container_name: fenixai-trading-bot
    restart: unless-stopped
    
    environment:
      - PYTHONPATH=/app
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
      - ENV=production
      - DEBUG=false
      
    volumes:
      # Use production environment file from OMV host path (read-only)
      - /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/.env.production:/app/.env:ro
      
      # Production data volumes using OMV host paths (read-write for data persistence)
      - /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/data/logs:/app/logs
      - /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/data/cache:/app/cache
      - /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/data/memory:/app/memory
      
      # Configuration override (read-only)
      - /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/config:/app/config:ro
      
    ports:
      - "8020:8020"
      
    depends_on:
      - redis
      
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
      
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8020/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
      
    networks:
      - fenixai-network

  redis:
    image: redis:7-alpine
    container_name: fenixai-redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    
    volumes:
      - /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/data/redis:/data
      
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      
    networks:
      - fenixai-network

networks:
  fenixai-network:
    driver: bridge
```

### Development Docker Compose

For local Windows development with hot reload:

```yaml
version: '3.8'

services:
  fenixai:
    build: 
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: fenixai-dev
    restart: unless-stopped
    
    environment:
      - PYTHONPATH=/app
      - PYTHONDONTWRITEBYTECODE=1
      - PYTHONUNBUFFERED=1
      - ENV=development
      - DEBUG=true
      
    volumes:
      # Use development environment file
      - ./.env.development:/app/.env:ro
      
      # Development: mount source code for hot reload (read-write for development)
      - ./:/app
      
      # Development data volumes
      - fenixai-dev-logs:/app/logs
      - fenixai-dev-cache:/app/cache
      - fenixai-dev-memory:/app/memory
      
      # Configuration override (optional)
      - ./config:/app/config:ro
      
    ports:
      - "8020:8020"
      
    networks:
      - fenixai-dev-network
      
    depends_on:
      - redis-dev

  redis-dev:
    image: redis:7-alpine
    container_name: fenixai-redis-dev
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - fenixai-dev-redis:/data
    networks:
      - fenixai-dev-network

volumes:
  fenixai-dev-logs:
  fenixai-dev-cache:
  fenixai-dev-memory:
  fenixai-dev-redis:

networks:
  fenixai-dev-network:
    driver: bridge
```

### Environment Configuration

FenixAI uses separate environment files for different deployment scenarios:

#### Development Environment (`.env.development`)

```env
# Development Environment Configuration
# Used for local Windows development

# Trading API Keys (use test/sandbox keys for development)
BINANCE_API_KEY=your_dev_binance_api_key
BINANCE_SECRET_KEY=your_dev_binance_secret_key

# Ollama Configuration (external Ollama server)
OLLAMA_BASE_URL=http://192.168.1.100:11434
OLLAMA_TIMEOUT=120

# Trading Settings (safe for development)
TRADING_MODE=paper
RISK_MANAGEMENT_ENABLED=true
MAX_POSITION_SIZE=100
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0

# Logging Configuration
LOG_LEVEL=DEBUG
LOG_FORMAT=json
LOG_RETENTION_DAYS=7

# Development specific
ENV=development
DEBUG=true
ENABLE_DEBUG_ENDPOINTS=true
HOT_RELOAD=true
```

#### Production Environment (`.env.production`)

```env
# Production Environment Configuration
# Used for OMV/NAS deployment

# Trading API Keys (use production keys with restricted permissions)
BINANCE_API_KEY=your_production_binance_api_key
BINANCE_SECRET_KEY=your_production_binance_secret_key

# Ollama Configuration (external Ollama server)
OLLAMA_BASE_URL=http://192.168.1.100:11434
OLLAMA_TIMEOUT=120

# Trading Settings (production values)
TRADING_MODE=paper
RISK_MANAGEMENT_ENABLED=true
MAX_POSITION_SIZE=1000
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30

# Production specific
ENV=production
DEBUG=false
ENABLE_DEBUG_ENDPOINTS=false
HOT_RELOAD=false
```

### Important Configuration Notes

1. **External Ollama**: Both environments use an external Ollama server at `192.168.1.100:11434`
2. **Separate Credentials**: Use different API keys for development and production
3. **Environment Detection**: The system automatically detects the environment based on the loaded configuration
4. **Security**: Never commit `.env` files to version control

## 🔧 Remote System Requirements

### Minimum System Requirements

- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB available space
- **Network**: Stable internet connection
- **Docker**: Version 20.10+ and Docker Compose

### Network Configuration

#### Required Ports

- **8020**: FenixAI Dashboard (HTTP)
- **6379**: Redis (internal)
- **11434**: Ollama (if external)

#### Firewall Rules

```bash
# Allow FenixAI dashboard
sudo ufw allow 8020/tcp

# If using external Ollama
sudo ufw allow from YOUR_NETWORK_RANGE to any port 11434
```

## 🚀 Deployment Commands

### Local Development Deployment

```bash
# 1. Navigate to project directory
cd /path/to/fenixai

# 2. Ensure correct Ollama configuration
# Edit .env.development to point to your Ollama server (e.g., 192.168.1.100:11434)

# 3. Start development environment
docker-compose up -d

# 4. Verify deployment
docker-compose ps
curl http://localhost:8020/health

# 5. Access dashboard
# Open browser to http://localhost:8020/dashboard
```

### Production Deployment (OMV/NAS)

```bash
# 1. Create deployment directory on target system
mkdir -p /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix
cd /opt/fenixai

# 2. Download production configuration
wget https://raw.githubusercontent.com/adamcodes716/fenixai/main/docker-compose.prod.yml

# 3. Create production environment file
nano .env.production
# Add your production configuration (see Environment Configuration section)

# 4. Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify deployment
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:8020/health

# 6. Check logs
docker-compose -f docker-compose.prod.yml logs -f fenixai
```

### Update Deployment

```bash
# Pull latest image
docker-compose -f docker-compose.prod.yml pull fenixai

# Restart with new image
docker-compose -f docker-compose.prod.yml up -d fenixai

# Clean old images
docker image prune -f
```

### Environment-Specific Commands

```bash
# Development environment
docker-compose up -d                    # Start development
docker-compose logs -f fenixai          # View logs
docker-compose restart fenixai          # Restart service
docker-compose down                     # Stop development

# Production environment
docker-compose -f docker-compose.prod.yml up -d       # Start production
docker-compose -f docker-compose.prod.yml logs -f     # View logs
docker-compose -f docker-compose.prod.yml restart     # Restart service
docker-compose -f docker-compose.prod.yml down        # Stop production
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Check health endpoints
curl http://localhost:8020/health
curl http://localhost:8020/api/system/metrics
```

### Backup Strategy

```bash
# For OMV/NAS systems with host path mounting
# Backup host directories directly
tar czf fenixai-backup-$(date +%Y%m%d).tar.gz \
  /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/data/

# For systems using Docker volumes
# Backup individual volumes
docker run --rm -v fenixai-logs:/data -v $(pwd):/backup alpine \
  tar czf /backup/fenixai-logs-$(date +%Y%m%d).tar.gz -C /data .

docker run --rm -v fenixai-memory:/data -v $(pwd):/backup alpine \
  tar czf /backup/fenixai-memory-$(date +%Y%m%d).tar.gz -C /data .

docker run --rm -v fenixai-redis-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/fenixai-redis-$(date +%Y%m%d).tar.gz -C /data .

# Backup configuration files
tar czf fenixai-config-$(date +%Y%m%d).tar.gz \
  .env.production .env.development docker-compose*.yml
```

### Log Rotation

```bash
# Configure log rotation for Docker
sudo nano /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
```

## 🔒 Security Considerations

### Environment File Security

**Important**: Your `.env` file is **NOT** included in the Docker image during build.

- **Build Time**: `.dockerignore` excludes `.env` from the image
- **Runtime**: `.env` is mounted as an external volume
- **Distribution**: Docker images can be safely shared without exposing secrets

**Deployment Process**:
1. Build image locally (secrets excluded automatically)
2. Push to registry (clean image, no secrets)
3. Create `.env` file manually on target system
4. Deploy using volume mounts for configuration

### Production Security

1. **Environment Variables**: Never commit `.env` to version control
2. **Image Distribution**: Docker images contain no secrets and are safe to share
3. **API Keys**: Use restricted API keys with minimal permissions
4. **Network Security**: Use firewalls and VPNs for remote access
5. **Image Security**: Regularly update base images and dependencies
6. **Access Control**: Limit dashboard access to trusted networks
7. **Target System**: Create `.env` files manually on each deployment target

### Secure Configuration

```yaml
# Add to docker-compose.prod.yml for enhanced security
services:
  fenixai:
    # ... existing config ...
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:size=100M
    user: "1000:1000"  # Non-root user
```

## 🌐 Cloud Platform Deployment

### AWS ECS/Fargate

```bash
# Install AWS CLI and ECS CLI
aws configure
ecs-cli configure cluster --cluster-name fenixai --region us-east-1

# Deploy to ECS
ecs-cli compose -f docker-compose.prod.yml up --create-log-groups
```

### Digital Ocean

```bash
# Use DigitalOcean App Platform
doctl apps create --spec .do/app.yaml
```

### Google Cloud Run

```bash
# Build and push to GCR
docker build -t gcr.io/PROJECT_ID/fenixai-trading .
docker push gcr.io/PROJECT_ID/fenixai-trading

# Deploy to Cloud Run
gcloud run deploy fenixai --image gcr.io/PROJECT_ID/fenixai-trading --platform managed
```

## 🎯 Quick Start Guide

### Local Development Setup

For immediate local development on Windows:

```powershell
# 1. Clone repository
git clone https://github.com/adamcodes716/fenixai.git
cd fenixai

# 2. Configure development environment
# Edit .env.development and set your Ollama server IP
# OLLAMA_BASE_URL=http://192.168.1.100:11434

# 3. Start development environment
docker-compose up -d

# 4. Access dashboard
# Open browser: http://localhost:8020/dashboard

# 5. Monitor logs
docker-compose logs -f fenixai
```

### OMV/NAS Production Setup

For deployment on OpenMediaVault or NAS systems:

```bash
# 1. Create data directory structure
sudo mkdir -p /srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/{data/logs,data/cache,data/memory,data/redis,config}

# 2. Download production configuration
wget https://raw.githubusercontent.com/adamcodes716/fenixai/main/docker-compose.prod.yml

# 3. Create production environment file
cat > .env.production << 'EOF'
BINANCE_API_KEY=your_production_api_key
BINANCE_SECRET_KEY=your_production_secret_key
OLLAMA_BASE_URL=http://192.168.1.100:11434
TRADING_MODE=paper
RISK_MANAGEMENT_ENABLED=true
MAX_POSITION_SIZE=1000
LOG_LEVEL=INFO
ENV=production
DEBUG=false
EOF

# 4. Deploy
docker-compose -f docker-compose.prod.yml up -d

# 5. Verify
curl http://localhost:8020/health
```

### Prerequisites

- **Docker**: Version 20.10+ with Docker Compose
- **Ollama Server**: Running at `192.168.1.100:11434` with required models
- **Network Access**: Ports 8020 (dashboard) and 6379 (Redis internal)
- **Storage**: 20GB+ available space for data persistence
- **Memory**: 4GB+ RAM recommended

## 📞 Troubleshooting

### Common Issues

1. **Image Not Found**: Ensure image `adamcodes716/fenixai-trading:latest` is available
2. **Permission Issues**: Check file permissions and user IDs, especially on NAS systems
3. **Network Connectivity**: Verify ports and firewall rules
4. **Resource Limits**: Monitor CPU/memory usage
5. **Ollama Connectivity**: Verify external Ollama service at `192.168.1.100:11434` is accessible
6. **Environment File**: Ensure correct `.env.development` or `.env.production` file is present
7. **OMV Path Issues**: Verify UUID path `/srv/dev-disk-by-uuid-ba1cc561-951a-4ddc-9569-9379a876ff67/AppData/Fenix/` exists

### Debug Commands

```bash
# Check container logs (development)
docker-compose logs fenixai

# Check container logs (production)
docker-compose -f docker-compose.prod.yml logs fenixai

# Interactive shell access
docker-compose exec fenixai bash

# Test Ollama connectivity from container
docker-compose exec fenixai curl -v http://192.168.1.100:11434/api/tags

# Network debugging
docker network ls
docker network inspect fenixai-network
docker network inspect fenixai-dev-network

# Resource usage
docker stats

# Check environment variables in container
docker-compose exec fenixai env | grep -E "(OLLAMA|BINANCE|TRADING)"
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy FenixAI

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            adamcodes716/fenixai-trading:latest
            adamcodes716/fenixai-trading:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          echo "Image adamcodes716/fenixai-trading:latest built and pushed"
          echo "Ready for deployment to production systems"
```

---

This guide provides a comprehensive approach to deploying FenixAI in various environments. Choose the deployment method that best fits your infrastructure and security requirements.
