"""
Test a specific Bedrock Claude model ID
Usage: python test_specific_model.py "anthropic.claude-3-5-sonnet-20241022-v2:0"
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.bedrock_service import BedrockService


async def test_specific_model(model_id: str):
    """Test a specific Bedrock Claude model"""
    print("=" * 70)
    print(f"Testing Specific Bedrock Model: {model_id}")
    print("=" * 70)
    print()
    
    # Initialize Bedrock service
    bedrock_service = BedrockService()
    
    if not bedrock_service.is_available():
        print("❌ Bedrock service is not available!")
        return False
    
    print("✅ Bedrock service initialized")
    print()
    
    print(f"Testing model: {model_id}")
    print("-" * 70)
    
    try:
        result = await bedrock_service.generate_text(
            prompt="Write a short, engaging video script (2-3 sentences) about AI careers for social media.",
            system_message="You are an expert video script writer.",
            max_tokens=200,
            temperature=0.7,
            model=model_id
        )
        
        if result:
            print(f"\n✅ SUCCESS! Generated text ({len(result)} chars):")
            print(f"\n{result}\n")
            print("=" * 70)
            print(f"✅ Model {model_id} is working correctly!")
            print("=" * 70)
            return True
        else:
            print("\n❌ Failed: No text generated")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error: {error_msg}")
        
        if "AccessDeniedException" in error_msg:
            print("\n⚠️  This is a permissions issue.")
            print("   The model exists but your IAM user doesn't have permission.")
            print("   See backend/BEDROCK_SETUP.md for permission setup.")
        elif "ValidationException" in error_msg:
            print("\n⚠️  Model not found or not enabled.")
            print("   Possible reasons:")
            print("   1. Model ID is incorrect")
            print("   2. Model is not enabled in Bedrock console")
            print("   3. Model doesn't exist in this region")
        else:
            import traceback
            traceback.print_exc()
        
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        model_id = sys.argv[1]
    else:
        # Default to trying what might be "sonnet 4.5" - but this doesn't exist
        # The user might mean a specific model ID
        print("Usage: python test_specific_model.py <model_id>")
        print("\nExample: python test_specific_model.py anthropic.claude-3-5-sonnet-20241022-v2:0")
        print("\nTrying common Claude 3.5 Sonnet models...")
        print()
        
        # Try common model IDs
        models_to_try = [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-5-sonnet-20241022-v1:0",
        ]
        
        for model_id in models_to_try:
            success = asyncio.run(test_specific_model(model_id))
            if success:
                break
        sys.exit(0)
    
    model_id = sys.argv[1]
    success = asyncio.run(test_specific_model(model_id))
    sys.exit(0 if success else 1)





