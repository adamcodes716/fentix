#!/usr/bin/env python3
"""
Ollama Model Validation and Recommendation Script
Checks which models are available and suggests the best ones for FenixAI
"""

import requests
import sys
from typing import List, Dict, Any

def check_ollama_models(base_url: str = "http://192.168.1.100:11434") -> List[str]:
    """
    Check which models are available on the Ollama server
    
    Args:
        base_url: Ollama server URL
        
    Returns:
        List of available model names
    """
    try:
        response = requests.get(f"{base_url}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [model.get('name', '') for model in data.get('models', [])]
            return [model for model in models if model]
        else:
            print(f"❌ Failed to get models: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return []

def get_model_recommendations() -> Dict[str, List[str]]:
    """Get model recommendations by category"""
    return {
        "sentiment_analysis": [
            "qwen2.5:0.5b",      # Ultra lightweight
            "qwen2.5:7b",        # Good balance
            "phi3:3.8b",         # Multi-purpose
        ],
        "visual_analysis": [
            "llava:7b",          # Proven vision model
            "llava:13b",         # Better but larger
            "moondream:1.8b",    # Lightweight vision
        ],
        "technical_analysis": [
            "phi3:3.8b",         # Good for reasoning
            "qwen2.5:7b",        # General purpose
            "mixtral:8x7b",      # High quality (if you have RAM)
        ],
        "decision_making": [
            "mixtral:8x7b",      # Best reasoning
            "qwen2.5:14b",       # Good reasoning
            "phi3:3.8b",         # Lightweight option
        ],
        "general_fallback": [
            "qwen2.5:7b",        # Reliable general model
            "phi3:3.8b",         # Lightweight reliable
            "gemma2:2b",         # Ultra lightweight
        ]
    }

def recommend_models_for_system(available_models: List[str]) -> Dict[str, str]:
    """
    Recommend the best available models for each FenixAI component
    
    Args:
        available_models: List of models available on the server
        
    Returns:
        Dictionary mapping component to recommended model
    """
    recommendations = get_model_recommendations()
    selected = {}
    
    for component, model_list in recommendations.items():
        selected_model = None
        for model in model_list:
            if model in available_models:
                selected_model = model
                break
        
        if selected_model:
            selected[component] = selected_model
        else:
            selected[component] = f"❌ None available (try: {model_list[0]})"
    
    return selected

def suggest_downloads(available_models: List[str]) -> List[str]:
    """Suggest which models to download for optimal FenixAI performance"""
    recommendations = get_model_recommendations()
    
    # Find the best model from each category that's not already available
    to_download = []
    
    for component, model_list in recommendations.items():
        has_model = any(model in available_models for model in model_list)
        if not has_model:
            # Suggest the first (best) model from the list
            to_download.append(model_list[0])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_downloads = []
    for model in to_download:
        if model not in seen:
            seen.add(model)
            unique_downloads.append(model)
    
    return unique_downloads

def main():
    """Main validation and recommendation function"""
    print("🤖 FenixAI Ollama Model Validator")
    print("=" * 50)
    
    base_url = "http://192.168.1.100:11434"
    print(f"🔍 Checking Ollama server at: {base_url}")
    
    # Check available models
    available_models = check_ollama_models(base_url)
    
    if not available_models:
        print("\n❌ Could not connect to Ollama server or no models found")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Ollama is running on 192.168.1.100")
        print("   2. Ensure Ollama is bound to 0.0.0.0:11434")
        print("   3. Check firewall settings")
        print("\n💡 To start Ollama properly:")
        print("   OLLAMA_HOST=0.0.0.0:11434 ollama serve")
        return
    
    print(f"✅ Found {len(available_models)} models on server")
    
    # Show available models
    print("\n📋 Available Models:")
    for i, model in enumerate(sorted(available_models), 1):
        print(f"   {i:2}. {model}")
    
    # Get recommendations
    recommendations = recommend_models_for_system(available_models)
    
    print("\n🎯 Recommended Models for FenixAI Components:")
    for component, model in recommendations.items():
        status = "✅" if not model.startswith("❌") else "❌"
        print(f"   {status} {component.replace('_', ' ').title()}: {model}")
    
    # Suggest downloads
    to_download = suggest_downloads(available_models)
    
    if to_download:
        print(f"\n📥 Suggested models to download ({len(to_download)} models):")
        for i, model in enumerate(to_download, 1):
            print(f"   {i}. ollama pull {model}")
        
        print("\n💻 Run these commands on your Ollama server:")
        for model in to_download:
            print(f"   ollama pull {model}")
    else:
        print("\n🎉 You have all the recommended models!")
    
    print("\n📊 System Requirements Estimate:")
    total_size_gb = len([m for m in available_models if any(x in m for x in ['7b', '8b'])]) * 4
    total_size_gb += len([m for m in available_models if '13b' in m]) * 7
    total_size_gb += len([m for m in available_models if any(x in m for x in ['0.5b', '1b', '2b'])]) * 1
    
    print(f"   Estimated disk usage: ~{total_size_gb}GB")
    print(f"   Recommended RAM: {max(8, total_size_gb // 2)}GB+")

if __name__ == "__main__":
    main()
