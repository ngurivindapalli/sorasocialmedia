"""
Test Claude Sonnet 4.5 with Inference Profile
According to the error, we need to use inference profile ARN as modelId
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


async def test_with_inference_profile():
    """Test Claude Sonnet 4.5 using inference profile ARN as modelId"""
    print("=" * 70)
    print("Testing Claude Sonnet 4.5 with Inference Profile")
    print("=" * 70)
    print()
    print("According to AWS error: 'Retry your request with the ID or ARN of")
    print("an inference profile that contains this model.'")
    print()
    print("This means we should use the inference profile ARN as the modelId")
    print()
    
    bedrock_service = BedrockService()
    
    if not bedrock_service.is_available():
        print("❌ Bedrock service is not available!")
        return False
    
    print("✅ Bedrock service initialized")
    print()
    
    # Try using inference profile ARN as modelId
    # The actual ARN format needs to be found in AWS Bedrock console
    # Common format might be: arn:aws:bedrock:region::inference-profile/profile-name
    inference_profile_arns = [
        # Try different possible ARN formats
        "arn:aws:bedrock:us-east-1::inference-profile/anthropic.claude-sonnet-4-5",
        "arn:aws:bedrock::us-east-1:inference-profile/anthropic.claude-sonnet-4-5",
        "arn:aws:bedrock:us-east-1::inference-profile/claude-sonnet-4-5",
    ]
    
    # Also try the direct model ID that gave us the helpful error
    model_ids = [
        "anthropic.claude-sonnet-4-5-20250929-v1:0",  # This one gave us the inference profile hint
    ]
    
    print("Step 1: Trying direct model ID (should tell us the inference profile ARN)...")
    print("-" * 70)
    
    for model_id in model_ids:
        print(f"\nTrying: {model_id}")
        try:
            result = await bedrock_service.generate_text(
                prompt="Say 'test'",
                system_message="You are a helpful assistant.",
                max_tokens=10,
                temperature=0.7,
                model=model_id,
                use_converse_api=True
            )
            if result:
                print(f"✅ SUCCESS with direct model ID: {model_id}")
                print(f"Response: {result}")
                return True
        except Exception as e:
            error_msg = str(e)
            if "inference profile" in error_msg.lower():
                print(f"   ℹ️  Error suggests using inference profile ARN")
                print(f"   Error: {error_msg[:150]}")
            else:
                print(f"   ❌ Error: {error_msg[:100]}")
    
    print("\n" + "=" * 70)
    print("Step 2: Trying inference profile ARNs as modelId...")
    print("=" * 70)
    print()
    print("Note: You need to find the actual inference profile ARN in AWS Bedrock console")
    print("Go to: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1")
    print("Navigate to: Inference profiles")
    print()
    
    for profile_arn in inference_profile_arns:
        print(f"\nTrying inference profile ARN: {profile_arn}")
        try:
            result = await bedrock_service.generate_text(
                prompt="Write a short, engaging video script (2-3 sentences) about AI careers.",
                system_message="You are an expert video script writer.",
                max_tokens=200,
                temperature=0.7,
                model=profile_arn,  # Use profile ARN as modelId
                use_converse_api=True
            )
            if result:
                print(f"\n✅ SUCCESS! Generated text ({len(result)} chars):")
                print(f"\n{result}\n")
                print("=" * 70)
                print(f"✅ Claude Sonnet 4.5 is working with inference profile: {profile_arn}")
                print("=" * 70)
                return True
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg[:100]}")
    
    print("\n" + "=" * 70)
    print("❌ Could not access Claude Sonnet 4.5")
    print("=" * 70)
    print()
    print("To find the correct inference profile ARN:")
    print("1. Go to AWS Bedrock Console: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1")
    print("2. Navigate to 'Inference profiles' in the left menu")
    print("3. Look for a profile containing Claude Sonnet 4.5")
    print("4. Copy the ARN (should look like: arn:aws:bedrock:...)")
    print("5. Use that ARN as the modelId in the Converse API")
    print()
    print("Alternatively, check the AWS documentation for the exact model ID format:")
    print("https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html")
    
    return False


if __name__ == "__main__":
    success = asyncio.run(test_with_inference_profile())
    sys.exit(0 if success else 1)





