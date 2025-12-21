# 🔑 Google Cloud Platform (GCP) Credentials Used

## Overview

Your project uses **Google Cloud Platform (GCP) Service Account** credentials to access:

1. **Vertex AI - Imagen** (Image Generation)
   - Model: `imagen-4.0-generate-001` (default)
   - Location: `us-central1` (required for Imagen 4)
   - API: `https://us-central1-aiplatform.googleapis.com/v1`

2. **Vertex AI - Veo 3** (Video Generation)
   - Model: `veo-3` (default)
   - Location: `us-central1` (default)
   - API: `https://us-central1-aiplatform.googleapis.com/v1`

---

## 🔐 Authentication Methods (Priority Order)

The project supports **3 authentication methods** (in priority order):

### 1. **Service Account JSON** (Recommended for Production)
- **Environment Variable:** `GOOGLE_SERVICE_ACCOUNT_JSON`
- **Format:** Full JSON content on one line
- **Use Case:** Render.com, Vercel, or any cloud deployment

### 2. **Service Account File Path** (Local Development)
- **Environment Variable:** `GOOGLE_APPLICATION_CREDENTIALS`
- **Format:** Path to JSON file (e.g., `./gcp-credentials.json`)
- **Use Case:** Local development on your machine

### 3. **gcloud CLI** (Alternative)
- **Environment Variable:** `VEO3_USE_GCLOUD_AUTH=true`
- **Requires:** `gcloud` CLI installed and authenticated
- **Use Case:** Local development with gcloud CLI

### 4. **Direct API Key** (Less Common)
- **Environment Variable:** `VEO3_API_KEY`
- **Format:** OAuth 2.0 access token
- **Use Case:** If you have a pre-generated access token

---

## 📋 Required Service Account Permissions

Your GCP service account needs these **IAM roles**:

### Minimum Required:
- **`Vertex AI User`** (`roles/aiplatform.user`)
  - Allows access to Vertex AI APIs (Imagen and Veo 3)

### Recommended (for full functionality):
- **`Vertex AI Service Agent`** (`roles/aiplatform.serviceAgent`)
  - Full access to Vertex AI services

### Alternative (if using Storage):
- **`Storage Object Admin`** (`roles/storage.objectAdmin`)
  - If you need to store/retrieve generated images/videos in Google Cloud Storage

### Full Access (Development):
- **`Editor`** (`roles/editor`)
  - Full project access (use only for development, not production)

---

## 🎯 Service Account Scope

The service account uses this **OAuth scope**:
```
https://www.googleapis.com/auth/cloud-platform
```

This scope provides access to:
- Vertex AI API (Imagen, Veo 3)
- Cloud Storage (if needed)
- Other Google Cloud Platform services

---

## 📝 How to Create/Get Your Service Account

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select your project (or create a new one)

### Step 2: Create Service Account
1. Navigate to **IAM & Admin** → **Service Accounts**
2. Click **"Create Service Account"**
3. Enter a name (e.g., `aigis-marketing-service`)
4. Click **"Create and Continue"**

### Step 3: Grant Permissions
1. In **"Grant this service account access to project"**, add:
   - **`Vertex AI User`** (`roles/aiplatform.user`)
   - (Optional) **`Storage Object Admin`** if using Cloud Storage
2. Click **"Continue"** → **"Done"**

### Step 4: Create Key
1. Click on your newly created service account
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Choose **JSON** format
5. Click **"Create"**
6. **The JSON file will download automatically** ⬇️

### Step 5: Use the Key
- **Local:** Save the file and set `GOOGLE_APPLICATION_CREDENTIALS=./path/to/key.json`
- **Production:** Copy the entire JSON content and set `GOOGLE_SERVICE_ACCOUNT_JSON` (all on one line)

---

## 🔍 What Your Service Account JSON Looks Like

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

---

## ✅ Verification Checklist

- [ ] Service account created in Google Cloud Console
- [ ] Service account has `Vertex AI User` role
- [ ] JSON key downloaded
- [ ] For local: `GOOGLE_APPLICATION_CREDENTIALS` points to JSON file
- [ ] For production: `GOOGLE_SERVICE_ACCOUNT_JSON` contains full JSON (one line)
- [ ] `GOOGLE_CLOUD_PROJECT_ID` or `VEO3_PROJECT_ID` is set
- [ ] Vertex AI API is enabled in your GCP project

---

## 🚨 Important Notes

1. **Never commit the JSON key file to git** ✅ (already in `.gitignore`)
2. **For Render/Vercel:** Use `GOOGLE_SERVICE_ACCOUNT_JSON` with full JSON on one line
3. **For local:** Use `GOOGLE_APPLICATION_CREDENTIALS` with file path
4. **Location:** Must be `us-central1` for Imagen 4 (default is already set)
5. **Project ID:** Can use either `GOOGLE_CLOUD_PROJECT_ID` or `VEO3_PROJECT_ID`

---

## 🔗 Related Environment Variables

```env
# Required
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}  # OR
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json

# Project Configuration
GOOGLE_CLOUD_PROJECT_ID=your-project-id
VEO3_PROJECT_ID=your-project-id  # Alternative to above
VEO3_LOCATION=us-central1  # Default, can be changed
IMAGEN_MODEL_ID=imagen-4.0-generate-001  # Default
VEO3_MODEL_ID=veo-3  # Default
```

---

## 📚 Additional Resources

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Imagen Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)
- [Veo 3 Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation)
- [Service Account Best Practices](https://cloud.google.com/iam/docs/best-practices-service-accounts)

