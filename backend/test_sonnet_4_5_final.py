"""
Test Claude Sonnet 4.5 with the actual inference profile ARN
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
    """Test Claude Sonnet 4.5 with the inference profile ARN"""
    print("=" * 70)
    print("Testing Claude Sonnet 4.5 with Inference Profile ARN")
    print("=" * 70)
    print()
    
    # The inference profile ARN from AWS console
    inference_profile_arn = "arn:aws:bedrock:us-east-1:222634391096:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
    
    print(f"Inference Profile ARN: {inference_profile_arn}")
    print()
    
    # Initialize Bedrock service
    bedrock_service = BedrockService()
    
    if not bedrock_service.is_available():
        print("❌ Bedrock service is not available!")
        return False
    
    print("✅ Bedrock service initialized")
    print()
    
    # Test 1: Simple text generation
    print("-" * 70)
    print("Test 1: Simple text generation")
    print("-" * 70)
    try:
        result = await bedrock_service.generate_text(
            prompt="Write a short, engaging video script (2-3 sentences) about AI careers for social media.",
            system_message="You are an expert video script writer.",
            max_tokens=200,
            temperature=0.7,
            model=inference_profile_arn,  # Use inference profile ARN as modelId
            use_converse_api=True
        )
        
        if result:
            print(f"\n✅ SUCCESS! Generated text ({len(result)} chars):")
            print(f"\n{result}\n")
        else:
            print("\n❌ Failed: No text generated")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Script generation
    print("-" * 70)
    print("Test 2: Video script generation")
    print("-" * 70)
    try:
        script = await bedrock_service.generate_text(
            prompt="Create a video script about the future of AI in marketing. Make it engaging and visual, suitable for Veo 3 video generation.",
            system_message="You are an expert video script writer who creates detailed, visual video scripts for AI video generation. Create scripts that are clear, engaging, and optimized for Veo 3 video generation.",
            max_tokens=500,
            temperature=0.7,
            model=inference_profile_arn,
            use_converse_api=True
        )
        
        if script:
            print(f"\n✅ SUCCESS! Generated script ({len(script)} chars):")
            print(f"\n{script[:400]}...\n")
        else:
            print("\n❌ Failed: No script generated")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 70)
    print("✅ All tests passed! Claude Sonnet 4.5 is working correctly!")
    print("=" * 70)
    print()
    print(f"Inference Profile ARN: {inference_profile_arn}")
    print()
    print("You can now use this ARN in your application by setting:")
    print(f'  model="{inference_profile_arn}"')
    print("  use_converse_api=True")
    print()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_claude_sonnet_4_5())
    sys.exit(0 if success else 1)




