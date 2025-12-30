"""
AWS S3 Service - Document and file storage
Replaces Hyperspell document storage functionality
"""

import os
import boto3
from typing import Optional, Dict
from datetime import datetime
from botocore.exceptions import ClientError
import asyncio


class S3Service:
    """Service for interacting with AWS S3 for document storage"""
    
    def __init__(self, bucket_name: Optional[str] = None, region: Optional[str] = None):
        """
        Initialize S3 service
        
        Args:
            bucket_name: S3 bucket name (or from AWS_S3_BUCKET env var)
            region: AWS region (or from AWS_REGION env var, defaults to us-east-1)
        """
        self.bucket_name = bucket_name or os.getenv('AWS_S3_BUCKET')
        self.region = region or os.getenv('AWS_REGION', 'us-east-1')
        self.available = False
        
        # Check for AWS credentials
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if not aws_access_key or not aws_secret_key:
            print("[S3] AWS credentials not found. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
            return
        
        if not self.bucket_name:
            print("[S3] S3 bucket name not provided. Set AWS_S3_BUCKET environment variable.")
            return
        
        try:
            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            
            # Verify bucket exists and is accessible
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.available = True
            print(f"[S3] OK S3 service initialized (bucket: {self.bucket_name}, region: {self.region})")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"[S3] ERROR: Bucket '{self.bucket_name}' not found. Please create it first.")
            elif error_code == '403':
                print(f"[S3] ERROR: Access denied to bucket '{self.bucket_name}'. Check IAM permissions.")
            else:
                print(f"[S3] ERROR: Error initializing S3 service: {e}")
            self.available = False
        except Exception as e:
            print(f"[S3] ERROR: Error initializing S3 service: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if S3 service is available"""
        return self.available
    
    async def upload_file(
        self,
        file_path: str,
        s3_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Upload a file to S3
        
        Args:
            file_path: Local file path to upload
            s3_key: S3 object key (path in bucket)
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            Dict with upload info (bucket, key, etag) or None if failed
        """
        if not self.available:
            print("[S3] Service not available for file upload")
            return None
        
        try:
            def upload_sync():
                extra_args = {}
                if content_type:
                    extra_args['ContentType'] = content_type
                if metadata:
                    extra_args['Metadata'] = {str(k): str(v) for k, v in metadata.items()}
                
                self.s3_client.upload_file(
                    file_path,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args if extra_args else None
                )
                
                # Get object info
                response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                return {
                    'bucket': self.bucket_name,
                    'key': s3_key,
                    'etag': response.get('ETag', '').strip('"'),
                    'size': response.get('ContentLength', 0),
                    'content_type': response.get('ContentType', content_type),
                    'uploaded_at': datetime.now().isoformat()
                }
            
            result = await asyncio.to_thread(upload_sync)
            print(f"[S3] OK File uploaded: s3://{self.bucket_name}/{s3_key}")
            return result
            
        except Exception as e:
            print(f"[S3] ERROR: Error uploading file: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def upload_file_content(
        self,
        file_content: bytes,
        s3_key: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Upload file content (bytes) directly to S3
        
        Args:
            file_content: File content as bytes
            s3_key: S3 object key (path in bucket)
            content_type: MIME type of the file
            metadata: Optional metadata dictionary
            
        Returns:
            Dict with upload info or None if failed
        """
        if not self.available:
            print("[S3] Service not available for file upload")
            return None
        
        try:
            def upload_sync():
                extra_args = {}
                if content_type:
                    extra_args['ContentType'] = content_type
                if metadata:
                    extra_args['Metadata'] = {str(k): str(v) for k, v in metadata.items()}
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=file_content,
                    **extra_args
                )
                
                # Get object info
                response = self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
                return {
                    'bucket': self.bucket_name,
                    'key': s3_key,
                    'etag': response.get('ETag', '').strip('"'),
                    'size': response.get('ContentLength', 0),
                    'content_type': response.get('ContentType', content_type),
                    'uploaded_at': datetime.now().isoformat()
                }
            
            result = await asyncio.to_thread(upload_sync)
            print(f"[S3] OK File content uploaded: s3://{self.bucket_name}/{s3_key}")
            return result
            
        except Exception as e:
            print(f"[S3] ERROR: Error uploading file content: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_file_url(self, s3_key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for accessing a file
        
        Args:
            s3_key: S3 object key
            expires_in: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.available:
            return None
        
        try:
            def generate_url_sync():
                return self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': s3_key},
                    ExpiresIn=expires_in
                )
            
            url = await asyncio.to_thread(generate_url_sync)
            return url
        except Exception as e:
            print(f"[S3] ERROR: Error generating presigned URL: {e}")
            return None
    
    async def delete_file(self, s3_key: str) -> bool:
        """
        Delete a file from S3
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False
        
        try:
            def delete_sync():
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            
            await asyncio.to_thread(delete_sync)
            print(f"[S3] OK File deleted: s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            print(f"[S3] ERROR: Error deleting file: {e}")
            return False
    
    def get_s3_path(self, user_id: str, filename: str, folder: str = "documents") -> str:
        """
        Generate S3 key path for a user's file
        
        Args:
            user_id: User identifier (email)
            filename: Original filename
            folder: Folder name (documents, images, etc.)
            
        Returns:
            S3 key path
        """
        # Sanitize user_id and filename
        safe_user_id = user_id.lower().strip().replace('@', '_at_').replace('.', '_')
        safe_filename = filename.replace(' ', '_')
        
        # Include timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return f"{folder}/{safe_user_id}/{timestamp}_{safe_filename}"

