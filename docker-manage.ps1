# FenixAI Docker Management Script (PowerShell)
# Simplified container management for Windows development and production

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Configuration
$ComposeFile = "docker-compose.yml"
$ServiceName = "fenixai"
$OllamaURL = "http://192.168.1.100:11434"

# Helper functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        Write-Success "Docker is running"
        return $true
    }
    catch {
        Write-Error "Docker is not running. Please start Docker and try again."
        return $false
    }
}

# Check Ollama connectivity
function Test-Ollama {
    Write-Info "Checking Ollama server connectivity at $OllamaURL..."
    try {
        $response = Invoke-RestMethod -Uri "$OllamaURL/api/version" -TimeoutSec 10 -ErrorAction Stop
        Write-Success "Ollama server is accessible"
        return $true
    }
    catch {
        Write-Error "Ollama server at $OllamaURL is not accessible"
        Write-Warning "Please ensure:"
        Write-Host "  1. Ollama is running on 192.168.1.100"
        Write-Host "  2. Port 11434 is accessible from this machine"
        Write-Host "  3. No firewall is blocking the connection"
        return $false
    }
}

# Check model availability
function Test-Models {
    Write-Info "Checking required models on Ollama server..."
    try {
        Push-Location $PSScriptRoot
        python -c "
import sys
sys.path.append('.')
from config.modern_models import print_model_availability_guide
print_model_availability_guide()
" 2>$null
        Pop-Location
    }
    catch {
        Write-Warning "Could not check models via Python script. Checking directly..."
        try {
            $models = Invoke-RestMethod -Uri "$OllamaURL/api/tags" -TimeoutSec 10
            $modelNames = $models.models | ForEach-Object { $_.name }
            $required = @('qwen2.5:7b-instruct-q5_k_m', 'qwen2.5vl:7b-q4_K_M', 'adrienbrault/nous-hermes2pro-llama3-8b:q4_K_M')
            
            Write-Host "Available models: $($modelNames.Count)"
            foreach ($req in $required) {
                $status = if ($modelNames -contains $req) { "✅" } else { "❌" }
                Write-Host "$status $req"
            }
        }
        catch {
            Write-Warning "Could not fetch model list from Ollama server"
        }
    }
}

# Build the Docker image
function Build-Image {
    Write-Info "Building FenixAI Docker image..."
    docker-compose -f $ComposeFile build --no-cache
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker image built successfully"
    } else {
        Write-Error "Failed to build Docker image"
        exit 1
    }
}

# Start services
function Start-Services {
    if (-not (Test-Docker)) {
        exit 1
    }
    
    if (-not (Test-Ollama)) {
        Write-Error "Cannot start without Ollama connectivity"
        exit 1
    }
    
    Write-Info "Starting FenixAI services..."
    docker-compose -f $ComposeFile up -d
    
    if ($LASTEXITCODE -eq 0) {
        # Wait for services to be healthy
        Write-Info "Waiting for services to be healthy..."
        Start-Sleep -Seconds 10
        
        $status = docker-compose -f $ComposeFile ps
        if ($status -match "Up.*healthy") {
            Write-Success "FenixAI services started successfully"
            Show-Status
        } else {
            Write-Warning "Services started but health check may have failed"
            Show-Logs
        }
    } else {
        Write-Error "Failed to start services"
        exit 1
    }
}

# Stop services
function Stop-Services {
    Write-Info "Stopping FenixAI services..."
    docker-compose -f $ComposeFile down
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Services stopped"
    }
}

# Show service status
function Show-Status {
    Write-Host ""
    Write-Info "Service Status:"
    docker-compose -f $ComposeFile ps
    
    Write-Host ""
    Write-Info "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}`t{{.CPUPerc}}`t{{.MemUsage}}`t{{.NetIO}}"
}

# Show logs
function Show-Logs {
    Write-Host ""
    Write-Info "Recent logs from ${ServiceName}:"
    docker-compose -f $ComposeFile logs --tail=50 $ServiceName
}

# Follow logs
function Follow-Logs {
    Write-Info "Following logs from ${ServiceName} (Ctrl+C to exit):"
    docker-compose -f $ComposeFile logs -f $ServiceName
}

# Restart services
function Restart-Services {
    Write-Info "Restarting FenixAI services..."
    Stop-Services
    Start-Sleep -Seconds 3
    Start-Services
}

# Clean up everything
function Clean-Resources {
    $response = Read-Host "This will remove all containers, images, and volumes. Continue? (y/N)"
    if ($response -match '^[Yy]$') {
        Write-Info "Cleaning up Docker resources..."
        docker-compose -f $ComposeFile down -v --rmi all
        docker system prune -f
        Write-Success "Cleanup completed"
    } else {
        Write-Info "Cleanup cancelled"
    }
}

# Run a command inside the container
function Invoke-ContainerCommand {
    param([string[]]$Command)
    
    if ($Command.Count -eq 0) {
        Write-Error "No command specified"
        exit 1
    }
    
    Write-Info "Executing command in ${ServiceName} container: $($Command -join ' ')"
    docker-compose -f $ComposeFile exec $ServiceName @Command
}

# Development mode with code mounting
function Start-DevMode {
    Write-Info "Starting in development mode with live code reloading..."
    
    if (-not (Test-Docker)) {
        exit 1
    }
    
    if (-not (Test-Ollama)) {
        Write-Error "Cannot start without Ollama connectivity"
        exit 1
    }
    
    # Create a development override file
    $overrideContent = @"
version: '3.8'
services:
  fenixai:
    volumes:
      - ./:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    command: ["python", "paper_trading_demo.py"]
"@
    
    $overrideContent | Out-File -FilePath "docker-compose.override.yml" -Encoding UTF8
    
    docker-compose -f $ComposeFile -f docker-compose.override.yml up
}

# Show help
function Show-Help {
    Write-Host "FenixAI Docker Management Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: .\docker-manage.ps1 [COMMAND]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build       Build the Docker image"
    Write-Host "  start       Start all services"
    Write-Host "  stop        Stop all services"
    Write-Host "  restart     Restart all services"
    Write-Host "  status      Show service status"
    Write-Host "  logs        Show recent logs"
    Write-Host "  follow      Follow logs in real-time"
    Write-Host "  run <cmd>   Run a command inside the container"
    Write-Host "  dev         Start in development mode"
    Write-Host "  clean       Remove all containers, images, and volumes"
    Write-Host "  check       Check system requirements"
    Write-Host "  help        Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\docker-manage.ps1 build"
    Write-Host "  .\docker-manage.ps1 start"
    Write-Host "  .\docker-manage.ps1 run python paper_trading_demo.py"
    Write-Host "  .\docker-manage.ps1 dev"
}

# Check system requirements
function Test-System {
    Write-Info "Checking system requirements..."
    $dockerOk = Test-Docker
    $ollamaOk = Test-Ollama
    Test-Models
    
    if ($dockerOk -and $ollamaOk) {
        Write-Success "System check completed"
    } else {
        Write-Error "System check failed"
        exit 1
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "build" {
        Build-Image
    }
    "start" {
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    "restart" {
        Restart-Services
    }
    "status" {
        Show-Status
    }
    "logs" {
        Show-Logs
    }
    "follow" {
        Follow-Logs
    }
    "run" {
        Invoke-ContainerCommand -Command $Arguments
    }
    "dev" {
        Start-DevMode
    }
    "clean" {
        Clean-Resources
    }
    "check" {
        Test-System
    }
    default {
        if ($Command -ne "help") {
            Write-Error "Unknown command: $Command"
        }
        Show-Help
    }
}
