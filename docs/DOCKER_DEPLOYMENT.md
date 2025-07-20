# FenixAI Docker Deployment Guide

## 🐳 Overview

This guide covers the complete Docker containerization setup for FenixAI, designed to work seamlessly with your external Ollama service at `192.168.1.100`.

## 📋 Prerequisites

### System Requirements
- **Docker Engine** 20.10+
- **Docker Compose** 2.0+
- **Minimum RAM**: 2GB available
- **Network Access**: To 192.168.1.100:11434
- **Storage**: 10GB free space

### Ollama Server Requirements
- Ollama running on `192.168.1.100:11434`
- Required models installed:
  - `qwen2.5:7b-instruct-q5_k_m`
  - `qwen2.5vl:7b-q4_K_M`
  - `adrienbrault/nous-hermes2pro-llama3-8b:q4_K_M`

## 🚀 Quick Start

### 1. Verify System Requirements

**Windows (PowerShell):**
```powershell
.\docker-manage.ps1 check
```

**Linux/macOS (Bash):**
```bash
chmod +x docker-manage.sh
./docker-manage.sh check
```

### 2. Build and Start

**Windows:**
```powershell
# Build the Docker image
.\docker-manage.ps1 build

# Start all services
.\docker-manage.ps1 start
```

**Linux/macOS:**
```bash
# Build the Docker image
./docker-manage.sh build

# Start all services
./docker-manage.sh start
```

### 3. Verify Deployment

Check service status:
```bash
# Windows
.\docker-manage.ps1 status

# Linux/macOS
./docker-manage.sh status
```

View logs:
```bash
# Windows
.\docker-manage.ps1 logs

# Linux/macOS
./docker-manage.sh logs
```

## 🔧 Configuration

### Environment Variables

The Docker setup uses the same environment configuration system established in Phase 1. Key variables:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://192.168.1.100:11434
OLLAMA_TIMEOUT=120

# Trading Configuration
TRADING_MODE=paper
RISK_MANAGEMENT_ENABLED=true
MAX_POSITION_SIZE=1000
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_RETENTION_DAYS=30
```

### Volume Mounts

Persistent data is stored in named volumes:
- `fenixai-logs`: Application logs
- `fenixai-cache`: Model and data cache
- `fenixai-memory`: Trading memory and state
- `fenixai-redis`: Optional Redis cache

### Port Mapping

- `8000`: Web interface (if enabled)
- Internal networking for Ollama communication

## 🛠️ Development Mode

For active development with live code reloading:

**Windows:**
```powershell
.\docker-manage.ps1 dev
```

**Linux/macOS:**
```bash
./docker-manage.sh dev
```

This mode:
- Mounts source code as a volume
- Enables debug logging
- Provides live reload capabilities
- Maintains connection to external Ollama

## 📊 Monitoring and Health Checks

### Built-in Health Checks

The Docker setup includes comprehensive health monitoring:

1. **Ollama Connectivity**: Verifies connection to 192.168.1.100:11434
2. **Model Availability**: Checks required models are accessible
3. **Application Health**: Monitors FenixAI service status

### Viewing Health Status

```bash
# Check overall service health
docker-compose ps

# View detailed container stats
docker stats

# Check health check logs
docker inspect fenixai-trading-bot | grep -A 10 '"Health"'
```

## 🔄 Common Operations

### Starting and Stopping

```bash
# Start services
./docker-manage.sh start
.\docker-manage.ps1 start

# Stop services
./docker-manage.sh stop
.\docker-manage.ps1 stop

# Restart services
./docker-manage.sh restart
.\docker-manage.ps1 restart
```

### Running Commands

Execute commands inside the container:

```bash
# Run paper trading demo
./docker-manage.sh run python paper_trading_demo.py
.\docker-manage.ps1 run python paper_trading_demo.py

# Run model availability check
./docker-manage.sh run python -c "from config.modern_models import print_model_availability_guide; print_model_availability_guide()"

# Interactive shell
./docker-manage.sh run bash
.\docker-manage.ps1 run powershell
```

### Log Management

```bash
# View recent logs
./docker-manage.sh logs
.\docker-manage.ps1 logs

# Follow logs in real-time
./docker-manage.sh follow
.\docker-manage.ps1 follow

# View specific service logs
docker-compose logs fenixai
docker-compose logs redis
```

## 🏗️ Architecture

### Multi-Stage Build

The Dockerfile uses a multi-stage build for optimization:

1. **Builder Stage**: Installs dependencies and builds Python packages
2. **Production Stage**: Minimal runtime environment with only necessary components

### Network Architecture

```
Host Network (192.168.1.0/24)
├── Ollama Server (192.168.1.100:11434)
│
Docker Network (172.20.0.0/16)
├── fenixai-trading-bot (app container)
├── ollama-health-check (connectivity validator)
└── redis (optional caching)
```

### Security Features

- **Non-root user**: Containers run as `fenixai` user
- **Read-only mounts**: Configuration files mounted read-only
- **Resource limits**: CPU and memory constraints
- **Network isolation**: Custom Docker network with controlled access

## 🚨 Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed

**Symptom**: Health check fails, "Ollama server not accessible"

**Solutions**:
```bash
# Test connectivity from host
curl http://192.168.1.100:11434/api/version

# Check firewall rules
# Windows: Check Windows Firewall
# Linux: Check iptables/ufw rules

# Verify Ollama is running on target server
ssh user@192.168.1.100 "systemctl status ollama"
```

#### 2. Models Not Found

**Symptom**: "Primary model unavailable" errors

**Solutions**:
```bash
# Check models on Ollama server
curl http://192.168.1.100:11434/api/tags

# Install missing models on Ollama server
ssh user@192.168.1.100 "ollama pull qwen2.5:7b-instruct-q5_k_m"
```

#### 3. Container Won't Start

**Symptom**: Docker container exits immediately

**Solutions**:
```bash
# Check container logs
docker-compose logs fenixai

# Check disk space
df -h

# Verify Docker resources
docker system df
```

#### 4. Performance Issues

**Symptom**: Slow model responses, timeouts

**Solutions**:
```bash
# Increase resource limits in docker-compose.yml
resources:
  limits:
    memory: 4G
    cpus: '2.0'

# Increase Ollama timeout
OLLAMA_TIMEOUT=180
```

### Debug Commands

```bash
# Enter container for debugging
docker-compose exec fenixai bash

# Check environment variables
docker-compose exec fenixai env | grep OLLAMA

# Test Python imports
docker-compose exec fenixai python -c "from config.modern_models import model_manager; print(model_manager.available_ollama_models)"

# Check network connectivity
docker-compose exec fenixai ping 192.168.1.100
```

## 🔄 Updates and Maintenance

### Pulling Source Updates

Since you want to maintain sync with the upstream repo:

```bash
# Pull latest changes from source repo
git pull upstream main

# Rebuild with updates
./docker-manage.sh stop
./docker-manage.sh build
./docker-manage.sh start
```

### Updating Dependencies

```bash
# Rebuild with updated packages
docker-compose build --no-cache --pull
```

### Cleanup

```bash
# Remove everything (containers, images, volumes)
./docker-manage.sh clean
.\docker-manage.ps1 clean

# Selective cleanup
docker system prune -f
docker volume prune -f
```

## 📈 Production Deployment

### Resource Recommendations

**Minimum**:
- 2 CPU cores
- 4GB RAM
- 20GB storage

**Recommended**:
- 4 CPU cores
- 8GB RAM
- 50GB storage
- SSD for cache volumes

### Production Environment Variables

```env
# Production settings
LOG_LEVEL=INFO
DEBUG=false
TRADING_MODE=live
MONITORING_ENABLED=true

# Performance tuning
OLLAMA_TIMEOUT=60
MAX_WORKERS=4
CACHE_SIZE=1GB
```

### Monitoring Stack (Optional)

Add monitoring services to `docker-compose.yml`:

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
```

## 🎯 Next Steps

1. **Test the deployment** with your specific trading strategies
2. **Set up monitoring** for production use
3. **Configure backup** for persistent volumes
4. **Implement CI/CD** for automated deployments
5. **Scale horizontally** if needed with Docker Swarm or Kubernetes

The Docker setup preserves all your Phase 1 environment configurations while providing a robust, scalable deployment platform that seamlessly connects to your external Ollama service! 🚀
