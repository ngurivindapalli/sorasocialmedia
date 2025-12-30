# Quick Setup Guide: AWS S3 + Mem0

## Step 1: Add AWS Credentials to .env

Add these lines to your `backend/.env` file:

```env
AWS_ACCESS_KEY_ID=your-aws-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key-here
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
USE_MEMORY_SERVICE=true
```

**Important**: Replace `your-bucket-name` with your actual S3 bucket name.

## Step 2: Create S3 Bucket

If you haven't created a bucket yet, run:

```bash
aws s3 mb s3://your-bucket-name --region us-east-1
```

Or create it via AWS Console: https://s3.console.aws.amazon.com/

## Step 3: Install Dependencies

```bash
pip install boto3 mem0ai
```

## Step 4: Restart Backend

The backend will automatically use S3 + Mem0 instead of Hyperspell.

## Quick Test

After restarting, you should see in the logs:
```
[S3] ✓ S3 service initialized (bucket: your-bucket-name, region: us-east-1)
[Mem0] ✓ Mem0 service initialized (vector_db: s3_vectors)
[Memory] ✓ Unified memory service initialized (S3 + Mem0)
[API] Using unified MemoryService (S3 + Mem0)
```

## Troubleshooting

If you see errors:
- **Bucket not found**: Create the bucket first
- **Access denied**: Check IAM permissions for your AWS credentials
- **Mem0 not installed**: Run `pip install mem0ai`



