#!/usr/bin/env python3
"""
Environment setup and validation script for FenixAI
"""

import os
import sys
import shutil
from pathlib import Path
import subprocess
import requests
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_status(message, status="INFO"):
    """Print a status message"""
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    icon = icons.get(status, "ℹ️")
    print(f"{icon} {message}")

def check_env_file():
    """Check if .env file exists and offer to create it"""
    print_header("Environment File Check")
    
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print_status(f".env file found at: {env_path.absolute()}", "SUCCESS")
        return True
    
    if env_example_path.exists():
        print_status(".env file not found, but .env.example exists", "WARNING")
        
        create_env = input("\n📝 Do you want to create .env from .env.example? (y/n): ").lower().strip()
        
        if create_env in ['y', 'yes']:
            try:
                shutil.copy(env_example_path, env_path)
                print_status(f"Created .env file from template", "SUCCESS")
                print_status("Please edit .env file with your actual configuration values", "INFO")
                return True
            except Exception as e:
                print_status(f"Error creating .env file: {e}", "ERROR")
                return False
        else:
            print_status("Continuing without .env file", "WARNING")
            return False
    else:
        print_status("Neither .env nor .env.example found", "ERROR")
        return False

def validate_ollama_connection():
    """Validate connection to Ollama service"""
    print_header("Ollama Connection Validation")
    
    # Try to import our enhanced config
    try:
        sys.path.append('.')
        from config.config_loader_enhanced import create_enhanced_app_config
        from config.ollama_client import create_ollama_client
        
        config = create_enhanced_app_config()
        ollama_client = create_ollama_client(config)
        
        print_status(f"Ollama Base URL: {config.ollama.base_url}", "INFO")
        print_status(f"Connection Timeout: {config.ollama.timeout}s", "INFO")
        print_status(f"Health Checks: {'Enabled' if config.ollama.health_check_enabled else 'Disabled'}", "INFO")
        
        # Test connection
        status = ollama_client.check_health(force=True)
        
        if status.is_healthy:
            print_status(f"Ollama connection successful ({status.response_time_ms:.1f}ms)", "SUCCESS")
            
            if status.available_models:
                print_status(f"Found {len(status.available_models)} available models:", "SUCCESS")
                for i, model in enumerate(status.available_models[:10]):  # Show first 10
                    print(f"   {i+1:2}. {model}")
                if len(status.available_models) > 10:
                    print(f"   ... and {len(status.available_models) - 10} more models")
            else:
                print_status("No models found - you may need to pull some models", "WARNING")
                
            return True
        else:
            print_status(f"Ollama connection failed: {status.error_message}", "ERROR")
            print_status("Troubleshooting tips:", "INFO")
            print("   1. Check if Ollama is running on the target server")
            print("   2. Verify the OLLAMA_BASE_URL in your .env file")
            print("   3. Check network connectivity and firewall settings")
            print("   4. For remote Ollama, ensure it's bound to 0.0.0.0:11434")
            return False
            
    except ImportError as e:
        print_status(f"Cannot import configuration modules: {e}", "ERROR")
        return False
    except Exception as e:
        print_status(f"Error validating Ollama connection: {e}", "ERROR")
        return False

def validate_binance_config():
    """Validate Binance API configuration"""
    print_header("Binance API Configuration")
    
    try:
        from config.config_loader_enhanced import ENHANCED_APP_CONFIG
        
        binance_config = ENHANCED_APP_CONFIG.binance
        trading_config = ENHANCED_APP_CONFIG.trading
        
        if trading_config.use_testnet:
            print_status("Testnet mode enabled - API keys optional", "INFO")
        else:
            print_status("Live trading mode - API keys required", "WARNING")
        
        if binance_config.api_key and binance_config.api_secret:
            print_status("Binance API credentials configured", "SUCCESS")
            print_status(f"API Key: {binance_config.api_key[:8]}...{binance_config.api_key[-4:]}", "INFO")
        else:
            if trading_config.use_testnet:
                print_status("Binance API credentials not set (OK for testnet)", "WARNING")
            else:
                print_status("Binance API credentials missing (Required for live trading)", "ERROR")
                return False
        
        return True
        
    except Exception as e:
        print_status(f"Error validating Binance configuration: {e}", "ERROR")
        return False

def validate_dependencies():
    """Check if required Python packages are installed"""
    print_header("Python Dependencies Check")
    
    required_packages = [
        'crewai', 'openai', 'instructor', 'pydantic', 'pydantic-settings',
        'python-dotenv', 'requests', 'pandas', 'numpy', 'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_status(f"{package}: Installed", "SUCCESS")
        except ImportError:
            print_status(f"{package}: Missing", "ERROR")
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
        print_status("Run: pip install -r requirements.txt", "INFO")
        return False
    
    return True

def show_configuration_summary():
    """Show current configuration summary"""
    print_header("Configuration Summary")
    
    try:
        from config.config_loader_enhanced import ENHANCED_APP_CONFIG
        
        config = ENHANCED_APP_CONFIG
        
        print("🔧 Core Settings:")
        print(f"   Ollama URL: {config.ollama.base_url}")
        print(f"   Trading Symbol: {config.trading.symbol}")
        print(f"   Timeframe: {config.trading.timeframe}")
        print(f"   Testnet Mode: {config.trading.use_testnet}")
        print(f"   Log Level: {config.logging.level}")
        
        print("\n⚡ Performance Settings:")
        print(f"   LLM Timeout: {config.llm.default_timeout}s")
        print(f"   Ollama Timeout: {config.ollama.timeout}s")
        print(f"   Health Checks: {config.ollama.health_check_enabled}")
        
        print("\n🛡️ Risk Management:")
        print(f"   Base Risk/Trade: {config.risk_management.base_risk_per_trade:.1%}")
        print(f"   Max Risk/Trade: {config.risk_management.max_risk_per_trade:.1%}")
        print(f"   Max Daily Loss: {config.risk_management.max_daily_loss_pct:.1%}")
        
        print("\n📊 Features:")
        print(f"   Chart Generation: {config.tools.chart_generator.save_charts_to_disk}")
        print(f"   Charts Directory: {config.tools.chart_generator.charts_dir}")
        
        return True
        
    except Exception as e:
        print_status(f"Error showing configuration: {e}", "ERROR")
        return False

def suggest_model_downloads():
    """Suggest downloading required models"""
    print_header("Model Download Suggestions")
    
    # Original project's preferred models (that are actually available on your server)
    original_project_models = [
        "granite3.2-vision:latest",  # ✅ Available on your server 
        "phi4-mini:3.8b",           # ✅ Available on your server
        "llama3.2:3b",              # ✅ Available (closest to original llama3.2:1b)
        "cogito:8b",                # ✅ Available on your server
    ]
    
    # Additional recommended models to complement the original setup
    additional_models = [
        "qwen2.5:0.5b",     # Lightweight sentiment analysis
        "qwen2.5:7b",       # General fallback
    ]
    
    print_status("✅ Original project models already on your server:", "SUCCESS") 
    for i, model in enumerate(original_project_models, 1):
        print(f"   {i}. {model}")
    
    print_status("\n💡 Additional models you might want to download:", "INFO")
    for i, model in enumerate(additional_models, 1):
        print(f"   {i}. {model}")
    
    print("\n📥 To download additional models:")
    for model in additional_models:
        print(f"   ollama pull {model}")
    
    print("\n🎉 Good news: Your server already has most of the original project's preferred models!")
    print("💡 Note: Run downloads on your Ollama server at 192.168.1.100")

def main():
    """Main setup and validation function"""
    print_header("FenixAI Environment Setup & Validation")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    total_checks = 5
    
    # Run all validation checks
    checks = [
        ("Environment File", check_env_file),
        ("Python Dependencies", validate_dependencies),
        ("Ollama Connection", validate_ollama_connection),
        ("Binance Configuration", validate_binance_config),
        ("Configuration Summary", show_configuration_summary)
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 Running {check_name} check...")
        if check_func():
            success_count += 1
    
    # Final summary
    print_header("Setup Summary")
    
    if success_count == total_checks:
        print_status(f"All checks passed! ({success_count}/{total_checks})", "SUCCESS")
        print_status("FenixAI is ready to run!", "SUCCESS")
        print("\n🚀 Next steps:")
        print("   1. Review your .env file configuration")
        print("   2. Ensure required models are available on your Ollama server")
        print("   3. Run: python run_paper_trading.py")
    else:
        print_status(f"Some checks failed ({success_count}/{total_checks})", "WARNING")
        print_status("Please address the issues above before running FenixAI", "WARNING")
    
    suggest_model_downloads()

if __name__ == "__main__":
    main()
