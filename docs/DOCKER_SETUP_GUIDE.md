# FenixAI Docker Setup Guide

## Overview

FenixAI is fully containerized using Docker for easy deployment and consistent environments. This guide covers everything you need to know about setting up, running, and managing the FenixAI trading system using Docker.

## 🐳 Quick Start

### Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **Git** for cloning the repository
- At least **4GB RAM** and **10GB disk space**

### Instant Setup

```bash
# Clone the repository
git clone https://github.com/adamcodes716/fentix.git
cd fentix

# Start the entire system
docker-compose up -d

# Access the dashboard
open http://localhost:8020/dashboard
```

That's it! The system will be running in under 5 minutes.

## 🏗️ Architecture Overview

The FenixAI Docker setup consists of three main containers:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Trading Bot   │    │      Redis      │    │ Ollama Health   │
│   (Port 8020)   │◄──►│   (Port 6379)   │    │   (Health Mon)  │
│                 │    │                 │    │                 │
│ • FastAPI       │    │ • Caching       │    │ • Model Check   │
│ • Dashboard     │    │ • Session Store │    │ • AI Monitoring │
│ • AI Agents     │    │ • Trade Memory  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Container Details

| Container | Purpose | Ports | Resources |
|-----------|---------|-------|-----------|
| `fenixai-trading-bot` | Main trading application | 8020:8020 | 2GB RAM, 2 CPU |
| `fenixai-redis` | Data caching and memory | 6379:6379 | 512MB RAM |
| `fenixai-ollama-health` | AI model monitoring | Internal | 256MB RAM |

## 📋 Detailed Setup Instructions

### Step 1: Environment Configuration

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Configure your API keys in `.env`:**
   ```bash
   # Trading Configuration
   BINANCE_API_KEY=your_binance_api_key_here
   BINANCE_API_SECRET=your_binance_secret_here
   
   # AI Configuration (Optional)
   OLLAMA_HOST=192.168.1.100:11434
   OPENAI_API_KEY=your_openai_key_here
   ```

### Step 2: Build and Start Services

#### Development Mode
```bash
# Build and start with logs visible
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

#### Production Mode
```bash
# Use optimized production build
docker-compose -f docker-compose.yml up -d --build
```

### Step 3: Verify Installation

1. **Check container status:**
   ```bash
   docker-compose ps
   ```

2. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f fenixai-trading-bot
   ```

3. **Test the system:**
   ```bash
   curl http://localhost:8020/health
   ```

## 🎛️ Docker Management Commands

### Essential Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View real-time logs
docker-compose logs -f

# Update and rebuild
docker-compose down && docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v --remove-orphans
```

### Troubleshooting Commands

```bash
# Check container status
docker-compose ps

# Inspect specific container
docker inspect fenixai-trading-bot

# Execute commands inside container
docker exec -it fenixai-trading-bot bash

# View container resource usage
docker stats

# Check Docker system info
docker system df
docker system prune  # Clean up unused resources
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BINANCE_API_KEY` | Required | Your Binance API key |
| `BINANCE_API_SECRET` | Required | Your Binance API secret |
| `OLLAMA_HOST` | `localhost:11434` | Ollama server address |
| `REDIS_URL` | `redis://fenixai-redis:6379` | Redis connection |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `TRADING_MODE` | `paper` | Trading mode (paper/live) |

### Volume Mounts

```yaml
volumes:
  - ./logs:/app/logs              # Trading logs
  - ./cache:/app/cache            # Cache data
  - ./memory:/app/memory          # Trade memory
  - ./.env:/app/.env              # Environment config
```

### Port Configuration

```yaml
ports:
  - "8020:8020"  # Dashboard and API
  - "6379:6379"  # Redis (optional external access)
```

## 🚀 Advanced Features

### Multi-Stage Builds

The Dockerfile uses multi-stage builds for optimization:

1. **Builder Stage**: Compiles dependencies
2. **Production Stage**: Minimal runtime image
3. **Security**: Non-root user execution
4. **Optimization**: Layer caching and size reduction

### Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8020/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Auto-restart Policies

```yaml
restart: unless-stopped  # Automatic restart on failure
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs for errors
docker-compose logs fenixai-trading-bot

# Common fixes:
docker-compose down
docker system prune -f
docker-compose up -d --build
```

#### 2. Permission Issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER ./logs ./cache ./memory
```

#### 3. Port Already in Use
```bash
# Check what's using port 8020
netstat -tulpn | grep 8020

# Kill process or change port in docker-compose.yml
```

#### 4. API Key Issues
```bash
# Verify .env file
cat .env | grep BINANCE

# Test API connection
docker exec fenixai-trading-bot python -c "
from config.config_loader import ConfigLoader
config = ConfigLoader()
print('API Key configured:', bool(config.binance.api_key))
"
```

### Log Analysis

```bash
# Monitor all logs in real-time
docker-compose logs -f --tail=100

# Filter for errors only
docker-compose logs | grep -i error

# Export logs to file
docker-compose logs > fenixai-logs-$(date +%Y%m%d).log
```

## 📊 Monitoring and Maintenance

### Health Monitoring

1. **Dashboard Health**: `http://localhost:8020/health`
2. **System Metrics**: `http://localhost:8020/api/metrics`
3. **Prometheus Metrics**: `http://localhost:8020/api/prometheus`

### Regular Maintenance

```bash
# Weekly cleanup
docker system prune -f

# Update images
docker-compose pull
docker-compose up -d --build

# Backup important data
tar -czf fenixai-backup-$(date +%Y%m%d).tar.gz \
  ./logs ./cache ./memory ./.env
```

### Resource Monitoring

```bash
# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check disk usage
docker system df
```

## 🔒 Security Best Practices

### 1. Environment Security
- Never commit `.env` files to version control
- Use strong, unique API keys
- Regularly rotate credentials

### 2. Container Security
- Containers run as non-root user (`fenixai`)
- Minimal base images (Python slim)
- Regular dependency updates

### 3. Network Security
- Internal container communication
- Expose only necessary ports
- Use Docker secrets for sensitive data

## 🚀 Production Deployment

### Recommended Setup

```bash
# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Enable log rotation
docker-compose exec fenixai-trading-bot logrotate /etc/logrotate.conf

# Set up monitoring
docker-compose exec fenixai-trading-bot pip install prometheus_client
```

### Performance Optimization

1. **Resource Limits**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
         cpus: '1.0'
   ```

2. **Persistent Volumes**:
   ```yaml
   volumes:
     fenixai-data:
       driver: local
   ```

## 📚 Additional Resources

- **Dashboard Guide**: See `/docs/DASHBOARD_GUIDE.md`
- **API Documentation**: `http://localhost:8020/docs`
- **Architecture Overview**: `/docs/ARCHITECTURE.md`
- **Troubleshooting**: `/docs/FIXES_SUMMARY.md`

## 🆘 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs: `docker-compose logs -f`
3. Verify configuration: `curl http://localhost:8020/health`
4. Create an issue on GitHub with logs and system info

---

**Next Steps**: After setup, check out the [Dashboard Guide](./DASHBOARD_GUIDE.md) to learn how to use the trading interface.
