# config/config_loader_enhanced.py
"""
Enhanced configuration loader with environment-first approach
Prioritizes environment variables over YAML configuration
"""
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings
from typing import List, Optional

logger = logging.getLogger(__name__)

def load_env_variables():
    """Load environment variables from .env files in order of preference"""
    possible_paths = [
        Path(__file__).parent.parent / ".env",  # Project root
        Path.cwd() / ".env",                    # Current working directory
        Path(".env")                            # Relative path
    ]
    
    loaded_from = None
    for env_path in possible_paths:
        if env_path.exists():
            load_dotenv(env_path, override=True)
            loaded_from = env_path
            logger.info(f"Loaded environment variables from: {env_path}")
            break
    
    if not loaded_from:
        logger.warning("No .env file found. Using system environment variables only.")
    
    return loaded_from is not None

# Load environment variables immediately
load_env_variables()

class OllamaConfig(BaseModel):
    """Ollama service configuration"""
    base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    timeout: int = Field(default_factory=lambda: int(os.getenv("OLLAMA_TIMEOUT", "120")))
    max_retries: int = Field(default_factory=lambda: int(os.getenv("OLLAMA_MAX_RETRIES", "3")))
    retry_delay: float = Field(default_factory=lambda: float(os.getenv("OLLAMA_RETRY_DELAY", "2.0")))
    health_check_enabled: bool = Field(default_factory=lambda: os.getenv("OLLAMA_HEALTH_CHECK_ENABLED", "true").lower() == "true")
    health_check_interval: int = Field(default_factory=lambda: int(os.getenv("OLLAMA_HEALTH_CHECK_INTERVAL", "300")))

    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('base_url must start with http:// or https://')
        return v.rstrip('/')

class TradingConfig(BaseModel):
    """Trading configuration with environment variable support"""
    symbol: str = Field(default_factory=lambda: os.getenv("TRADING_SYMBOL", "SOLUSDT"))
    timeframe: str = Field(default_factory=lambda: os.getenv("TRADING_TIMEFRAME", "5m"))
    use_testnet: bool = Field(default_factory=lambda: os.getenv("TRADING_USE_TESTNET", "true").lower() == "true")
    min_candles_for_bot_start: int = Field(default_factory=lambda: int(os.getenv("TRADING_MIN_CANDLES_FOR_START", "51")))
    trade_cooldown_after_close_seconds: int = Field(default_factory=lambda: int(os.getenv("TRADING_COOLDOWN_AFTER_CLOSE", "60")))
    sentiment_refresh_cooldown_seconds: int = Field(default_factory=lambda: int(os.getenv("TRADING_SENTIMENT_REFRESH_COOLDOWN", "600")))
    order_status_max_retries: int = Field(default_factory=lambda: int(os.getenv("TRADING_ORDER_STATUS_MAX_RETRIES", "7")))
    order_status_initial_delay: float = Field(default_factory=lambda: float(os.getenv("TRADING_ORDER_STATUS_INITIAL_DELAY", "0.5")))

class BinanceConfig(BaseModel):
    """Binance API configuration"""
    api_key: str = Field(default_factory=lambda: os.getenv("BINANCE_API_KEY", ""))
    api_secret: str = Field(default_factory=lambda: os.getenv("BINANCE_API_SECRET", ""))

    def __init__(self, **data):
        super().__init__(**data)
        if not self.api_key or not self.api_secret:
            logger.warning("Binance API credentials not found in environment variables")

class RiskManagementConfig(BaseModel):
    """Risk management configuration"""
    base_risk_per_trade: float = Field(default_factory=lambda: float(os.getenv("RISK_BASE_PER_TRADE", "0.02")))
    max_risk_per_trade: float = Field(default_factory=lambda: float(os.getenv("RISK_MAX_PER_TRADE", "0.04")))
    min_risk_per_trade: float = Field(default_factory=lambda: float(os.getenv("RISK_MIN_PER_TRADE", "0.005")))
    atr_sl_multiplier: float = Field(default_factory=lambda: float(os.getenv("RISK_ATR_SL_MULTIPLIER", "1.5")))
    atr_tp_multiplier: float = Field(default_factory=lambda: float(os.getenv("RISK_ATR_TP_MULTIPLIER", "2.0")))
    min_reward_risk_ratio: float = Field(default_factory=lambda: float(os.getenv("RISK_MIN_REWARD_RISK_RATIO", "1.5")))
    target_reward_risk_ratio: float = Field(default_factory=lambda: float(os.getenv("RISK_TARGET_REWARD_RISK_RATIO", "2.0")))
    max_daily_loss_pct: float = Field(default_factory=lambda: float(os.getenv("RISK_MAX_DAILY_LOSS_PCT", "0.05")))
    max_consecutive_losses: int = Field(default_factory=lambda: int(os.getenv("RISK_MAX_CONSECUTIVE_LOSSES", "6")))
    max_trades_per_day: int = Field(default_factory=lambda: int(os.getenv("RISK_MAX_TRADES_PER_DAY", "60")))

class LLMConfig(BaseModel):
    """LLM configuration"""
    default_timeout: int = Field(default_factory=lambda: int(os.getenv("LLM_DEFAULT_TIMEOUT", "90")))
    default_temperature: float = Field(default_factory=lambda: float(os.getenv("LLM_DEFAULT_TEMPERATURE", "0.15")))
    default_max_tokens: int = Field(default_factory=lambda: int(os.getenv("LLM_DEFAULT_MAX_TOKENS", "1500")))

class NewsScraperConfig(BaseModel):
    """News scraper configuration"""
    cryptopanic_api_tokens: List[str] = Field(default_factory=lambda: [
        token.strip() for token in os.getenv("CRYPTOPANIC_TOKENS", "").split(",") 
        if token.strip()
    ])

class ChartGeneratorConfig(BaseModel):
    """Chart generator configuration"""
    save_charts_to_disk: bool = Field(default_factory=lambda: os.getenv("CHART_SAVE_TO_DISK", "true").lower() == "true")
    charts_dir: str = Field(default_factory=lambda: os.getenv("CHART_DIRECTORY", "logs/charts"))

class ToolsConfig(BaseModel):
    """Tools configuration"""
    news_scraper: NewsScraperConfig = Field(default_factory=NewsScraperConfig)
    chart_generator: ChartGeneratorConfig = Field(default_factory=ChartGeneratorConfig)

class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: str = Field(default_factory=lambda: os.getenv("LOG_FILE", "logs/fenix_live_trading.log"))

class TechnicalToolsConfig(BaseModel):
    """Technical analysis tools configuration"""
    maxlen_buffer: int = Field(default_factory=lambda: int(os.getenv("TECHNICAL_MAXLEN_BUFFER", "100")))
    min_candles_for_reliable_calc: int = Field(default_factory=lambda: int(os.getenv("TECHNICAL_MIN_CANDLES_FOR_CALC", "51")))

class DevelopmentConfig(BaseModel):
    """Development and synchronization configuration"""
    original_repo_url: str = Field(default_factory=lambda: os.getenv("ORIGINAL_REPO_URL", "https://github.com/Ganador1/FenixAI_tradingBot.git"))
    auto_sync_enabled: bool = Field(default_factory=lambda: os.getenv("AUTO_SYNC_ENABLED", "false").lower() == "true")
    sync_branch: str = Field(default_factory=lambda: os.getenv("SYNC_BRANCH", "main"))

class EnhancedAppConfig(BaseModel):
    """Enhanced application configuration with environment-first approach"""
    # Core configurations
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    trading: TradingConfig = Field(default_factory=TradingConfig)
    binance: BinanceConfig = Field(default_factory=BinanceConfig)
    risk_management: RiskManagementConfig = Field(default_factory=RiskManagementConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tools: ToolsConfig = Field(default_factory=ToolsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    technical_tools: TechnicalToolsConfig = Field(default_factory=TechnicalToolsConfig)
    development: DevelopmentConfig = Field(default_factory=DevelopmentConfig)

def merge_yaml_config(config: EnhancedAppConfig, yaml_config: dict) -> EnhancedAppConfig:
    """Merge YAML configuration with environment-based config (env takes precedence)"""
    try:
        # Only update fields that weren't explicitly set via environment variables
        # This preserves the environment-first approach
        
        # For now, we'll keep the environment variables as the primary source
        # YAML can serve as documentation and fallback for missing env vars
        logger.info("YAML configuration loaded as fallback (environment variables take precedence)")
        return config
    except Exception as e:
        logger.warning(f"Error merging YAML configuration: {e}")
        return config

def create_enhanced_app_config() -> EnhancedAppConfig:
    """Create enhanced application configuration with environment-first approach"""
    try:
        # Create config from environment variables first
        config = EnhancedAppConfig()
        
        # Try to load YAML config as fallback/documentation
        config_path = Path(__file__).parent / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f) or {}
                config = merge_yaml_config(config, yaml_config)
                logger.info(f"Loaded YAML configuration from: {config_path}")
            except Exception as e:
                logger.warning(f"Error loading YAML configuration: {e}")
        
        # Validate critical configurations
        if not config.binance.api_key or not config.binance.api_secret:
            if not config.trading.use_testnet:
                raise ValueError(
                    "Binance API credentials are required for live trading. "
                    "Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables."
                )
            else:
                logger.warning("Binance API credentials not set. Continuing with testnet mode.")
        
        logger.info(f"Enhanced configuration loaded successfully:")
        logger.info(f"  - Ollama Base URL: {config.ollama.base_url}")
        logger.info(f"  - Trading Symbol: {config.trading.symbol}")
        logger.info(f"  - Trading Timeframe: {config.trading.timeframe}")
        logger.info(f"  - Use Testnet: {config.trading.use_testnet}")
        logger.info(f"  - Log Level: {config.logging.level}")
        
        return config
        
    except Exception as e:
        logger.error(f"Error creating enhanced configuration: {e}")
        raise

# Create the global enhanced configuration
try:
    ENHANCED_APP_CONFIG = create_enhanced_app_config()
except Exception as e:
    logger.error(f"Failed to create enhanced app configuration: {e}")
    # Fall back to basic configuration if needed
    raise

# Backward compatibility with existing code
APP_CONFIG = ENHANCED_APP_CONFIG

if __name__ == "__main__":
    print("Enhanced Configuration Test")
    print("=" * 50)
    
    config = create_enhanced_app_config()
    
    print(f"Ollama Base URL: {config.ollama.base_url}")
    print(f"Ollama Timeout: {config.ollama.timeout}s")
    print(f"Trading Symbol: {config.trading.symbol}")
    print(f"Trading Timeframe: {config.trading.timeframe}")
    print(f"Use Testnet: {config.trading.use_testnet}")
    print(f"Log Level: {config.logging.level}")
    print(f"Health Check Enabled: {config.ollama.health_check_enabled}")
    
    if config.binance.api_key:
        print(f"Binance API Key: {'*' * 20}...")
    else:
        print("Binance API Key: Not configured")
