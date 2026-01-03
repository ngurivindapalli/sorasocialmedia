# S3 Access Setup for Render - Complete Guide

## 🎯 Goal
Grant Render backend access to your S3 bucket: `x-video-hook-mem0-20251228193510`

## ⚠️ Important: Separate AWS Accounts

**If you're using `noel-bedrock-user` for Bedrock (managed by someone else), you need to create a separate IAM user in YOUR OWN AWS account for S3 access.**

This guide assumes:
- ✅ **Bedrock access:** Uses `noel-bedrock-user` (managed by someone else) - **DO NOT use these credentials for S3**
- ✅ **S3 access:** You'll create a new IAM user in **YOUR OWN AWS account** for S3 bucket access

## 📋 Step-by-Step Instructions

### Step 1: Log into YOUR AWS Account

1. Visit: https://console.aws.amazon.com/
2. **Log in with YOUR AWS account** (the one that owns/manages the S3 bucket)
3. Make sure you're in the correct AWS account (not the Bedrock account)
4. Go to: https://console.aws.amazon.com/iam/
5. Click **Users** in the left sidebar

### Step 2: Create New IAM User for S3 Access

**⚠️ DO NOT use `noel-bedrock-user` - that's for Bedrock only and managed by someone else.**

1. Click **Create user**
2. **User name:** `render-s3-access` (or any name you prefer, e.g., `s3-memory-storage`)
3. **Access type:** Select **"Access key - Programmatic access"**
4. Click **Next: Permissions**

### Step 3: Create IAM Policy for S3 Access

1. In IAM Console, click **Policies** in the left sidebar
2. Click **Create policy**
3. Click **JSON** tab
4. **Replace the entire JSON** with this policy:

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
        }
    ]
}
```

5. Click **Next**
6. **Policy name:** `RenderS3AccessPolicy` (or any name)
7. **Description:** `Allows Render backend to access S3 bucket for memory storage`
8. Click **Create policy**

### Step 4: Attach Policy to IAM User

1. Go back to **Users** → Click on your user (or the one you just created)
2. Click **Add permissions** → **Attach policies directly**
3. Search for `RenderS3AccessPolicy` (or the name you used)
4. Check the box next to it
5. Click **Add permissions**

### Step 5: Get Access Keys

**If you created a new user:**

1. Go to **Users** → Click on your user
2. Click **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. **Use case:** Select **"Application running outside AWS"**
6. Click **Next** → **Create access key**
7. **IMPORTANT:** Copy both:
   - **Access key ID**
   - **Secret access key** (you won't see this again!)

**If using existing user:**

1. Go to **Users** → Click on your user
2. Click **Security credentials** tab
3. If you already have access keys, you can use those
4. If not, create new ones (see above)

### Step 6: Update Render Environment Variables

**⚠️ IMPORTANT: Use the NEW S3 credentials, NOT the Bedrock credentials!**

1. Go to **Render Dashboard** → Your Backend Service → **Environment**
2. Update or add these variables with your **NEW S3 IAM user credentials**:

```
AWS_ACCESS_KEY_ID=your-new-s3-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-new-s3-secret-access-key-here
AWS_S3_BUCKET=x-video-hook-mem0-20251228193510
AWS_REGION=us-east-1
```

**Note:** These are DIFFERENT from any Bedrock credentials you might have. The S3 credentials are for YOUR AWS account, not the Bedrock account.

3. Click **Save Changes**
4. Render will automatically redeploy

### Step 7: Verify S3 Bucket Exists

1. Go to **S3 Console**: https://s3.console.aws.amazon.com/s3/
2. Check if bucket `x-video-hook-mem0-20251228193510` exists
3. If it doesn't exist:
   - Click **Create bucket**
   - **Bucket name:** `x-video-hook-mem0-20251228193510`
   - **Region:** `us-east-1`
   - **Block Public Access:** Keep enabled (default)
   - Click **Create bucket**

### Step 8: Verify Access

After Render redeploys, check the logs for:

**Success:**
```
[S3] OK S3 service initialized (bucket: x-video-hook-mem0-20251228193510, region: us-east-1)
[Mem0] OK Mem0 service initialized with S3 (persistent) storage
```

**If you still see errors:**
- Check that IAM policy is attached to the user
- Verify bucket name matches exactly
- Ensure region is `us-east-1`

## 🔒 Security Best Practices

### Minimal Permissions Policy

The policy above only grants:
- ✅ `s3:PutObject` - Upload files
- ✅ `s3:GetObject` - Download files (also covers HeadObject operations)
- ✅ `s3:DeleteObject` - Delete files
- ✅ `s3:ListBucket` - List files in bucket (also covers HeadBucket operations)

**No other AWS services are accessible** - this is secure!

### Additional Security (Optional)

If you want even more security, you can restrict to specific prefixes:

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
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::x-video-hook-mem0-20251228193510",
                "arn:aws:s3:::x-video-hook-mem0-20251228193510/documents/*",
                "arn:aws:s3:::x-video-hook-mem0-20251228193510/vectors/*"
            ]
        }
    ]
}
```

## 🐛 Troubleshooting

### Error: "Access denied to bucket"

**Possible causes:**
1. Using Bedrock credentials instead of S3 credentials
2. IAM policy not attached to user
3. Wrong bucket name
4. Wrong region
5. Access keys not updated in Render
6. Logged into wrong AWS account

**Fix:**
1. **Verify you're using S3 credentials, NOT Bedrock credentials** in Render
2. Make sure you're logged into YOUR AWS account (the one with the S3 bucket)
3. Verify policy is attached: IAM → Users → Your S3 User → Permissions
4. Check bucket name matches exactly (case-sensitive)
5. Verify region is `us-east-1`
6. Update Render environment variables with the NEW S3 user's access keys
7. Ensure the S3 bucket exists in YOUR AWS account, not the Bedrock account

### Error: "Bucket not found"

**Fix:**
1. Create the bucket in S3 Console
2. Name must be exactly: `x-video-hook-mem0-20251228193510`
3. Region must be: `us-east-1`

### Error: "Invalid credentials"

**Fix:**
1. Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in Render
2. Make sure no extra spaces or quotes
3. Create new access keys if needed

## 📝 Quick Checklist

- [ ] Logged into YOUR AWS account (not the Bedrock account)
- [ ] New IAM user created for S3 access (e.g., `render-s3-access`)
- [ ] IAM policy created with S3 permissions
- [ ] Policy attached to the NEW S3 IAM user
- [ ] Access keys created/copied for the NEW S3 IAM user
- [ ] S3 bucket exists in YOUR AWS account: `x-video-hook-mem0-20251228193510`
- [ ] Bucket region: `us-east-1`
- [ ] Environment variables set in Render with NEW S3 credentials:
  - [ ] `AWS_ACCESS_KEY_ID` (from NEW S3 user, NOT Bedrock user)
  - [ ] `AWS_SECRET_ACCESS_KEY` (from NEW S3 user, NOT Bedrock user)
  - [ ] `AWS_S3_BUCKET=x-video-hook-mem0-20251228193510`
  - [ ] `AWS_REGION=us-east-1`
- [ ] Render service redeployed
- [ ] Logs show: `[S3] OK S3 service initialized`

## 🎉 Success Indicators

After setup, you should see in Render logs:

```
[S3] OK S3 service initialized (bucket: x-video-hook-mem0-20251228193510, region: us-east-1)
[Mem0] OK Mem0 service initialized with S3 (persistent) storage
```

**No more errors!** Your memories will now persist across deployments! 🚀

## 📚 Additional Resources

- [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html)
- [S3 Bucket Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html)
- [IAM Policy Examples](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_examples.html)


