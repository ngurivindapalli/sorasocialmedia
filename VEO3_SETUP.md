# Veo 3 Setup Guide - Google Cloud Vertex AI

This guide explains how to configure Veo 3 video generation using the official Google Cloud Vertex AI API.

## Reference Documentation

- [Google Cloud Veo Video Generation Documentation](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation)

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud Project**: Create or select a project in Google Cloud Console
3. **Vertex AI API**: Enable the Vertex AI API in your project
4. **Authentication**: Set up authentication (see below)

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your **Project ID** (not the project name)

### 2. Enable Vertex AI API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for "Vertex AI API"
3. Click **Enable**

### 2.5. Request Access to Veo 3 (IMPORTANT)

**⚠️ Veo 3 is currently in limited preview/early access and may not be available in all projects.**

If you get a `404 Model not found` error, you may need to:

1. **Check if Veo 3 is available in your project:**
   - Go to [Vertex AI Models](https://console.cloud.google.com/vertex-ai/models)
   - Look for "veo-3" or "Veo" in the list of available models
   - If it's not listed, you need to request access

2. **Request Access:**
   - Contact Google Cloud Support or your account representative
   - Request access to "Veo 3" or "Vertex AI Video Generation"
   - Mention that you need access to the `veo-3` model in Vertex AI

3. **Alternative: Use a different project:**
   - Some projects may have Veo 3 enabled by default
   - Try creating a new project or using a different existing project

4. **Check Region Availability:**
   - Veo 3 may only be available in specific regions
   - Currently supported regions: `us-central1` (default)
   - Check the [Vertex AI documentation](https://cloud.google.com/vertex-ai/docs) for the latest region availability

### 3. Set Up Authentication

**⚠️ Important:** Vertex AI requires OAuth 2.0 access tokens, NOT API keys. API keys will not work and will result in `401 API_KEY_SERVICE_BLOCKED` errors.

You have two options for authentication:

#### Option A: Using gcloud CLI (Recommended for Development)

1. Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
2. Authenticate:
   ```bash
   gcloud auth login
   ```
3. Set your project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

4. In your `backend/.env` file, add:
   ```env
   GOOGLE_CLOUD_PROJECT_ID=your-project-id
   VEO3_USE_GCLOUD_AUTH=true
   ```

#### Option B: Using Service Account (Recommended for Production)

1. In Google Cloud Console, go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Give it a name (e.g., "veo3-service")
4. Grant it the **Vertex AI User** role
5. Create a JSON key:
   - Click on the service account
   - Go to **Keys** tab
   - Click **Add Key** > **Create new key**
   - Choose **JSON** format
   - Download the key file

6. In your `backend/.env` file, add:
   ```env
   GOOGLE_CLOUD_PROJECT_ID=your-project-id
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
   ```

### 4. Configure Environment Variables

Add these to your `backend/.env` file:

```env
# Required
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here

# Authentication (choose one):
# Option 1: Service Account JSON file (Recommended)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Option 2: gcloud CLI
# VEO3_USE_GCLOUD_AUTH=true

# Note: VEO3_API_KEY does NOT work with Vertex AI - use service account or gcloud CLI instead

# Optional - defaults shown
GOOGLE_CLOUD_LOCATION=us-central1
VEO3_MODEL_ID=veo-3

# Optional - for storing videos in Google Cloud Storage
VEO3_STORAGE_URI=gs://your-bucket-name/path/to/videos
```

## API Usage

### Text-to-Video

```python
result = await veo3_service.generate_video(
    prompt="A beautiful sunset over the ocean",
    duration=8,  # seconds (typically 5 or 10)
    resolution="1280x720"  # or "1920x1080"
)
```

### Image-to-Video

```python
result = await veo3_service.generate_video(
    prompt="A beautiful sunset over the ocean",
    duration=8,
    resolution="1280x720",
    image_urls=["https://example.com/image.jpg"]
)
```

### Check Status

```python
status = await veo3_service.get_video_status(job_id)
# Returns: {"status": "running" or "completed", "video_urls": [...], ...}
```

### Download Video

```python
video_bytes = await veo3_service.download_video(video_url)
```

## Supported Resolutions and Aspect Ratios

The API supports these aspect ratios:
- `9:16` - Vertical/Portrait (e.g., 1080x1920)
- `16:9` - Horizontal/Landscape (e.g., 1920x1080, 1280x720)
- `1:1` - Square (e.g., 1080x1080)
- `4:3` - Traditional (e.g., 1920x1440)
- `21:9` - Ultra-wide

The service automatically converts resolution strings (e.g., "1280x720") to the closest supported aspect ratio.

## API Endpoints

### POST `/api/veo3/generate`
Generate a video using Veo 3

**Request:**
```json
{
  "prompt": "A beautiful sunset",
  "duration": 8,
  "resolution": "1280x720",
  "image_urls": ["https://example.com/image.jpg"],  // optional
  "style": "cinematic"  // optional
}
```

### GET `/api/veo3/status/{job_id}`
Check the status of a video generation job

### GET `/api/veo3/download/{job_id}`
Download a completed video

## Troubleshooting

### Error: "GOOGLE_CLOUD_PROJECT_ID not set"
- Make sure you've set `GOOGLE_CLOUD_PROJECT_ID` in your `.env` file
- Restart the backend server after changing `.env`

### Error: "Failed to get access token from gcloud CLI"
- Make sure `gcloud` is installed and in your PATH
- Run `gcloud auth login` to authenticate
- Set `VEO3_USE_GCLOUD_AUTH=true` in your `.env`

### Error: "API endpoint not found" or 404
- Make sure Vertex AI API is enabled in your Google Cloud project
- Check that your Project ID is correct
- Verify you have the necessary permissions

### Error: "Permission denied"
- Make sure your account/service account has the **Vertex AI User** role
- For service accounts, ensure the JSON key file path is correct

## Cost Considerations

- Veo 3 video generation is billed per second of generated video
- Check [Google Cloud Pricing](https://cloud.google.com/vertex-ai/pricing) for current rates
- Consider using GCS storage (`VEO3_STORAGE_URI`) for better cost management

## Notes

- Video generation is a long-running operation (can take several minutes)
- The API returns an operation ID that you must poll to check status
- Videos can be stored in Google Cloud Storage or returned as base64-encoded data
- The service automatically handles aspect ratio conversion from resolution strings

