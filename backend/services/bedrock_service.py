"""
AWS Bedrock Service - Claude Integration
Uses AWS Bedrock to access Claude models for text generation
"""

import os
import json
from typing import Optional, Dict
import boto3
import asyncio
from botocore.exceptions import ClientError


class BedrockService:
    """Service for AWS Bedrock Claude text generation"""
    
    def __init__(self):
        """Initialize Bedrock service with AWS credentials"""
        self.available = False
        self.bedrock_runtime = None
        
        # Get AWS credentials from environment
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not aws_access_key or not aws_secret_key:
            print("[Bedrock] AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
            return
        
        try:
            # Initialize Bedrock runtime client
            self.bedrock_runtime = boto3.client(
                'bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Test connection by listing available models (optional check)
            # For now, just mark as available if client initializes
            self.available = True
            print(f"[Bedrock] OK Bedrock service initialized (region: {aws_region})")
            print(f"[Bedrock] Using Claude via AWS Bedrock")
        except Exception as e:
            print(f"[Bedrock] ERROR: Failed to initialize Bedrock service: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Bedrock service is available"""
        return self.available
    
    async def generate_text(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant.",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: str = "arn:aws:bedrock:us-east-1:222634391096:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        use_converse_api: bool = False,
        inference_profile: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate text using Claude via AWS Bedrock
        
        Args:
            prompt: User prompt
            system_message: System message for Claude
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            model: Claude model ID (default: Claude 3.5 Sonnet)
            use_converse_api: Use Converse API (required for Claude Sonnet 4.5)
            inference_profile: Inference profile for Converse API (optional)
            
        Returns:
            Generated text or None if failed
            
        Available models:
            - arn:aws:bedrock:us-east-1:222634391096:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0 (Claude Sonnet 4.5 - default, requires Converse API)
            - anthropic.claude-3-5-sonnet-20241022-v2:0 (Claude 3.5 Sonnet - fallback)
            - anthropic.claude-3-opus-20240229-v1:0 (Claude 3 Opus)
            - anthropic.claude-3-sonnet-20240229-v1:0 (Claude 3 Sonnet)
            - anthropic.claude-3-haiku-20240307-v1:0 (Claude 3 Haiku - fastest)
        """
        if not self.available or not self.bedrock_runtime:
            print("[Bedrock] Bedrock service not available.")
            return None
        
        try:
            # Use Converse API for Claude Sonnet 4.5 (default) or if explicitly requested
            # Claude Sonnet 4.5 uses inference profile ARN, so check for that or explicit flag
            if use_converse_api or "inference-profile" in model.lower() or "sonnet-4-5" in model.lower() or "claude-4" in model.lower():
                return await self._generate_with_converse_api(
                    prompt=prompt,
                    system_message=system_message,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    model=model,
                    inference_profile=inference_profile
                )
            
            # Build the request body for Claude API (Bedrock format)
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_message,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Invoke Claude model via Bedrock (boto3 calls are sync, so wrap in thread)
            def invoke_sync():
                response = self.bedrock_runtime.invoke_model(
                    modelId=model,
                    body=json.dumps(request_body)
                )
                return json.loads(response['body'].read())
            
            response_body = await asyncio.to_thread(invoke_sync)
            
            # Extract text from Claude's response
            # Claude response format: {"content": [{"type": "text", "text": "..."}]}
            if 'content' in response_body and len(response_body['content']) > 0:
                generated_text = response_body['content'][0].get('text', '')
                if generated_text:
                    print(f"[Bedrock] ✓ Text generated with Claude ({len(generated_text)} chars)")
                    return generated_text
            
            print("[Bedrock] WARNING: Empty response from Claude")
            return None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"[Bedrock] ERROR: AWS Bedrock error ({error_code}): {error_message}")
            
            # Handle common errors
            if error_code == 'AccessDeniedException':
                print("[Bedrock] Make sure your AWS credentials have permission to use Bedrock")
                print("[Bedrock] Enable Claude model access in AWS Bedrock console")
            elif error_code == 'ValidationException':
                print(f"[Bedrock] Invalid request - check model ID: {model}")
            
            return None
        except Exception as e:
            print(f"[Bedrock] ERROR: Error generating text with Claude: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def _generate_with_converse_api(
        self,
        prompt: str,
        system_message: str,
        max_tokens: int,
        temperature: float,
        model: str,
        inference_profile: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate text using Bedrock Converse API (required for Claude Sonnet 4.5)
        """
        try:
            # Build Converse API request
            converse_request = {
                "modelId": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "system": [{"text": system_message}],
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature
                }
            }
            
            # Note: For Claude Sonnet 4.5, use inference profile ARN as modelId
            # The inference_profile parameter should be the ARN of the inference profile
            # If provided, use it as the modelId instead
            if inference_profile:
                # If inference_profile looks like an ARN, use it as modelId
                if inference_profile.startswith("arn:aws:bedrock"):
                    converse_request["modelId"] = inference_profile
                else:
                    # Otherwise, try to construct ARN (this is a guess - actual ARN format may differ)
                    print(f"[Bedrock] Note: Inference profile should be an ARN, not a region name")
            
            # Invoke Converse API
            def converse_sync():
                response = self.bedrock_runtime.converse(**converse_request)
                return response
            
            response = await asyncio.to_thread(converse_sync)
            
            # Extract text from Converse API response
            if 'output' in response and 'message' in response['output']:
                content = response['output']['message'].get('content', [])
                if content and len(content) > 0:
                    generated_text = content[0].get('text', '')
                    if generated_text:
                        print(f"[Bedrock] ✓ Text generated with Claude Sonnet 4.5 ({len(generated_text)} chars)")
                        return generated_text
            
            print("[Bedrock] WARNING: Empty response from Claude Converse API")
            return None
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"[Bedrock] ERROR: Converse API error ({error_code}): {error_message}")
            
            if error_code == 'AccessDeniedException':
                print("[Bedrock] Make sure your AWS credentials have permission to use Bedrock Converse API")
                print("[Bedrock] Enable Claude Sonnet 4.5 model access in Bedrock console")
            elif error_code == 'ValidationException':
                print(f"[Bedrock] Invalid request - check model ID: {model}")
                print("[Bedrock] Claude Sonnet 4.5 requires Converse API and may need an inference profile")
            
            return None
        except Exception as e:
            print(f"[Bedrock] ERROR: Error with Converse API: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def generate_script(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """
        Generate a video script using Claude via Bedrock
        
        Args:
            prompt: Script generation prompt
            system_message: Optional system message (uses default if not provided)
            max_tokens: Maximum tokens (default 2000 for scripts)
            temperature: Sampling temperature
            
        Returns:
            Generated script text or None if failed
        """
        default_system_message = (
            "You are an expert video script writer who creates detailed, visual video scripts "
            "for AI video generation. Create scripts that are clear, engaging, and optimized "
            "for Veo 3 video generation."
        )
        
        system_msg = system_message or default_system_message
        
        # Use Claude Sonnet 4.5 inference profile ARN for script generation
        # This is the latest and most capable model for complex tasks
        sonnet_4_5_arn = "arn:aws:bedrock:us-east-1:222634391096:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        
        return await self.generate_text(
            prompt=prompt,
            system_message=system_msg,
            max_tokens=max_tokens,
            temperature=temperature,
            model=sonnet_4_5_arn,  # Use Claude Sonnet 4.5 for scripts
            use_converse_api=True  # Required for Sonnet 4.5
        )

