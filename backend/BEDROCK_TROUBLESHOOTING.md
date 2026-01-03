# Bedrock Permissions Troubleshooting

## Current Status
❌ Still getting `AccessDeniedException` for `bedrock:InvokeModel`

## Quick Fix: Use Wildcard Resource

The most reliable approach is to use a wildcard (`*`) for the resource in your IAM policy. This avoids ARN format issues.

### Policy JSON (Wildcard Resource)

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

### Steps to Apply

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Navigate to**: Users → `noel-bedrock-user`
3. **Click**: "Add permissions" → "Create inline policy"
4. **Select**: JSON tab
5. **Paste** the policy JSON above
6. **Name it**: `BedrockInvokeModelPolicy`
7. **Click**: "Create policy"

**OR** attach as a managed policy:

1. **Go to**: IAM → Policies → "Create policy"
2. **JSON tab** → Paste the policy above
3. **Name**: `BedrockInvokeModelPolicy`
4. **Create policy**
5. **Go back to user** → "Add permissions" → "Attach policies directly"
6. **Search for** `BedrockInvokeModelPolicy` → Attach

## Verify Model Access

**CRITICAL**: Even with IAM permissions, you must enable model access in Bedrock console:

1. Go to: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
2. Click **"Manage model access"** or **"Model access"**
3. Find and **check** these Claude models:
   - ✅ `anthropic.claude-3-5-sonnet-20241022-v2:0`
   - ✅ `anthropic.claude-3-sonnet-20240229-v1:0`
   - ✅ `anthropic.claude-3-haiku-20240307-v1:0`
4. Click **"Save changes"**

**Note**: Model access can take a few minutes to propagate.

## Common Issues

### Issue 1: Policy Not Attached
- **Symptom**: Still getting AccessDeniedException
- **Fix**: Verify policy is attached to the user in IAM console

### Issue 2: Wrong Resource ARN Format
- **Symptom**: Policy attached but still denied
- **Fix**: Use wildcard `"Resource": ["*"]` instead of specific ARNs

### Issue 3: Model Not Enabled
- **Symptom**: ValidationException or AccessDeniedException
- **Fix**: Enable model in Bedrock console (see "Verify Model Access" above)

### Issue 4: Policy Propagation Delay
- **Symptom**: Policy attached but still denied
- **Fix**: Wait 1-2 minutes, then test again

### Issue 5: Wrong Region
- **Symptom**: Model not found
- **Fix**: Ensure `AWS_REGION=us-east-1` in `.env` and model is enabled in that region

## Test After Fix

Run the test script:
```bash
cd backend
python test_bedrock_claude.py
```

You should see:
- ✅ Bedrock service initialized
- ✅ Simple text generation test passed
- ✅ Script generation test passed

## Alternative: Check Policy via AWS CLI

If you have AWS CLI configured with admin credentials:

```bash
# List attached policies
aws iam list-attached-user-policies --user-name noel-bedrock-user

# Get policy document
aws iam get-policy --policy-arn <POLICY_ARN>
aws iam get-policy-version --policy-arn <POLICY_ARN> --version-id <VERSION_ID>

# List inline policies
aws iam list-user-policies --user-name noel-bedrock-user
aws iam get-user-policy --user-name noel-bedrock-user --policy-name <POLICY_NAME>
```

## Direct Links

- **IAM User**: https://console.aws.amazon.com/iam/home#/users/noel-bedrock-user
- **Bedrock Model Access**: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
- **IAM Policies**: https://console.aws.amazon.com/iam/home#/policies




