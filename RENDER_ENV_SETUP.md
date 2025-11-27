# Render Environment Variables Setup - Complete Guide

## Required Environment Variables for Image Generation

Based on your service account JSON, you need to add these to Render:

### 1. GOOGLE_CLOUD_PROJECT_ID (REQUIRED)
- **Key:** `GOOGLE_CLOUD_PROJECT_ID`
- **Value:** `igvideogen`
- **Why:** This is your Google Cloud project ID (found in your service account JSON)

### 2. GOOGLE_SERVICE_ACCOUNT_JSON (REQUIRED)
- **Key:** `GOOGLE_SERVICE_ACCOUNT_JSON`
- **Value:** Paste the ENTIRE JSON content from your service account file
- **Format:** Should start with `{` and end with `}`
- **Example:**
```json
{"type": "service_account", "project_id": "igvideogen", "private_key_id": "65c321c145188bcbb69dddc2c5cb1613047c390a", "private_key": "-----BEGIN PRIVATE KEY-----\n...", "client_email": "vertex-ai-user@igvideogen.iam.gserviceaccount.com", ...}
```

### 3. Remove/Update These (if present):
- **GOOGLE_APPLICATION_CREDENTIALS** - Remove if it has Windows path like `C:\Users\...`
- **VEO3_API_KEY** - Remove if expired (causing 401 errors)

## Step-by-Step Instructions

1. **Go to Render Dashboard** → Your Backend Service → **Environment** tab

2. **Add GOOGLE_CLOUD_PROJECT_ID:**
   - Click "+ Add" button
   - Key: `GOOGLE_CLOUD_PROJECT_ID`
   - Value: `igvideogen`
   - Click "Add"

3. **Add GOOGLE_SERVICE_ACCOUNT_JSON:**
   - Click "+ Add" button
   - Key: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Value: Paste your ENTIRE service account JSON (from the file you showed)
   - **Important:** Copy the entire JSON, including all the `{` and `}` and all fields
   - Click "Add"

4. **Remove problematic variables (if they exist):**
   - If `GOOGLE_APPLICATION_CREDENTIALS` has a Windows path → Delete it
   - If `VEO3_API_KEY` is expired → Delete it

5. **Save and Deploy:**
   - Click "Save, rebuild, and deploy" button
   - Wait for deployment to complete

## Verification

After deployment, check the logs. You should see:
```
[ImageGen] ✓ Gemini 3 Pro Image initialized via Vertex AI
[ImageGen]   Project ID: igvideogen
[ImageGen]   Location: us-central1
```

If you see errors, check:
- Is `GOOGLE_CLOUD_PROJECT_ID` set to `igvideogen`?
- Is `GOOGLE_SERVICE_ACCOUNT_JSON` set with the full JSON content?
- Did you remove the Windows path from `GOOGLE_APPLICATION_CREDENTIALS`?

## Troubleshooting

**Error: "GOOGLE_CLOUD_PROJECT_ID not set"**
→ Add `GOOGLE_CLOUD_PROJECT_ID` = `igvideogen`

**Error: "Service account key file not found"**
→ Add `GOOGLE_SERVICE_ACCOUNT_JSON` with full JSON content

**Error: "401 Unauthorized"**
→ Make sure `GOOGLE_SERVICE_ACCOUNT_JSON` has the complete JSON (all fields including private_key)

