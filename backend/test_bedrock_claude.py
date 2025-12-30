"""
Test script for AWS Bedrock Claude integration
This script tests if Bedrock service is properly configured and can generate text.
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


async def test_bedrock_claude():
    """Test Bedrock Claude service"""
    print("=" * 60)
    print("Testing AWS Bedrock Claude Integration")
    print("=" * 60)
    print()
    
    # Check AWS credentials
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    print(f"[TEST] AWS Region: {aws_region}")
    print(f"[TEST] AWS Access Key ID: {'✅ Set' if aws_access_key else '❌ Missing'} ({aws_access_key[:10] + '...' if aws_access_key else 'N/A'})")
    print(f"[TEST] AWS Secret Access Key: {'✅ Set' if aws_secret_key else '❌ Missing'}")
    print()
    
    # Initialize Bedrock service
    print("[TEST] Initializing Bedrock service...")
    bedrock_service = BedrockService()
    
    if not bedrock_service.is_available():
        print("❌ Bedrock service is not available!")
        print("\nPossible issues:")
        print("  1. AWS credentials not set (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("  2. AWS region not set (AWS_REGION, default: us-east-1)")
        print("  3. Bedrock not enabled in your AWS account")
        print("  4. Claude models not enabled in Bedrock console")
        return False
    
    print("✅ Bedrock service initialized successfully!")
    print()
    
    # Test 1: Simple text generation - Try multiple Claude 3.5 Sonnet versions
    print("-" * 60)
    print("Test 1: Simple text generation (trying Claude 3.5 Sonnet model variants)")
    print("-" * 60)
    
    # Try different model versions - including potential newer versions
    models_to_try = [
        "anthropic.claude-3-5-sonnet-20241022-v2:0",  # v2 (current default)
        "anthropic.claude-3-5-sonnet-20241022-v1:0",  # v1
        "anthropic.claude-3-5-sonnet-20240620-v1:0",  # Older version
        # Try variations that might exist
        "anthropic.claude-3-5-sonnet-20250101-v1:0",  # Potential newer version
    ]
    
    result = None
    working_model = None
    
    for model_id in models_to_try:
        print(f"\nTrying model: {model_id}")
        try:
            result = await bedrock_service.generate_text(
                prompt="Write a short, engaging video script (2-3 sentences) about AI careers for social media.",
                system_message="You are an expert video script writer.",
                max_tokens=200,
                temperature=0.7,
                model=model_id
            )
            
            if result:
                working_model = model_id
                print(f"✅ Success with {model_id}!")
                break
        except Exception as e:
            error_msg = str(e)
            if "AccessDeniedException" in error_msg:
                print(f"   ❌ Access denied (permissions issue)")
            elif "ValidationException" in error_msg:
                print(f"   ⚠️  Model not found or not enabled")
            else:
                print(f"   ❌ Failed: {error_msg[:100]}")
            continue
    
    if result:
        print(f"\n✅ Success! Generated text ({len(result)} chars) using {working_model}:")
        print(f"\n{result}\n")
    else:
        print("\n❌ Failed: No text generated with any model version")
        print("\nNote: If you meant a specific model ID, please provide it and we can test that directly.")
        return False
    
    # Test 2: Script generation with the working model
    print("-" * 60)
    print(f"Test 2: Script generation (using {working_model})")
    print("-" * 60)
    try:
        # Override the default model in generate_script by calling generate_text directly
        script = await bedrock_service.generate_text(
            prompt="Create a video script about the future of AI in marketing. Make it engaging and visual.",
            system_message="You are an expert video script writer who creates detailed, visual video scripts for AI video generation. Create scripts that are clear, engaging, and optimized for Veo 3 video generation.",
            max_tokens=500,
            temperature=0.7,
            model=working_model
        )
        
        if script:
            print(f"✅ Success! Generated script ({len(script)} chars):")
            print(f"\n{script[:300]}...\n")
        else:
            print("❌ Failed: No script generated")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    print(f"✅ All tests passed! Claude via AWS Bedrock is working correctly with {working_model}.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = asyncio.run(test_bedrock_claude())
    sys.exit(0 if success else 1)
