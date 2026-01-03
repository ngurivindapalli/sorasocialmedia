# S3 Setup: Separate AWS Accounts (Bedrock vs S3)

## 🎯 Situation

You have:
- **Bedrock access:** Via `noel-bedrock-user` (managed by someone else, different AWS account)
- **S3 bucket:** In YOUR OWN AWS account (`x-video-hook-mem0-20251228193510`)

**Solution:** Create a separate IAM user in YOUR AWS account specifically for S3 access.

## ✅ What You Need to Do

### 1. Identify Your AWS Account

1. Log into AWS Console: https://console.aws.amazon.com/
2. Click your account name (top right) to see:
   - Account email
   - Account ID
3. **This is YOUR account** - where your S3 bucket should be

### 2. Verify S3 Bucket Location

1. Go to S3 Console: https://s3.console.aws.amazon.com/s3/
2. Check if bucket `x-video-hook-mem0-20251228193510` exists
3. **If it exists:** Note which AWS account it's in
4. **If it doesn't exist:** Create it in YOUR AWS account

### 3. Create IAM User in YOUR AWS Account

**Follow the main guide (`S3_RENDER_ACCESS_SETUP.md`) but make sure:**

1. ✅ You're logged into **YOUR AWS account** (not the Bedrock account)
2. ✅ Create a **NEW IAM user** (e.g., `render-s3-access`)
3. ✅ Create IAM policy with S3 permissions
4. ✅ Attach policy to the NEW user
5. ✅ Create access keys for the NEW user

### 4. Use Separate Credentials in Render

**Render Environment Variables:**

```
# S3 Access (YOUR AWS account)
AWS_ACCESS_KEY_ID=your-new-s3-user-access-key
AWS_SECRET_ACCESS_KEY=your-new-s3-user-secret-key
AWS_S3_BUCKET=x-video-hook-mem0-20251228193510
AWS_REGION=us-east-1

# Bedrock (if needed separately - managed by someone else)
# Do NOT use Bedrock credentials for S3!
```

## 🔑 Key Points

1. **Separate Accounts:** Bedrock and S3 are in different AWS accounts
2. **Separate Users:** Use different IAM users for each service
3. **Separate Credentials:** Never mix Bedrock and S3 credentials
4. **Your Account:** S3 bucket must be in YOUR AWS account

## 📋 Quick Setup Steps

1. **Log into YOUR AWS account** (where S3 bucket is/will be)
2. **Create IAM user:** `render-s3-access` (or similar)
3. **Create IAM policy:** Copy from `S3_RENDER_ACCESS_SETUP.md` Step 3
4. **Attach policy** to the new user
5. **Create access keys** for the new user
6. **Update Render** with the NEW S3 credentials
7. **Verify bucket exists** in YOUR account (create if needed)

## ✅ Verification

After setup, check Render logs:

**Success:**
```
[S3] OK S3 service initialized (bucket: x-video-hook-mem0-20251228193510, region: us-east-1)
[Mem0] OK Mem0 service initialized with S3 (persistent) storage
```

**If you see errors:**
- Check you're using S3 credentials (not Bedrock)
- Verify bucket exists in YOUR AWS account
- Ensure IAM policy is attached to YOUR S3 user

## 🚨 Common Mistakes

1. ❌ Using Bedrock credentials for S3
2. ❌ Creating IAM user in wrong AWS account
3. ❌ Bucket in wrong AWS account
4. ❌ Mixing credentials between accounts

## 📚 Related Files

- `S3_RENDER_ACCESS_SETUP.md` - Complete setup guide
- `backend/services/s3_service.py` - S3 service implementation
- `backend/services/mem0_service.py` - Mem0 with S3 vectors

