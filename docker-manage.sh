#!/bin/bash
# FenixAI Docker Management Script
# Simplified container management for development and production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
SERVICE_NAME="fenixai"
OLLAMA_URL="http://192.168.1.100:11434"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log_success "Docker is running"
}

# Check Ollama connectivity
check_ollama() {
    log_info "Checking Ollama server connectivity at $OLLAMA_URL..."
    if curl -f "$OLLAMA_URL/api/version" > /dev/null 2>&1; then
        log_success "Ollama server is accessible"
        return 0
    else
        log_error "Ollama server at $OLLAMA_URL is not accessible"
        log_warning "Please ensure:"
        echo "  1. Ollama is running on 192.168.1.100"
        echo "  2. Port 11434 is accessible from this machine"
        echo "  3. No firewall is blocking the connection"
        return 1
    fi
}

# Check model availability
check_models() {
    log_info "Checking required models on Ollama server..."
    python3 -c "
import sys
sys.path.append('.')
from config.modern_models import print_model_availability_guide
print_model_availability_guide()
" 2>/dev/null || {
    log_warning "Could not check models via Python script. Checking directly..."
    curl -s "$OLLAMA_URL/api/tags" | python3 -c "
import json, sys
data = json.load(sys.stdin)
models = [m['name'] for m in data.get('models', [])]
required = ['qwen2.5:7b-instruct-q5_k_m', 'qwen2.5vl:7b-q4_K_M', 'adrienbrault/nous-hermes2pro-llama3-8b:q4_K_M']
print(f'Available models: {len(models)}')
for req in required:
    status = '✅' if req in models else '❌'
    print(f'{status} {req}')
"
}
}

# Build the Docker image
build() {
    log_info "Building FenixAI Docker image..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    log_success "Docker image built successfully"
}

# Start services
start() {
    check_docker
    check_ollama || {
        log_error "Cannot start without Ollama connectivity"
        exit 1
    }
    
    log_info "Starting FenixAI services..."
    docker-compose -f $COMPOSE_FILE up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    if docker-compose -f $COMPOSE_FILE ps | grep -q "Up (healthy)"; then
        log_success "FenixAI services started successfully"
        show_status
    else
        log_warning "Services started but health check may have failed"
        show_logs
    fi
}

# Stop services
stop() {
    log_info "Stopping FenixAI services..."
    docker-compose -f $COMPOSE_FILE down
    log_success "Services stopped"
}

# Show service status
show_status() {
    echo ""
    log_info "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Show logs
show_logs() {
    echo ""
    log_info "Recent logs from $SERVICE_NAME:"
    docker-compose -f $COMPOSE_FILE logs --tail=50 $SERVICE_NAME
}

# Follow logs
follow_logs() {
    log_info "Following logs from $SERVICE_NAME (Ctrl+C to exit):"
    docker-compose -f $COMPOSE_FILE logs -f $SERVICE_NAME
}

# Restart services
restart() {
    log_info "Restarting FenixAI services..."
    stop
    sleep 3
    start
}

# Clean up everything
clean() {
    log_warning "This will remove all containers, images, and volumes. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "Cleaning up Docker resources..."
        docker-compose -f $COMPOSE_FILE down -v --rmi all
        docker system prune -f
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Run a command inside the container
run_command() {
    if [ $# -eq 0 ]; then
        log_error "No command specified"
        exit 1
    fi
    
    log_info "Executing command in $SERVICE_NAME container: $*"
    docker-compose -f $COMPOSE_FILE exec $SERVICE_NAME "$@"
}

# Development mode with code mounting
dev() {
    log_info "Starting in development mode with live code reloading..."
    check_docker
    check_ollama || {
        log_error "Cannot start without Ollama connectivity"
        exit 1
    }
    
    # Create a development override file
    cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  fenixai:
    volumes:
      - ./:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    command: ["python", "-m", "watchdog.main", "--patterns", "*.py", "--recursive", "--restart-command", "python paper_trading_demo.py"]
EOF
    
    docker-compose -f $COMPOSE_FILE -f docker-compose.override.yml up
}

# Show help
show_help() {
    echo "FenixAI Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show recent logs"
    echo "  follow      Follow logs in real-time"
    echo "  run <cmd>   Run a command inside the container"
    echo "  dev         Start in development mode"
    echo "  clean       Remove all containers, images, and volumes"
    echo "  check       Check system requirements"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 start"
    echo "  $0 run python paper_trading_demo.py"
    echo "  $0 dev"
}

# Check system requirements
check_system() {
    log_info "Checking system requirements..."
    check_docker
    check_ollama
    check_models
    log_success "System check completed"
}

# Main script logic
case "${1:-help}" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    follow)
        follow_logs
        ;;
    run)
        shift
        run_command "$@"
        ;;
    dev)
        dev
        ;;
    clean)
        clean
        ;;
    check)
        check_system
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
