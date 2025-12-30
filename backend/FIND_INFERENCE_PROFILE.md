# How to Find Claude Sonnet 4.5 Inference Profile ARN

## Step-by-Step Guide

### 1. Navigate to Cross-Region Inference

In the AWS Bedrock console sidebar (left side):
- Find the **"Infer"** section (should be expanded)
- Click on **"Cross-region inference"** (highlighted in yellow)

### 2. Find Claude Sonnet 4.5 Profile

Once you're in the Cross-region inference page:
- Look for inference profiles that contain **Claude Sonnet 4.5**
- The profile name might be something like:
  - `anthropic.claude-sonnet-4-5`
  - `claude-sonnet-4-5-cross-region`
  - Or a system-defined profile name

### 3. Get the ARN

When you find the profile:
- Click on the profile name
- Look for the **ARN** field
- It should look like: `arn:aws:bedrock:us-east-1::inference-profile/...`
- **Copy this ARN**

### 4. Alternative Locations

If you don't see it in Cross-region inference, also check:
- **"Custom model on-demand"** (also in the Infer section)
- Look for any profile that mentions Claude Sonnet 4.5

### 5. Use the ARN

Once you have the ARN, you can test it with:

```bash
python test_sonnet_4_5_inference_profile.py
```

Or update the test script with the actual ARN you found.

## What to Look For

The inference profile ARN will be used as the `modelId` parameter in the Converse API call. According to AWS documentation, Claude Sonnet 4.5 can only be accessed through inference profiles, not directly via model ID.

## Quick Test

After you find the ARN, you can test it directly:

```python
from services.bedrock_service import BedrockService
import asyncio

async def test():
    service = BedrockService()
    result = await service.generate_text(
        prompt="Say 'test'",
        model="<paste-your-inference-profile-arn-here>",
        use_converse_api=True
    )
    print(result)

asyncio.run(test())
```

## Console Links

- **Bedrock Console**: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1
- **Cross-region inference**: Navigate via sidebar → Infer → Cross-region inference


