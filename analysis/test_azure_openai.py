#!/usr/bin/env python3
"""Test script to verify Azure OpenAI integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.config import settings
from src.llm.client import LLMClient

def test_azure_openai():
    """Test Azure OpenAI connection and basic functionality."""
    print("Testing Azure OpenAI Integration...")
    print("=" * 50)
    
    # Check configuration
    if settings.azure_openai_api_key and settings.azure_openai_endpoint:
        print("✓ Azure OpenAI credentials found")
        print(f"  Endpoint: {settings.azure_openai_endpoint}")
        print(f"  API Version: {settings.azure_openai_api_version}")
        print(f"  Deployment: {settings.azure_openai_deployment_name}")
    elif settings.openai_api_key:
        print("ℹ Using standard OpenAI (fallback)")
        print(f"  Model: {settings.openai_model}")
    else:
        print("✗ No API credentials found!")
        print("  Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env")
        return
    
    print("\nInitializing LLM client...")
    
    try:
        # Initialize client
        client = LLMClient()
        
        if client.using_azure:
            print("✓ Using Azure OpenAI")
        else:
            print("ℹ Using standard OpenAI")
        
        print(f"  Model/Deployment: {client.model}")
        
        # Test simple completion
        print("\nTesting API call...")
        response = client.generate_response(
            prompt="What is 2+2?",
            instructions="You are a helpful assistant. Answer concisely.",
            temperature=0.1
        )
        
        print("✓ API call successful!")
        print(f"  Response: {response.content}")
        print(f"  Model: {response.model}")
        if response.tokens_used:
            print(f"  Tokens: {response.tokens_used}")
        
        # Test structured output
        print("\nTesting structured output...")
        from src.features.models import ResponseFeatures
        
        response = client.generate_response(
            prompt="Analyze this feedback: 'The cultural funding programs need more transparency and better communication.'",
            instructions="Extract features from this feedback.",
            response_format=ResponseFeatures
        )
        
        print("✓ Structured output test completed!")
        print(f"  Response length: {len(response.content)} characters")
        
    except Exception as e:
        print(f"✗ Error: {type(e).__name__}: {str(e)}")
        return
    
    print("\n" + "=" * 50)
    print("✓ All tests completed successfully!")

if __name__ == "__main__":
    test_azure_openai()