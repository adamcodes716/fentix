#!/usr/bin/env python3
"""
Simple test script to verify the enhanced configuration is working
"""

import sys
import os
sys.path.append('.')

def test_config_loading():
    """Test loading the enhanced configuration"""
    print("🧪 Testing Enhanced Configuration Loading")
    print("=" * 50)
    
    try:
        # Test basic environment loading
        from config.config_loader_enhanced import create_enhanced_app_config
        
        print("✅ Successfully imported enhanced config loader")
        
        # Create configuration
        config = create_enhanced_app_config()
        
        print("✅ Successfully created enhanced configuration")
        print()
        
        # Show key configuration values
        print("📋 Configuration Summary:")
        print(f"   Ollama URL: {config.ollama.base_url}")
        print(f"   Ollama Timeout: {config.ollama.timeout}s")
        print(f"   Trading Symbol: {config.trading.symbol}")
        print(f"   Trading Timeframe: {config.trading.timeframe}")
        print(f"   Use Testnet: {config.trading.use_testnet}")
        print(f"   Log Level: {config.logging.level}")
        print(f"   Health Checks: {config.ollama.health_check_enabled}")
        print()
        
        # Test Ollama client (without health check to avoid connection error)
        print("🔧 Testing Ollama Client Setup:")
        from config.ollama_client import OllamaClient
        
        # Create client but skip health check for now
        client = OllamaClient(config)
        print(f"   Base URL: {client.base_url}")
        print(f"   API URL: {client.get_api_url()}")
        print(f"   V1 URL: {client.get_v1_url()}")
        print("✅ Ollama client created successfully")
        print()
        
        print("🎉 Enhanced configuration system is working!")
        print()
        print("📝 Notes:")
        print("   - Ollama connection will work once your server at 192.168.1.100 is running")
        print("   - All configuration is now environment-driven")
        print("   - YAML file serves as fallback/documentation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_config_loading()
    if success:
        print("\n✅ Phase 1 Implementation: SUCCESS")
    else:
        print("\n❌ Phase 1 Implementation: FAILED")
