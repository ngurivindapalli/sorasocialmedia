"""
Verify Bedrock Permissions
Checks what permissions are actually attached to the IAM user
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_permissions():
    """Verify what permissions are attached"""
    print("=" * 70)
    print("Verifying Bedrock Permissions")
    print("=" * 70)
    print()
    
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not aws_access_key or not aws_secret_key:
        print("❌ AWS credentials not found")
        return
    
    try:
        # Get identity
        sts_client = boto3.client(
            'sts',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        identity = sts_client.get_caller_identity()
        arn = identity.get('Arn', '')
        username = arn.split(':user/')[-1] if ':user/' in arn else 'N/A'
        
        print(f"Identity: {arn}")
        print(f"Username: {username}")
        print()
        
        # Try to list attached policies (requires iam:ListAttachedUserPolicies)
        iam_client = boto3.client(
            'iam',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        try:
            print("Checking attached policies...")
            attached_policies = iam_client.list_attached_user_policies(UserName=username)
            
            if attached_policies.get('AttachedPolicies'):
                print(f"✅ Found {len(attached_policies['AttachedPolicies'])} attached policy/policies:")
                for policy in attached_policies['AttachedPolicies']:
                    print(f"   - {policy['PolicyName']} (ARN: {policy['PolicyArn']})")
            else:
                print("⚠️  No attached policies found")
            
            print()
            
            # Check inline policies
            inline_policies = iam_client.list_user_policies(UserName=username)
            if inline_policies.get('PolicyNames'):
                print(f"✅ Found {len(inline_policies['PolicyNames'])} inline policy/policies:")
                for policy_name in inline_policies['PolicyNames']:
                    print(f"   - {policy_name}")
            else:
                print("⚠️  No inline policies found")
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'AccessDeniedException':
                print("⚠️  Cannot list policies (missing iam:ListAttachedUserPolicies permission)")
                print("   This is OK - we can still test Bedrock directly")
            else:
                print(f"⚠️  Error listing policies: {e}")
        
        print()
        print("-" * 70)
        print("Testing Bedrock Access")
        print("-" * 70)
        
        # Test with different model IDs
        bedrock_runtime = boto3.client(
            'bedrock-runtime',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        models_to_test = [
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "anthropic.claude-3-5-sonnet-20241022-v1:0",
            "anthropic.claude-3-sonnet-20240229-v1:0",
            "anthropic.claude-3-haiku-20240307-v1:0"
        ]
        
        test_payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 10,
            "temperature": 0.7,
            "system": "You are a helpful assistant.",
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'test'"
                }
            ]
        }
        
        import json
        
        for model_id in models_to_test:
            print(f"\nTesting model: {model_id}")
            try:
                response = bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(test_payload)
                )
                response_body = json.loads(response['body'].read())
                text = response_body['content'][0]['text']
                print(f"✅ SUCCESS! Model {model_id} works!")
                print(f"   Response: {text}")
                return True
            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']
                if error_code == 'AccessDeniedException':
                    print(f"   ❌ Access denied: {error_message[:100]}")
                elif error_code == 'ValidationException':
                    print(f"   ⚠️  Validation error (model might not be enabled): {error_message[:100]}")
                else:
                    print(f"   ❌ Error ({error_code}): {error_message[:100]}")
            except Exception as e:
                print(f"   ❌ Unexpected error: {str(e)[:100]}")
        
        print()
        print("=" * 70)
        print("TROUBLESHOOTING")
        print("=" * 70)
        print()
        print("If all models failed with AccessDeniedException:")
        print("1. Verify the policy is attached to the user:")
        print(f"   https://console.aws.amazon.com/iam/home#/users/{username}")
        print()
        print("2. Check the policy allows bedrock:InvokeModel on the correct resources")
        print()
        print("3. Enable model access in Bedrock console:")
        print("   https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess")
        print()
        print("4. If using a resource ARN in the policy, ensure it matches exactly:")
        print("   arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0")
        print()
        print("5. Try using a wildcard resource instead:")
        print('   "Resource": ["*"]')
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    verify_permissions()





