"""
Check AWS Identity for Bedrock Requests
Identifies who is making the AWS Bedrock API calls
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_aws_identity():
    """Check the AWS identity being used for API calls"""
    print("=" * 70)
    print("AWS Identity Check for Bedrock Requests")
    print("=" * 70)
    print()
    
    # Get AWS credentials from environment
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    if not aws_access_key or not aws_secret_key:
        print("❌ AWS credentials not found in environment variables")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return
    
    print(f"[INFO] AWS Region: {aws_region}")
    print(f"[INFO] AWS Access Key ID: {aws_access_key[:10]}...{aws_access_key[-4:]}")
    print()
    
    try:
        # Create STS client to get caller identity
        sts_client = boto3.client(
            'sts',
            region_name=aws_region,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        
        print("[INFO] Getting caller identity...")
        identity = sts_client.get_caller_identity()
        
        print()
        print("-" * 70)
        print("IDENTITY INFORMATION")
        print("-" * 70)
        
        arn = identity.get('Arn', 'N/A')
        user_id = identity.get('UserId', 'N/A')
        account = identity.get('Account', 'N/A')
        
        print(f"Account ID: {account}")
        print(f"User ID: {user_id}")
        print(f"ARN: {arn}")
        print()
        
        # Determine identity type
        print("-" * 70)
        print("IDENTITY TYPE ANALYSIS")
        print("-" * 70)
        
        if ':user/' in arn:
            print("✅ Identity Type: IAM USER")
            username = arn.split(':user/')[-1]
            print(f"   Username: {username}")
            print()
            print("📝 This is a direct IAM user.")
            print("   To grant permissions:")
            print("   1. Go to IAM Console → Users → " + username)
            print("   2. Attach policy with bedrock:InvokeModel permission")
            print("   3. Enable Claude models in Bedrock console")
            
        elif ':role/' in arn:
            if ':assumed-role/' in arn:
                print("✅ Identity Type: ASSUMED ROLE (via STS)")
                role_name = arn.split(':assumed-role/')[1].split('/')[0]
                session_name = arn.split('/')[-1] if '/' in arn.split(':assumed-role/')[1] else 'N/A'
                print(f"   Role Name: {role_name}")
                print(f"   Session Name: {session_name}")
                print()
                print("📝 This is an assumed role (temporary credentials via STS).")
                print("   The role itself needs permissions.")
                print("   To grant permissions:")
                print("   1. Go to IAM Console → Roles → " + role_name)
                print("   2. Attach policy with bedrock:InvokeModel permission")
                print("   3. Enable Claude models in Bedrock console")
            else:
                print("✅ Identity Type: IAM ROLE")
                role_name = arn.split(':role/')[-1]
                print(f"   Role Name: {role_name}")
                print()
                print("📝 This is an IAM role (used by EC2, Lambda, ECS, etc.).")
                print("   To grant permissions:")
                print("   1. Go to IAM Console → Roles → " + role_name)
                print("   2. Attach policy with bedrock:InvokeModel permission")
                print("   3. Enable Claude models in Bedrock console")
        else:
            print("⚠️  Identity Type: UNKNOWN")
            print(f"   ARN format: {arn}")
        
        print()
        print("-" * 70)
        print("BEDROCK PERMISSIONS CHECK")
        print("-" * 70)
        
        # Try to check Bedrock access
        try:
            bedrock_client = boto3.client(
                'bedrock',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Try to list foundation models (requires bedrock:ListFoundationModels permission)
            try:
                models = bedrock_client.list_foundation_models()
                print("✅ Can access Bedrock API (list_foundation_models works)")
                print(f"   Found {len(models.get('modelSummaries', []))} foundation models")
            except ClientError as e:
                if e.response['Error']['Code'] == 'AccessDeniedException':
                    print("⚠️  Cannot list foundation models (missing bedrock:ListFoundationModels)")
                    print("   This is OK - you only need bedrock:InvokeModel for generation")
                else:
                    print(f"⚠️  Error checking models: {e}")
            
            # Check if we can invoke a model
            bedrock_runtime = boto3.client(
                'bedrock-runtime',
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            print()
            print("Testing bedrock:InvokeModel permission...")
            print("   (This will fail if permission is missing, which is expected)")
            
        except Exception as e:
            print(f"⚠️  Could not check Bedrock access: {e}")
        
        print()
        print("=" * 70)
        print("RECOMMENDED ACTIONS")
        print("=" * 70)
        print()
        print("1. Enable Claude models in Bedrock Console:")
        print("   https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess")
        print()
        print("2. Grant bedrock:InvokeModel permission to this identity:")
        print(f"   {arn}")
        print()
        print("3. See backend/BEDROCK_SETUP.md for detailed instructions")
        print()
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"❌ Error getting identity: {error_code}")
        print(f"   {error_message}")
        print()
        print("Possible issues:")
        print("  - Invalid AWS credentials")
        print("  - Credentials don't have sts:GetCallerIdentity permission")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_aws_identity()




