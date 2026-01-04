# Veo 3 Quick Start - New Account 🚀

**TL;DR**: Set up a new Google Cloud account for Veo 3 in 10 minutes.

## Essential Steps

### 1. Create Account & Enable Billing
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create account → Enable billing (required, but $300 free credits included)

### 2. Create Project
- Click project dropdown → "New Project"
- Name it (e.g., "veo3-app")
- **Save the Project ID** (not the name!)

### 3. Enable APIs
- Go to **APIs & Services** > **Library**
- Search "Vertex AI API" → **Enable**

### 4. Request Veo 3 Access
- Go to [Vertex AI Models](https://console.cloud.google.com/vertex-ai/models)
- If you see "veo-3" → ✅ You're good!
- If not → Request access via Google Cloud Support

### 5. Create Service Account
1. Go to **IAM & Admin** > **Service Accounts**
2. Click **"+ CREATE SERVICE ACCOUNT"**
3. Name: `veo3-service`
4. Grant role: **"Vertex AI User"**
5. Create JSON key → **Download and save it**

### 6. Update `.env` File

Add to `backend/.env`:

```env
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\your-service-account-key.json
GOOGLE_CLOUD_LOCATION=us-central1
```

**Replace**:
- `your-project-id-here` with your actual Project ID
- `your-service-account-key.json` with your downloaded JSON filename

### 7. Install Package & Restart

```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install google-auth
python main.py
```

Look for: `[Veo3] ✓ Veo 3 service initialized`

---

## What You Need

✅ Google Cloud account  
✅ Billing enabled ($300 free credits)  
✅ Project ID  
✅ Service account JSON key file  
✅ Updated `.env` file  
✅ Backend restarted  

---

## Common Issues

**"GOOGLE_CLOUD_PROJECT_ID not set"**
→ Add to `.env` and restart server

**"404 Model not found"**
→ Veo 3 access not approved yet - request access

**"Permission denied"**
→ Service account needs "Vertex AI User" role

**"Billing account not found"**
→ Enable billing in Google Cloud Console

---

## Full Guide

See `VEO3_NEW_ACCOUNT_SETUP.md` for detailed instructions.




















