"""
Test Claude Sonnet 4.5 in Amazon Bedrock
Based on: https://aws.amazon.com/blogs/aws/introducing-claude-sonnet-4-5-in-amazon-bedrock-anthropics-most-intelligent-model-best-for-coding-and-complex-agents/
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


async def test_claude_sonnet_4_5():
    """Test Claude Sonnet 4.5 via Bedrock Converse API"""
    print("=" * 70)
    print("Testing Claude Sonnet 4.5 in Amazon Bedrock")
    print("=" * 70)
    print()
    print("Reference: https://aws.amazon.com/blogs/aws/introducing-claude-sonnet-4-5-in-amazon-bedrock-anthropics-most-intelligent-model-best-for-coding-and-complex-agents/")
    print()
    
    # Initialize Bedrock service
    bedrock_service = BedrockService()
    
    if not bedrock_service.is_available():
        print("❌ Bedrock service is not available!")
        return False
    
    print("✅ Bedrock service initialized")
    print()
    
    # Try different possible model IDs for Claude Sonnet 4.5
    # According to the blog, it's accessed via Converse API with inference profile
    models_to_try = [
        "anthropic.claude-sonnet-4-5-20250929-v1:0",  # Possible format
        "anthropic.claude-sonnet-4-5-20250929-v0:0",  # Alternative
        "anthropic.claude-sonnet-4-5",  # Without version
        "anthropic.claude-4-5-sonnet-20250929-v1:0",  # Alternative naming
    ]
    
    # Inference profiles (from blog: "system-defined cross-Region inference profiles")
    inference_profiles = [
        None,  # Try without profile first
        "us-east-1",  # Single region
        "us-west-2",  # Alternative region
    ]
    
    print("Note: Claude Sonnet 4.5 requires Converse API and may use inference profiles")
    print()
    
    for model_id in models_to_try:
        print(f"\n{'='*70}")
        print(f"Trying model: {model_id}")
        print(f"{'='*70}")
        
        # Try with and without inference profile
        for profile in inference_profiles:
            profile_str = f" (profile: {profile})" if profile else " (no profile)"
            print(f"\n  Attempting{profile_str}...")
            
            try:
                result = await bedrock_service.generate_text(
                    prompt="Write a short, engaging video script (2-3 sentences) about AI careers for social media.",
                    system_message="You are an expert video script writer.",
                    max_tokens=200,
                    temperature=0.7,
                    model=model_id,
                    use_converse_api=True,
                    inference_profile=profile
                )
                
                if result:
                    print(f"\n  ✅ SUCCESS! Generated text ({len(result)} chars):")
                    print(f"\n  {result}\n")
                    print("=" * 70)
                    print(f"✅ Claude Sonnet 4.5 is working with model: {model_id}")
                    if profile:
                        print(f"   Using inference profile: {profile}")
                    print("=" * 70)
                    return True
                    
            except Exception as e:
                error_msg = str(e)
                if "AccessDeniedException" in error_msg:
                    print(f"  ❌ Access denied (permissions issue)")
                elif "ValidationException" in error_msg or "not found" in error_msg.lower():
                    print(f"  ⚠️  Model not found or invalid ID")
                else:
                    print(f"  ❌ Error: {error_msg[:80]}")
                continue
        
        print(f"\n  ❌ Model {model_id} not accessible")
    
    print("\n" + "=" * 70)
    print("❌ Could not access Claude Sonnet 4.5")
    print("=" * 70)
    print("\nPossible issues:")
    print("1. Model ID format may be different - check AWS Bedrock console")
    print("2. Model may not be enabled in your region")
    print("3. Permissions may not be set up for Converse API")
    print("4. Inference profile may be required")
    print("\nNext steps:")
    print("- Check AWS Bedrock console for exact model ID")
    print("- Verify model is enabled in your region")
    print("- Ensure IAM permissions include bedrock:InvokeModel for Converse API")
    print("\nReference: https://aws.amazon.com/blogs/aws/introducing-claude-sonnet-4-5-in-amazon-bedrock-anthropics-most-intelligent-model-best-for-coding-and-complex-agents/")
    
    return False


if __name__ == "__main__":
    success = asyncio.run(test_claude_sonnet_4_5())
    sys.exit(0 if success else 1)





