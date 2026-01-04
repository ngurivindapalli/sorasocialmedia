# Fix Mem0 S3 Vectors IAM Policy

## 🔴 Problem

```
s3vectors:GetVectorBucket operation: User: arn:aws:iam::222634391096:user/render-s3-access is not authorized to perform: s3vectors:GetVectorBucket
```

**Root Cause:** Mem0 uses **Amazon S3 Vectors** (a separate AWS service), not regular S3. The IAM policy needs `s3vectors:*` permissions, not just `s3:*`.

## 🔧 Solution: Update IAM Policy

### Step 1: Go to IAM Policy

1. AWS Console → IAM → Policies
2. Find your policy (e.g., `RenderS3AccessPolicy`)
3. Click on it → **Edit** → **Edit policy** (JSON tab)

### Step 2: Add S3 Vectors Permissions

**Add this statement to your existing policy:**

```json
{
    "Sid": "S3VectorsAccess",
    "Effect": "Allow",
    "Action": [
        "s3vectors:CreateVectorBucket",
        "s3vectors:PutVectorBucketPolicy",
        "s3vectors:DeleteVectorBucket",
        "s3vectors:DeleteVectorBucketPolicy",
        "s3vectors:GetVectorBucket",
        "s3vectors:GetVectorBucketPolicy",
        "s3vectors:ListVectorBuckets",
        "s3vectors:CreateIndex",
        "s3vectors:DeleteIndex",
        "s3vectors:GetIndex",
        "s3vectors:ListIndexes",
        "s3vectors:DeleteVectors",
        "s3vectors:GetVectors",
        "s3vectors:ListVectors",
        "s3vectors:PutVectors",
        "s3vectors:QueryVectors"
    ],
    "Resource": "*"
}
```

### Step 3: Complete Policy Example

**Full policy with both S3 and S3 Vectors permissions:**

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
            "Sid": "S3VectorsAccess",
            "Effect": "Allow",
            "Action": [
                "s3vectors:CreateVectorBucket",
                "s3vectors:PutVectorBucketPolicy",
                "s3vectors:DeleteVectorBucket",
                "s3vectors:DeleteVectorBucketPolicy",
                "s3vectors:GetVectorBucket",
                "s3vectors:GetVectorBucketPolicy",
                "s3vectors:ListVectorBuckets",
                "s3vectors:CreateIndex",
                "s3vectors:DeleteIndex",
                "s3vectors:GetIndex",
                "s3vectors:ListIndexes",
                "s3vectors:DeleteVectors",
                "s3vectors:GetVectors",
                "s3vectors:ListVectors",
                "s3vectors:PutVectors",
                "s3vectors:QueryVectors"
            ],
            "Resource": "*"
        }
    ]
}
```

### Step 4: Save Policy

1. Click **Next** → **Save changes**
2. Policy is automatically attached to your user

### Step 5: Wait for Propagation

1. Wait **2-3 minutes** for IAM changes to propagate
2. Restart Render service (or wait for auto-redeploy)
3. Check logs for success

## ✅ Success Indicators

After updating the policy, you should see in Render logs:

```
[Mem0] ✅ Successfully initialized with config
[Mem0] ✅ S3 bucket access verified: x-video-hook-mem0-20251228193510
[Mem0] OK Mem0 service initialized with S3 (persistent) storage
```

**NOT:**
```
[Mem0] WARNING: Config initialization failed
[Mem0] ❌ CRITICAL: S3 vector initialization failed!
```

## 📝 Important Notes

1. **S3 Vectors is a separate service** from regular S3
2. **Both permissions are needed:**
   - `s3:*` for regular S3 operations (documents, files)
   - `s3vectors:*` for Mem0 vector storage
3. **Resource: "*"** is needed for S3 Vectors (service-level permissions)
4. **Wait 2-3 minutes** after updating policy before testing

## 🔗 References

- [AWS S3 Vectors IAM Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-iam-policies.html)
- [Mem0 S3 Vectors Documentation](https://docs.mem0.ai/v0x/components/vectordbs/dbs/s3_vectors)

