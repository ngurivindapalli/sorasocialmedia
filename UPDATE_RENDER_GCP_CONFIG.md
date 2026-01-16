# Update Render Environment Variables for New GCP Project

## Overview
After changing your Google Cloud Platform (GCP) project, you need to update the following environment variables in your Render deployment.

## Required Environment Variables

### 1. GOOGLE_CLOUD_PROJECT_ID (REQUIRED)
- **Key:** `GOOGLE_CLOUD_PROJECT_ID`
- **Value:** Your new GCP project ID (e.g., `ordinal-idea-484320-j9`)
- **Purpose:** Identifies which Google Cloud project to use for Veo 3 and image generation
- **Where to find:** In your GCP Console → Project Settings, or in your service account JSON file as `project_id`

### 2. GOOGLE_SERVICE_ACCOUNT_JSON (REQUIRED)
- **Key:** `GOOGLE_SERVICE_ACCOUNT_JSON`
- **Value:** The **ENTIRE** JSON content from your new service account key file
- **Format:** Should be a complete JSON object starting with `{` and ending with `}`
- **Purpose:** Authenticates your application with Google Cloud services
- **Important:** 
  - Copy the ENTIRE JSON content (all fields including `private_key`, `client_email`, etc.)
  - Do NOT use file paths - paste the actual JSON content
  - Make sure there are no line breaks or formatting issues

### 3. VEO3_STORAGE_URI (REQUIRED for Video Extensions)
- **Key:** `VEO3_STORAGE_URI`
- **Value:** Your Google Cloud Storage bucket URI (e.g., `gs://your-bucket-name/videos/`)
- **Format:** `gs://bucket-name/path/`
- **Purpose:** Stores video files for Veo 3 extensions
- **Example:** `gs://ordinal-idea-484320-j9-veo3-videos/videos/`
- **Note:** Make sure the bucket exists and the service account has Storage Admin permissions

### 4. VEO3_USE_VERTEX_AI (Optional)
- **Key:** `VEO3_USE_VERTEX_AI`
- **Value:** `true` or `false` (default: `false`)
- **Purpose:** Enables Vertex AI mode for Veo 3 (recommended)
- **Set to:** `true` if you're using Vertex AI with service account authentication

### 5. GOOGLE_CLOUD_LOCATION (Optional)
- **Key:** `GOOGLE_CLOUD_LOCATION`
- **Value:** Your GCP region (default: `us-central1`)
- **Purpose:** Specifies which region to use for Vertex AI services
- **Common values:** `us-central1`, `us-east1`, `europe-west1`, etc.

## Step-by-Step Instructions for Render

1. **Go to Render Dashboard**
   - Navigate to https://dashboard.render.com
   - Select your backend service (e.g., `sorasocialmedia-backend`)

2. **Open Environment Tab**
   - Click on the **"Environment"** tab in your service settings

3. **Update/Add Environment Variables**

   **a. Update GOOGLE_CLOUD_PROJECT_ID:**
   - Find `GOOGLE_CLOUD_PROJECT_ID` in the list
   - Click on it to edit
   - Update the value to your new project ID
   - Click "Save"

   **b. Update GOOGLE_SERVICE_ACCOUNT_JSON:**
   - Find `GOOGLE_SERVICE_ACCOUNT_JSON` in the list
   - Click on it to edit
   - Replace the entire value with your new service account JSON
   - **Important:** Copy the complete JSON from your service account key file
   - Click "Save"

   **c. Update VEO3_STORAGE_URI:**
   - Find `VEO3_STORAGE_URI` (or add it if it doesn't exist)
   - Update to: `gs://your-new-bucket-name/videos/`
   - Make sure the bucket exists in your new GCP project
   - Click "Save"

   **d. Update VEO3_USE_VERTEX_AI (if needed):**
   - Find `VEO3_USE_VERTEX_AI`
   - Set to: `true` (recommended for Vertex AI mode)
   - Click "Save"

4. **Remove Old/Invalid Variables (if any):**
   - If `GOOGLE_APPLICATION_CREDENTIALS` has a file path (like `C:\Users\...`), **DELETE IT**
   - If `VEO3_API_KEY` exists and is expired, **DELETE IT**
   - These are not needed when using `GOOGLE_SERVICE_ACCOUNT_JSON`

5. **Save and Deploy**
   - Click **"Save Changes"** or **"Save, rebuild, and deploy"**
   - Wait for the deployment to complete (usually 2-5 minutes)

## Verification

After deployment, check your Render logs. You should see:

```
[Veo3] Veo 3 service initialized (Google Cloud Vertex AI)
[Veo3]   Project ID: your-new-project-id
[Veo3]   Location: us-central1
[Veo3]   Auth: Service Account (from GOOGLE_SERVICE_ACCOUNT_JSON)
```

If you see errors, verify:
- ✅ `GOOGLE_CLOUD_PROJECT_ID` matches your new project ID
- ✅ `GOOGLE_SERVICE_ACCOUNT_JSON` contains the complete JSON (all fields)
- ✅ `VEO3_STORAGE_URI` points to a valid GCS bucket in your new project
- ✅ Service account has required permissions (Vertex AI User, Storage Admin)

## Common Issues

### Error: "GOOGLE_CLOUD_PROJECT_ID not set"
**Solution:** Add `GOOGLE_CLOUD_PROJECT_ID` with your new project ID

### Error: "Service account key file not found"
**Solution:** Make sure `GOOGLE_SERVICE_ACCOUNT_JSON` contains the full JSON content (not a file path)

### Error: "401 Unauthorized"
**Solution:** 
- Verify `GOOGLE_SERVICE_ACCOUNT_JSON` has all fields including `private_key`
- Check that the service account has proper IAM roles in GCP

### Error: "Bucket not found" or "Storage URI invalid"
**Solution:**
- Verify `VEO3_STORAGE_URI` format: `gs://bucket-name/videos/`
- Make sure the bucket exists in your new GCP project
- Ensure service account has "Storage Admin" role on the bucket

## Quick Checklist

Before deploying, make sure you have:
- [ ] New GCP project ID
- [ ] New service account JSON (complete file content)
- [ ] GCS bucket created in new project
- [ ] Service account has required permissions:
  - [ ] Vertex AI User
  - [ ] Storage Admin (on the bucket)
- [ ] Updated all environment variables in Render
- [ ] Removed old/invalid variables

## Need Help?

If you encounter issues:
1. Check Render logs for specific error messages
2. Verify your service account JSON is valid JSON
3. Test GCP authentication locally first
4. Ensure all GCP APIs are enabled in your new project:
   - Vertex AI API
   - Cloud Storage API
