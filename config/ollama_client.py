# config/ollama_client.py
"""
Abstracted Ollama client with health checks and connection management
Supports both local and remote Ollama services
"""
import asyncio
import logging
import time
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class OllamaHealthStatus:
    """Health status information for Ollama service"""
    is_healthy: bool
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    available_models: List[str] = None

class OllamaClient:
    """
    Enhanced Ollama client with health monitoring and connection management
    """
    
    def __init__(self, config):
        """
        Initialize Ollama client with configuration
        
        Args:
            config: Configuration object with ollama settings
        """
        self.config = config
        self.base_url = config.ollama.base_url
        self.timeout = config.ollama.timeout
        self.max_retries = config.ollama.max_retries
        self.retry_delay = config.ollama.retry_delay
        self.health_check_enabled = config.ollama.health_check_enabled
        self.health_check_interval = config.ollama.health_check_interval
        
        # Health monitoring
        self._last_health_check: Optional[datetime] = None
        self._health_status: Optional[OllamaHealthStatus] = None
        self._consecutive_failures = 0
        
        logger.info(f"Ollama client initialized with base URL: {self.base_url}")
    
    def get_api_url(self, endpoint: str = "") -> str:
        """Get full API URL for a given endpoint"""
        base = self.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base}/api/{endpoint}" if endpoint else f"{base}/api"
    
    def get_v1_url(self, endpoint: str = "") -> str:
        """Get OpenAI-compatible v1 API URL"""
        base = self.base_url.rstrip('/')
        endpoint = endpoint.lstrip('/')
        return f"{base}/v1/{endpoint}" if endpoint else f"{base}/v1"
    
    def check_health(self, force: bool = False) -> OllamaHealthStatus:
        """
        Check Ollama service health
        
        Args:
            force: Force health check even if recently checked
            
        Returns:
            OllamaHealthStatus object with current status
        """
        now = datetime.now()
        
        # Return cached status if recently checked and not forced
        if (not force and 
            self._last_health_check and 
            self._health_status and
            (now - self._last_health_check).seconds < self.health_check_interval):
            return self._health_status
        
        start_time = time.time()
        
        try:
            # Try to get version info (lightweight endpoint)
            response = requests.get(
                f"{self.base_url}/api/version",
                timeout=min(self.timeout, 10)  # Use shorter timeout for health checks
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # Try to get available models
                models = self._get_available_models()
                
                self._health_status = OllamaHealthStatus(
                    is_healthy=True,
                    response_time_ms=response_time_ms,
                    last_check=now,
                    available_models=models
                )
                self._consecutive_failures = 0
                
                logger.debug(f"Ollama health check passed ({response_time_ms:.1f}ms)")
                
            else:
                raise requests.RequestException(f"HTTP {response.status_code}")
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            self._consecutive_failures += 1
            
            self._health_status = OllamaHealthStatus(
                is_healthy=False,
                response_time_ms=response_time_ms,
                last_check=now,
                error_message=str(e)
            )
            
            logger.warning(f"Ollama health check failed: {e} (consecutive failures: {self._consecutive_failures})")
        
        self._last_health_check = now
        return self._health_status
    
    def _get_available_models(self) -> List[str]:
        """Get list of available models from Ollama"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=min(self.timeout, 15)
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [model.get('name', '') for model in data.get('models', [])]
                return [model for model in models if model]
            else:
                logger.warning(f"Failed to get model list: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Error getting available models: {e}")
            return []
    
    def is_healthy(self) -> bool:
        """Quick health check"""
        if not self.health_check_enabled:
            return True
            
        status = self.check_health()
        return status.is_healthy
    
    def ensure_healthy(self) -> bool:
        """
        Ensure Ollama service is healthy, with retries
        
        Returns:
            True if service is healthy, False otherwise
        """
        if not self.health_check_enabled:
            return True
        
        for attempt in range(self.max_retries):
            status = self.check_health(force=True)
            
            if status.is_healthy:
                return True
            
            if attempt < self.max_retries - 1:
                logger.info(f"Ollama health check failed, retrying in {self.retry_delay}s... (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
        
        logger.error(f"Ollama service unhealthy after {self.max_retries} attempts")
        return False
    
    def get_health_status(self) -> Optional[OllamaHealthStatus]:
        """Get current health status (cached)"""
        return self._health_status
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information and status"""
        status = self.check_health()
        
        return {
            "base_url": self.base_url,
            "api_url": self.get_api_url(),
            "v1_url": self.get_v1_url(),
            "timeout": self.timeout,
            "health_check_enabled": self.health_check_enabled,
            "is_healthy": status.is_healthy if status else False,
            "response_time_ms": status.response_time_ms if status else None,
            "last_check": status.last_check.isoformat() if status and status.last_check else None,
            "available_models": status.available_models if status else [],
            "consecutive_failures": self._consecutive_failures,
            "error_message": status.error_message if status else None
        }
    
    def validate_model_availability(self, model_name: str) -> bool:
        """
        Check if a specific model is available
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model is available, False otherwise
        """
        if not self.is_healthy():
            logger.warning(f"Cannot validate model '{model_name}' - Ollama service unhealthy")
            return False
        
        status = self.get_health_status()
        if not status or not status.available_models:
            logger.warning(f"Cannot validate model '{model_name}' - no model list available")
            return False
        
        # Check for exact match or partial match (for different tags)
        available = status.available_models
        exact_match = model_name in available
        partial_match = any(model_name.split(':')[0] in model for model in available)
        
        if exact_match:
            logger.debug(f"Model '{model_name}' found (exact match)")
            return True
        elif partial_match:
            logger.debug(f"Model '{model_name}' found (partial match)")
            return True
        else:
            logger.warning(f"Model '{model_name}' not found in available models: {available}")
            return False

def create_ollama_client(config) -> OllamaClient:
    """
    Factory function to create and validate Ollama client
    
    Args:
        config: Application configuration object
        
    Returns:
        Configured and validated OllamaClient instance
    """
    client = OllamaClient(config)
    
    # Perform initial health check if enabled
    if client.health_check_enabled:
        logger.info("Performing initial Ollama health check...")
        if client.ensure_healthy():
            logger.info("✅ Ollama service is healthy and ready")
            
            # Log available models
            status = client.get_health_status()
            if status and status.available_models:
                logger.info(f"Available models: {', '.join(status.available_models[:5])}{'...' if len(status.available_models) > 5 else ''}")
        else:
            logger.error("❌ Ollama service is not healthy")
            logger.error("Please check:")
            logger.error(f"  1. Ollama is running at {client.base_url}")
            logger.error("  2. Network connectivity to the Ollama service")
            logger.error("  3. Firewall settings if using remote Ollama")
    else:
        logger.info("Health checks disabled, assuming Ollama is available")
    
    return client

if __name__ == "__main__":
    # Test the Ollama client
    from config_loader_enhanced import create_enhanced_app_config
    
    print("Testing Ollama Client")
    print("=" * 50)
    
    try:
        config = create_enhanced_app_config()
        client = create_ollama_client(config)
        
        print(f"Base URL: {client.base_url}")
        print(f"Health Check Enabled: {client.health_check_enabled}")
        
        # Test health check
        status = client.check_health(force=True)
        print(f"Health Status: {'✅ Healthy' if status.is_healthy else '❌ Unhealthy'}")
        print(f"Response Time: {status.response_time_ms:.1f}ms")
        
        if status.error_message:
            print(f"Error: {status.error_message}")
        
        if status.available_models:
            print(f"Available Models: {len(status.available_models)} models")
            for model in status.available_models[:5]:  # Show first 5
                print(f"  - {model}")
            if len(status.available_models) > 5:
                print(f"  ... and {len(status.available_models) - 5} more")
        
        # Test connection info
        print("\nConnection Info:")
        info = client.get_connection_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"Error testing Ollama client: {e}")
        import traceback
        traceback.print_exc()
