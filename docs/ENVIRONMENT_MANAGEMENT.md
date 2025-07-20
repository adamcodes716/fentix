# Environment Management Guide

This guide explains how to use the different environment configurations for FenixAI development and deployment.

## 📁 Environment Files

### `.env.development`
- **Purpose**: Local Windows development
- **Ollama**: Expects local Ollama at `localhost:11434`
- **Trading**: Safe development settings (lower position sizes)
- **Logging**: Debug level for detailed troubleshooting
- **Features**: Debug endpoints enabled, hot reload

### `.env.production`
- **Purpose**: OMV production deployment
- **Ollama**: External server at `192.168.1.100:11434`
- **Trading**: Production-ready settings
- **Logging**: Info level for performance
- **Features**: Debug disabled, metrics enabled

## 🚀 Usage Commands

### Local Development (Windows)

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop development environment
docker-compose down

# Rebuild development image
docker-compose build
```

### Production Deployment (OMV)

```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Update production deployment
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Stop production
docker-compose -f docker-compose.prod.yml down
```

## 🔧 Environment Setup

### For Development:
1. Ensure you have local Ollama running on port 11434
2. Copy `.env.example` to `.env.development` 
3. Add your development API keys
4. Run: `docker-compose up -d`

### For Production (OMV):
1. Copy `.env.production` to your OMV data directory
2. Update with production API keys and settings
3. Ensure Ollama is accessible at `192.168.1.100:11434`
4. Run: `docker-compose -f docker-compose.prod.yml up -d`

## 📂 File Structure

```
FenixAI/
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── docker-compose.omv.yml      # OMV-specific with host paths
├── .env.development            # Development config
├── .env.production             # Production config
├── .env.example                # Template
└── .env                        # Local override (gitignored)
```

## 🔒 Security Notes

- **Never commit** actual API keys to Git
- **Development keys** should be test/sandbox keys only
- **Production keys** should have minimal required permissions
- **Environment files** are automatically excluded from Docker builds
- **Each environment** has separate data volumes

## 🎯 Key Differences

| Aspect | Development | Production |
|--------|-------------|------------|
| **Image Source** | Built locally | Pulled from Docker Hub |
| **Environment** | `.env.development` | `.env.production` |
| **Ollama** | `localhost:11434` | `192.168.1.100:11434` |
| **Code Mount** | Source code mounted | No source mount |
| **Debug Level** | DEBUG | INFO |
| **Position Size** | $100 max | $1000 max |
| **Container Names** | `*-dev` suffix | Production names |
| **Networks** | `fenixai-dev-network` | `fenixai-network` |

## 🔄 Switching Environments

### From Development to Production:
1. Build and push your image: `docker build -t adamcodes716/fenixai-trading:latest . && docker push adamcodes716/fenixai-trading:latest`
2. Copy `.env.production` to target system
3. Deploy: `docker-compose -f docker-compose.prod.yml up -d`

### Testing Production Locally:
```bash
# Use production compose with development settings
docker-compose -f docker-compose.prod.yml up -d
```

## 🚨 Troubleshooting

### Development Issues:
- **Ollama not accessible**: Ensure Ollama is running locally
- **Source changes not reflected**: Check if code mounting is working
- **Debug info missing**: Verify `.env.development` is being used

### Production Issues:
- **Image not found**: Ensure image is pushed to Docker Hub
- **Ollama connection failed**: Check external Ollama server accessibility
- **Environment not loaded**: Verify `.env.production` path in compose file

## 📈 Best Practices

1. **Always test locally** before deploying to production
2. **Use separate API keys** for each environment
3. **Monitor resource usage** in production
4. **Regular backups** of production data volumes
5. **Version your Docker images** with tags (e.g., `v1.0.0`)
6. **Document environment differences** for team members
