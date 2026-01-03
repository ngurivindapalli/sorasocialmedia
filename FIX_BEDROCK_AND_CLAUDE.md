# Fixing Bedrock and Claude API Issues

## Current Problems

1. **Bedrock Access Denied**: `render-s3-access` user doesn't have Bedrock permissions (only S3)
2. **Claude API Key Invalid**: `ANTHROPIC_API_KEY` is missing or invalid in Render

## Solution Options

### Option A: Use Separate Bedrock Credentials (Recommended if you have access)

If you have access to the Bedrock account (`noel-bedrock-user`), use separate credentials:

#### Step 1: Get Bedrock Credentials

You'll need the AWS access keys for the Bedrock account (managed by someone else):
- `BEDROCK_AWS_ACCESS_KEY_ID` (from `noel-bedrock-user`)
- `BEDROCK_AWS_SECRET_ACCESS_KEY` (from `noel-bedrock-user`)

#### Step 2: Update Render Environment Variables

Add these to Render Dashboard → Environment:

```
# S3 Access (your account)
AWS_ACCESS_KEY_ID=your-s3-access-key-id
AWS_SECRET_ACCESS_KEY=your-s3-secret-access-key
AWS_S3_BUCKET=x-video-hook-mem0-20251228193510
AWS_REGION=us-east-1

# Bedrock Access (separate account - if available)
BEDROCK_AWS_ACCESS_KEY_ID=your-bedrock-access-key
BEDROCK_AWS_SECRET_ACCESS_KEY=your-bedrock-secret-key
BEDROCK_AWS_REGION=us-east-1
```

#### Step 3: Update BedrockService to Use Separate Credentials

We need to modify `backend/services/bedrock_service.py` to check for separate Bedrock credentials first.

---

### Option B: Disable Bedrock, Use Anthropic/OpenAI Only (Easiest)

If you don't have Bedrock access, disable it and use Anthropic/OpenAI APIs:

#### Step 1: Add Claude API Key to Render

1. Get your Anthropic API key from: https://console.anthropic.com/
2. Go to Render Dashboard → Environment
3. Add:
   ```
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

#### Step 2: Update Code to Skip Bedrock

The code already falls back to Anthropic/OpenAI when Bedrock fails, but we can make it skip Bedrock entirely if credentials aren't available.

---

### Option C: Add Bedrock Permissions to S3 User (If Same Account)

If Bedrock is in the same AWS account as your S3 bucket, you can add Bedrock permissions:

#### Step 1: Update IAM Policy

1. Go to IAM → Policies → `render` (or `RenderS3AccessPolicy`)
2. Edit → JSON tab
3. Add Bedrock permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3BucketAccess",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:ListBucketMultipartUploads",
                "s3:ListMultipartUploadParts",
                "s3:AbortMultipartUpload",
                "s3:GetBucketLocation",
                "s3:GetObjectVersion"
            ],
            "Resource": [
                "arn:aws:s3:::x-video-hook-mem0-20251228193510",
                "arn:aws:s3:::x-video-hook-mem0-20251228193510/*"
            ]
        },
        {
            "Sid": "BedrockAccess",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:Converse",
                "bedrock:ConverseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:us-east-1:222634391096:inference-profile/*",
                "arn:aws:bedrock:us-east-1:222634391096:foundation-model/*"
            ]
        }
    ]
}
```

4. Save changes

**Note**: This only works if Bedrock is in the same AWS account (222634391096). If Bedrock is in a different account, this won't work.

---

## ✅ Solution: Use Separate Bedrock Credentials (IMPLEMENTED)

The code has been updated to support separate Bedrock credentials! Follow these steps:

### Step 1: Add Bedrock Credentials to Render

1. Go to **Render Dashboard** → Your Backend Service → **Environment**
2. Add these new environment variables:

```
BEDROCK_AWS_ACCESS_KEY_ID=your-bedrock-access-key-id
BEDROCK_AWS_SECRET_ACCESS_KEY=your-bedrock-secret-access-key
BEDROCK_AWS_REGION=us-east-1
```

3. **Keep your existing S3 credentials** (these are separate):
```
AWS_ACCESS_KEY_ID=your-s3-access-key-id
AWS_SECRET_ACCESS_KEY=your-s3-secret-access-key
AWS_S3_BUCKET=x-video-hook-mem0-20251228193510
AWS_REGION=us-east-1
```

4. Click **Save Changes** - Render will auto-redeploy

### Step 2: Verify

After deployment, check logs. You should see:
```
[Bedrock] Using separate Bedrock AWS credentials (BEDROCK_AWS_ACCESS_KEY_ID)
[Bedrock] OK Bedrock service initialized (region: us-east-1)
[Bedrock] Using Claude via AWS Bedrock
```

**No more Bedrock access denied errors!**

### How It Works

- **S3 operations** use: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` (your S3 user)
- **Bedrock operations** use: `BEDROCK_AWS_ACCESS_KEY_ID` / `BEDROCK_AWS_SECRET_ACCESS_KEY` (Bedrock user)
- If Bedrock credentials aren't set, it falls back to regular AWS credentials

---

## Step-by-Step: Add Claude API Key

### 1. Get Your Anthropic API Key

1. Go to: https://console.anthropic.com/
2. Sign in or create account
3. Go to **API Keys** section
4. Click **Create Key**
5. Copy the key (starts with `sk-ant-...`)

### 2. Add to Render

1. Go to Render Dashboard → Your Backend Service → **Environment**
2. Click **Add Environment Variable**
3. Key: `ANTHROPIC_API_KEY`
4. Value: `sk-ant-...` (your key)
5. Click **Save Changes**
6. Render will auto-redeploy

### 3. Verify

After deployment, check logs. You should see:
- Bedrock errors (expected, since no Bedrock access)
- Anthropic Claude API working (no more "invalid x-api-key" errors)
- Or OpenAI fallback working

---

## Summary

**✅ IMPLEMENTED: Separate Bedrock Credentials**

The code now supports separate Bedrock credentials. Just add to Render:

```
BEDROCK_AWS_ACCESS_KEY_ID=your-bedrock-access-key-id
BEDROCK_AWS_SECRET_ACCESS_KEY=your-bedrock-secret-access-key
BEDROCK_AWS_REGION=us-east-1
```

**Optional: Add Anthropic API Key (for fallback)**

If you also want Anthropic Claude API as a fallback:
1. Get key from: https://console.anthropic.com/
2. Add to Render: `ANTHROPIC_API_KEY=sk-ant-...`

The system will:
- ✅ Use Bedrock with separate credentials (primary)
- ✅ Fall back to Anthropic Claude API if Bedrock fails (if key is set)
- ✅ Fall back to OpenAI if both fail (already working)

