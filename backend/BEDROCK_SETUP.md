# AWS Bedrock Claude Setup Guide

## Test Results

✅ **Bedrock Service**: Initialized successfully  
✅ **AWS Credentials**: Configured correctly  
✅ **AWS Region**: us-east-1  
❌ **Permissions**: IAM user needs Bedrock invoke permissions  

## Identity Making Requests

**Identity Type**: IAM USER  
**Username**: `noel-bedrock-user`  
**ARN**: `arn:aws:iam::434793037118:user/noel-bedrock-user`  
**Account ID**: `434793037118`  
**User ID**: `AIDAWKO5PHU7CMGYMNXI7`

## Current Error

```
AccessDeniedException: User: arn:aws:iam::434793037118:user/noel-bedrock-user 
is not authorized to perform: bedrock:InvokeModel
```

This confirms the request is coming from an **IAM User** (not a role or assumed role).

## Required Setup Steps

### 1. Enable Claude Models in Bedrock Console

1. Go to [AWS Bedrock Console](https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)
2. Click **"Manage model access"** or **"Model access"**
3. Find **Claude models** in the list:
   - `anthropic.claude-3-5-sonnet-20241022-v2:0` (Claude 3.5 Sonnet - Recommended)
   - `anthropic.claude-3-opus-20240229-v1:0` (Claude 3 Opus)
   - `anthropic.claude-3-sonnet-20240229-v1:0` (Claude 3 Sonnet)
   - `anthropic.claude-3-haiku-20240307-v1:0` (Claude 3 Haiku - Fastest)
4. Check the boxes for the models you want to use
5. Click **"Save changes"**

### 2. Grant IAM Permissions

The IAM user `noel-bedrock-user` (ARN: `arn:aws:iam::434793037118:user/noel-bedrock-user`) needs permission to invoke Bedrock models.

#### Option A: Using AWS Console (Recommended - Wildcard Resource)

**Recommended approach**: Use a wildcard resource to avoid ARN format issues.

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Navigate to **Users** → **noel-bedrock-user**
3. Click **"Add permissions"** → **"Create inline policy"** (or **"Attach policies directly"** → **"Create policy"**)
4. Click **"JSON"** tab
5. Paste this policy (uses wildcard resource for simplicity):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        }
    ]
}
```

6. Click **"Next"** → Name it: `BedrockInvokeModelPolicy`
7. Click **"Create policy"**
8. If you created a managed policy, go back to the user → **"Add permissions"** → **"Attach policies directly"** → Search for `BedrockInvokeModelPolicy` and attach it

**Alternative**: If you prefer specific model ARNs, use this instead:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-opus-20240229-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        }
    ]
}
```

#### Option B: Using AWS CLI

```bash
# Create the policy (using wildcard resource - recommended)
aws iam create-policy \
    --policy-name BedrockInvokeModelPolicy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": "*"
            }
        ]
    }'

# Attach policy to user (replace ACCOUNT_ID with your AWS account ID: 434793037118)
aws iam attach-user-policy \
    --user-name noel-bedrock-user \
    --policy-arn arn:aws:iam::434793037118:policy/BedrockInvokeModelPolicy
```

**Note**: If permissions still don't work, see `backend/BEDROCK_TROUBLESHOOTING.md` for detailed troubleshooting steps.

### 3. Test Again

After completing the above steps, run:

```bash
cd backend
python test_bedrock_claude.py
```

You should see:
- ✅ Bedrock service initialized
- ✅ Simple text generation test passed
- ✅ Script generation test passed

## Environment Variables

Ensure your `.env` file has:

```env
AWS_ACCESS_KEY_ID=your-aws-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key-here
AWS_REGION=us-east-1
```

## Current Status

- ✅ Bedrock service code: Working correctly
- ✅ AWS credentials: Configured
- ❌ Model access: Needs to be enabled in Bedrock console
- ❌ IAM permissions: Needs `bedrock:InvokeModel` permission

Once permissions are set up, the system will automatically use Bedrock Claude for:
1. Video script generation
2. Context summarization
3. All text generation tasks

