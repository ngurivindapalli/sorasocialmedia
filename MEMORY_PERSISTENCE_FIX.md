# Fix Memory Persistence After Server Restart

## 🔴 Problem: Memories Lost After Restart

Memories are being lost when the Render server restarts. This means Mem0 is not using S3 vectors for persistent storage.

## 🔍 Diagnosis

Check your Render logs on startup. You should see one of these:

### ✅ **Correct (S3 Vectors):**
```
[Mem0] Using S3 vectors for persistent storage (survives deployments)
[Mem0] Configuring S3 vectors with bucket: x-video-hook-mem0-20251228193510 (region: us-east-1)
[Mem0] ✅ Successfully initialized with config
[Mem0] ✅ S3 bucket access verified: x-video-hook-mem0-20251228193510
[Mem0] OK Mem0 service initialized with S3 (persistent) storage
```

### ❌ **Wrong (ChromaDB - Local):**
```
[Mem0] Using ChromaDB (local) - AWS credentials not configured for S3 vectors
[Mem0] WARNING: Local ChromaDB will be lost on deployment. Configure AWS for persistent storage.
[Mem0] OK Mem0 service initialized with ChromaDB (local) storage
```

### ⚠️ **Error (S3 Failed):**
```
[Mem0] Using S3 vectors for persistent storage (survives deployments)
[Mem0] WARNING: Config initialization failed, trying simple init: ...
[Mem0] ❌ CRITICAL: S3 vector initialization failed! Memories will NOT persist.
```

## 🔧 Fix: Verify Render Environment Variables

### Required Environment Variables

Go to [Render Dashboard](https://dashboard.render.com/) → Your Backend Service → **Environment** tab.

**Must have ALL of these:**

```
AWS_ACCESS_KEY_ID=AKIATHVQLGY4P4S2JFJ4
AWS_SECRET_ACCESS_KEY=bb6+xf6XqKjW7KRX0m7gmS8Gc5lWcsjCCRROA6Za
AWS_S3_BUCKET=x-video-hook-mem0-20251228193510
AWS_REGION=us-east-1
```

### Verification Checklist

- [ ] `AWS_ACCESS_KEY_ID` is set (starts with `AKIA`)
- [ ] `AWS_SECRET_ACCESS_KEY` is set (long string)
- [ ] `AWS_S3_BUCKET` is set to `x-video-hook-mem0-20251228193510`
- [ ] `AWS_REGION` is set to `us-east-1`
- [ ] No extra spaces or quotes around values
- [ ] All variables are enabled for the correct environment

## 🚀 Steps to Fix

### Step 1: Check Current Environment Variables

1. Go to Render Dashboard
2. Select your backend service
3. Go to **Environment** tab
4. Verify all 4 AWS variables are present

### Step 2: Add Missing Variables

If any are missing, add them:

1. Click **"Add Environment Variable"**
2. Add each missing variable:
   - **Key:** `AWS_ACCESS_KEY_ID`
   - **Value:** Your access key (starts with `AKIA`)
   - **Key:** `AWS_SECRET_ACCESS_KEY`
   - **Value:** Your secret key
   - **Key:** `AWS_S3_BUCKET`
   - **Value:** `x-video-hook-mem0-20251228193510`
   - **Key:** `AWS_REGION`
   - **Value:** `us-east-1`
3. Click **Save Changes**

### Step 3: Restart Render Service

1. Go to **Manual Deploy** → **Clear build cache & deploy**
2. Wait for deployment to complete
3. Check logs for S3 initialization messages

### Step 4: Verify S3 Access

After restart, check logs for:

```
[Mem0] ✅ S3 bucket access verified: x-video-hook-mem0-20251228193510
```

If you see an error instead, check IAM permissions (see `S3_RENDER_ACCESS_SETUP.md`).

## 🐛 Troubleshooting

### "Using ChromaDB (local)" in Logs

**Cause:** AWS credentials not found

**Fix:**
1. Verify all 4 environment variables are set in Render
2. Check variable names are exact (case-sensitive)
3. Restart Render service

### "S3 vector initialization failed"

**Cause:** S3 bucket access denied or invalid credentials

**Fix:**
1. Verify IAM user has correct permissions (see `S3_RENDER_ACCESS_SETUP.md`)
2. Check bucket name is correct: `x-video-hook-mem0-20251228193510`
3. Verify region is `us-east-1`
4. Check AWS credentials are valid

### "Could not verify S3 bucket access"

**Cause:** IAM permissions issue

**Fix:**
1. Check IAM policy includes all required S3 permissions
2. Verify bucket exists in AWS Console
3. Check IAM user has access to the bucket

## ✅ Success Indicators

After fixing, you should see in logs:

1. ✅ `[Mem0] Using S3 vectors for persistent storage`
2. ✅ `[Mem0] ✅ Successfully initialized with config`
3. ✅ `[Mem0] ✅ S3 bucket access verified`
4. ✅ `[Mem0] OK Mem0 service initialized with S3 (persistent) storage`

## 🧪 Test Memory Persistence

1. **Add a memory:**
   - Upload a document or add text memory
   - Check logs: Should see `[Mem0] OK Memory added for user...`

2. **Restart Render:**
   - Go to Render Dashboard
   - Click **Manual Deploy** → **Clear build cache & deploy**

3. **Verify memory still exists:**
   - Query the same memory
   - Should still find it

## 📝 Quick Reference

**Environment Variables Needed:**
```
AWS_ACCESS_KEY_ID=your-aws-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key-here
AWS_S3_BUCKET=x-video-hook-mem0-20251228193510
AWS_REGION=us-east-1
```
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
run_terminal_cmd

**Expected Log Output:**
```
[Mem0] Using S3 vectors for persistent storage (survives deployments)
[Mem0] Configuring S3 vectors with bucket: x-video-hook-mem0-20251228193510 (region: us-east-1)
[Mem0] ✅ Successfully initialized with config
[Mem0] ✅ S3 bucket access verified: x-video-hook-mem0-20251228193510
[Mem0] OK Mem0 service initialized with S3 (persistent) storage
```

## 🔗 Related Files

- `backend/services/mem0_service.py` - Mem0 initialization
- `S3_RENDER_ACCESS_SETUP.md` - IAM permissions setup
- `RENDER_ENV_VARIABLES_COMPLETE.md` - All environment variables
