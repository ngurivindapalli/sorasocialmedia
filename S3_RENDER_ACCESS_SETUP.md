# S3 Access Setup for Render - Complete Guide

## 🎯 Goal
Grant Render backend access to your S3 bucket: `x-video-hook-mem0-20251228193510`

## 📋 Step-by-Step Instructions

### Step 1: Go to AWS IAM Console

1. Visit: https://console.aws.amazon.com/iam/
2. Make sure you're in the correct AWS account
3. Click **Users** in the left sidebar

### Step 2: Create or Use Existing IAM User

**Option A: Create New IAM User (Recommended)**

1. Click **Create user**
2. **User name:** `render-s3-access` (or any name you prefer)
3. **Access type:** Select **"Access key - Programmatic access"**
4. Click **Next: Permissions**

**Option B: Use Existing User**

1. Find your existing IAM user (the one with `AWS_ACCESS_KEY_ID` you're using)
2. Click on the user name
3. Go to **Permissions** tab
4. Skip to Step 3

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
                "s3:HeadBucket",
                "s3:HeadObject"
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

1. Go to **Render Dashboard** → Your Backend Service → **Environment**
2. Update or add these variables:

```
AWS_ACCESS_KEY_ID=your-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-secret-access-key-here
AWS_S3_BUCKET=x-video-hook-mem0-20251228193510
AWS_REGION=us-east-1
```

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
- ✅ `s3:GetObject` - Download files
- ✅ `s3:DeleteObject` - Delete files
- ✅ `s3:ListBucket` - List files in bucket
- ✅ `s3:HeadBucket` - Check if bucket exists
- ✅ `s3:HeadObject` - Get file metadata

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
                "s3:ListBucket",
                "s3:HeadBucket",
                "s3:HeadObject"
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
1. IAM policy not attached to user
2. Wrong bucket name
3. Wrong region
4. Access keys not updated in Render

**Fix:**
1. Verify policy is attached: IAM → Users → Your User → Permissions
2. Check bucket name matches exactly (case-sensitive)
3. Verify region is `us-east-1`
4. Update Render environment variables with correct keys

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

- [ ] IAM user created (or existing user identified)
- [ ] IAM policy created with S3 permissions
- [ ] Policy attached to IAM user
- [ ] Access keys created/copied
- [ ] S3 bucket exists: `x-video-hook-mem0-20251228193510`
- [ ] Bucket region: `us-east-1`
- [ ] Environment variables set in Render:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
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

