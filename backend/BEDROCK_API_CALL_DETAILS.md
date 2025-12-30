# Bedrock API Call Details

This document shows the exact code that calls AWS Bedrock and the details your team needs to debug the permission issue.

## Identity Making the Request

- **Type**: IAM User
- **Username**: `noel-bedrock-user`
- **ARN**: `arn:aws:iam::434793037118:user/noel-bedrock-user`
- **Account ID**: `434793037118`
- **User ID**: `AIDAWKO5PHU7CMGYMNXI7`

## AWS Credentials

- **Access Key ID**: `AKIAWKO5PHU7IU436ZU6` (first 10 chars: `AKIAWKO5PH...`)
- **Secret Access Key**: Set (from environment variable)
- **Region**: `us-east-1`

## Code Snippet: Bedrock API Call

### File: `backend/services/bedrock_service.py`

```python
import boto3
import json
import asyncio
from botocore.exceptions import ClientError

# Initialize Bedrock Runtime Client
bedrock_runtime = boto3.client(
    'bedrock-runtime',
    region_name='us-east-1',
    aws_access_key_id='AKIAWKO5PHU7IU436ZU6',
    aws_secret_access_key='<from environment>'
)

# Request Body Format
request_body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "temperature": 0.7,
    "system": "You are a helpful assistant.",
    "messages": [
        {
            "role": "user",
            "content": "Write a short video script about AI careers."
        }
    ]
}

# THE ACTUAL API CALL (Line 101-104)
def invoke_sync():
    response = bedrock_runtime.invoke_model(
        modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
        body=json.dumps(request_body)
    )
    return json.loads(response['body'].read())

# Called asynchronously
response_body = await asyncio.to_thread(invoke_sync)
```

## Exact API Call Details

### Service: `bedrock-runtime`
### Method: `invoke_model()`
### Parameters:

```python
{
    "modelId": "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "body": json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.7,
        "system": "You are a helpful assistant.",
        "messages": [
            {
                "role": "user",
                "content": "<prompt text>"
            }
        ]
    })
}
```

### Model ID: `anthropic.claude-3-5-sonnet-20241022-v2:0`

## Current Error

```
AccessDeniedException: User: arn:aws:iam::434793037118:user/noel-bedrock-user 
is not authorized to perform: bedrock:InvokeModel on resource: 
arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0 
because no identity-based policy allows the bedrock:InvokeModel action
```

## Required IAM Permission

The IAM user needs a policy that allows:

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

**OR** with specific model ARNs:

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
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
                "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            ]
        }
    ]
}
```

## Additional Requirements

1. **Model Access**: The Claude models must be enabled in Bedrock Console:
   - Go to: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
   - Enable: `anthropic.claude-3-5-sonnet-20241022-v2:0`

2. **IAM Policy Attachment**: The policy must be attached to the user:
   - User: `noel-bedrock-user`
   - ARN: `arn:aws:iam::434793037118:user/noel-bedrock-user`

## Full Code Context

The complete service class is in: `backend/services/bedrock_service.py`

Key methods:
- `__init__()`: Initializes boto3 client (lines 17-47)
- `generate_text()`: Makes the API call (lines 53-137)
- `generate_script()`: Wrapper for script generation (lines 139-172)

The actual `invoke_model()` call happens at **line 101**:

```python
response = self.bedrock_runtime.invoke_model(
    modelId=model,
    body=json.dumps(request_body)
)
```

## Testing

To test if permissions work, run:

```bash
cd backend
python test_bedrock_claude.py
```

Or use the verification script:

```bash
python verify_bedrock_permissions.py
```

## AWS Console Links

- **IAM User**: https://console.aws.amazon.com/iam/home#/users/noel-bedrock-user
- **Bedrock Model Access**: https://us-east-1.console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
- **IAM Policies**: https://console.aws.amazon.com/iam/home#/policies


