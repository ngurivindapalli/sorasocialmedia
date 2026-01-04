# Migration Guide: Hyperspell → AWS S3 + Mem0

## Overview
This migration replaces Hyperspell with:
- **AWS S3**: For document/file storage
- **Mem0**: For memory and context management

## Implementation Status
✅ **Core services created** (S3Service, Mem0Service, MemoryService)
✅ **Drop-in replacement ready** - MemoryService matches HyperspellService interface
✅ **main.py updated** - Can switch between Hyperspell and new service via env var

## Setup Instructions

### 1. Install Dependencies
```bash
pip install boto3 mem0ai
```

### 2. Configure AWS S3
Set these environment variables in your `.env` file:
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

**Important**: Create the S3 bucket first:
```bash
aws s3 mb s3://your-bucket-name --region us-east-1
```

### 3. Configure Mem0
Mem0 will automatically use:
- **S3 Vectors** if AWS credentials are available
- **ChromaDB** (local) if AWS credentials are not available

For S3 Vectors, ensure your bucket has the necessary permissions.

### 4. Enable New Service
Set this in your `.env` file:
```env
USE_MEMORY_SERVICE=true
```

Or keep using Hyperspell (default):
```env
USE_MEMORY_SERVICE=false
```

## Migration Steps

### Step 1: Test with New Service
1. Set `USE_MEMORY_SERVICE=true`
2. Restart backend
3. Test document upload
4. Test memory storage/retrieval
5. Test context summaries

### Step 2: Data Migration (if needed)
If you have existing Hyperspell data to migrate:
1. Export data from Hyperspell
2. Use migration script (to be created) to import to Mem0
3. Upload documents to S3

### Step 3: Full Switch
Once tested and verified:
1. Set `USE_MEMORY_SERVICE=true` permanently
2. Remove Hyperspell dependency (optional)
3. Update any remaining references

## API Compatibility

The `MemoryService` provides the same interface as `HyperspellService`:
- ✅ `upload_document()` - Uses S3
- ✅ `add_text_memory()` - Uses Mem0
- ✅ `query_memories()` - Uses Mem0
- ✅ `get_all_memories_context()` - Uses Mem0
- ✅ `append_to_unified_brand_context()` - Uses Mem0
- ✅ `get_context_summary()` - Uses Mem0

## Cost Comparison

**Hyperspell**: Per-API-call pricing
**S3 + Mem0**: 
- S3: ~$0.023/GB storage + $0.0004/1000 requests
- Mem0: Free tier available, then usage-based

## Performance Notes

- **S3**: Fast uploads, scalable storage
- **Mem0**: Vector-based search, fast semantic queries
- **Latency**: Similar to Hyperspell for most operations

## Troubleshooting

### S3 Issues
- Check AWS credentials are correct
- Verify bucket exists and is accessible
- Check IAM permissions

### Mem0 Issues
- Check Mem0 installation: `pip install mem0ai`
- Verify vector database configuration
- Check logs for specific errors

## Rollback

To rollback to Hyperspell:
1. Set `USE_MEMORY_SERVICE=false`
2. Restart backend
3. Hyperspell will be used again

## Next Steps

1. ✅ Test document upload
2. ✅ Test memory storage
3. ✅ Test context retrieval
4. ⏳ Create data migration script (if needed)
5. ⏳ Performance benchmarking
6. ⏳ Full production deployment






