# Fixing Mem0 S3 Vectors Access Denied Error

## Current Error

```
[S3] ERROR: Access denied to bucket 'x-video-hook-mem0-20251228193510'. Check IAM permissions.
[Mem0] WARNING: Config initialization failed, trying simple init: An error occurred (AccessDeniedException) when calling the GetVectorBucket operation: User: arn:aws:iam::222634391096:user/render-s3-access is not authorized to perform: s3vectors:GetVectorBucket
```

## Solution: Update IAM Policy

The IAM policy needs additional S3 permissions for Mem0's vector operations. Update your existing policy:

### Step 1: Go to IAM Policy

1. AWS Console → IAM → Policies
2. Find `RenderS3AccessPolicy`
3. Click on it → Edit → Edit policy (JSON tab)

### Step 2: Replace with Updated Policy

Replace the entire JSON with this (includes additional permissions for Mem0):

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

### Step 3: Save Policy

1. Click "Next" → "Save changes"
2. The policy is automatically attached to your user (no need to re-attach)

### Step 4: Verify S3 Bucket Exists

**CRITICAL:** Make sure the bucket exists in YOUR AWS account:

1. Go to S3 Console: https://s3.console.aws.amazon.com/s3/
2. Check if bucket `x-video-hook-mem0-20251228193510` exists
3. **If it doesn't exist:**
   - Click "Create bucket"
   - Bucket name: `x-video-hook-mem0-20251228193510` (exact match, case-sensitive)
   - Region: `us-east-1`
   - Keep all default settings (Block Public Access enabled)
   - Click "Create bucket"

### Step 5: Wait and Check Render Logs

After updating the policy:
1. Wait 1-2 minutes for changes to propagate
2. Check Render logs (Render will auto-redeploy if needed)
3. Look for:

**Success:**
```
[S3] OK S3 service initialized (bucket: x-video-hook-mem0-20251228193510, region: us-east-1)
[Mem0] OK Mem0 service initialized with S3 (persistent) storage
```

## Additional Permissions Added

The updated policy includes:
- `s3:ListBucketMultipartUploads` - For large file uploads
- `s3:ListMultipartUploadParts` - For multipart operations
- `s3:AbortMultipartUpload` - To cancel failed uploads
- `s3:GetBucketLocation` - To verify bucket region
- `s3:GetObjectVersion` - For versioned objects

These are needed for Mem0's vector storage operations.

## If Still Not Working

If you still see errors after updating the policy:

1. **Verify bucket exists** in the correct AWS account (222634391096)
2. **Check policy is attached** to `render-s3-access` user
3. **Wait 2-3 minutes** for IAM changes to propagate
4. **Check bucket name** matches exactly (case-sensitive)
5. **Verify region** is `us-east-1`

## Alternative: Use ChromaDB (Temporary)

If S3 continues to have issues, Mem0 will fall back to ChromaDB, but this won't persist across deployments. For production, S3 is required.

