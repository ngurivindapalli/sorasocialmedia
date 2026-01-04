# Veo 3 Setup Guide - New Google Cloud Account 🎬

Complete step-by-step guide to set up a fresh Google Cloud account with Veo 3 video generation.

## Overview

This guide will help you:
1. Create a new Google Cloud account
2. Set up billing (required for Veo 3)
3. Create a project
4. Enable Vertex AI API
5. Request Veo 3 access
6. Set up authentication
7. Configure your app

---

## Step 1: Create Google Cloud Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Get Started for Free"** or **"Sign In"** if you have a Google account
3. Accept the terms of service
4. Complete account setup

**Note**: Google Cloud offers $300 in free credits for new accounts (valid for 90 days)

---

## Step 2: Enable Billing

⚠️ **Billing is REQUIRED for Veo 3**, even if you're using free credits.

1. In Google Cloud Console, click the **hamburger menu** (☰) > **Billing**
2. Click **"Link a billing account"** or **"Create billing account"**
3. Fill in your billing information:
   - Country/Region
   - Account name
   - Payment method (credit card)
4. Click **"Submit and enable billing"**

**Important**: 
- You won't be charged until you exceed free credits
- Set up billing alerts to monitor usage
- Free tier includes $300 credit for 90 days

---

## Step 3: Create a New Project

1. In Google Cloud Console, click the **project dropdown** at the top
2. Click **"New Project"**
3. Enter project details:
   - **Project name**: e.g., "veo3-video-generator"
   - **Project ID**: Auto-generated (or customize)
   - **Location**: Choose organization (if applicable)
4. Click **"Create"**
5. **Wait 1-2 minutes** for project to be fully created
6. Select your new project from the dropdown

**Note**: Save your **Project ID** (not the project name) - you'll need it later!

---

## Step 4: Enable Vertex AI API

1. In Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for **"Vertex AI API"**
3. Click on **"Vertex AI API"**
4. Click **"Enable"**
5. Wait for it to enable (usually takes 30-60 seconds)

**Alternative method**:
- Go to **APIs & Services** > **Enabled APIs**
- Click **"+ ENABLE APIS AND SERVICES"**
- Search for "Vertex AI API" and enable it

---

## Step 5: Request Veo 3 Access

⚠️ **Veo 3 is in limited preview** - you may need to request access.

### Check if Veo 3 is Available

1. Go to [Vertex AI Models](https://console.cloud.google.com/vertex-ai/models)
2. Look for **"veo-3"** or **"Veo"** in the model list
3. If you see it, you're good to go! ✅
4. If not, continue to request access

### Request Access (if needed)

**Option 1: Through Google Cloud Console**
1. Go to [Vertex AI](https://console.cloud.google.com/vertex-ai)
2. Look for **"Request Access"** or **"Early Access"** section
3. Fill out the access request form
4. Mention you need access to **"Veo 3 video generation"** or **"veo-3 model"**

**Option 2: Contact Support**
1. Go to [Google Cloud Support](https://cloud.google.com/support)
2. Create a support case
3. Request: "Access to Veo 3 video generation model in Vertex AI"
4. Include your Project ID

**Option 3: Wait for General Availability**
- Veo 3 may become available in your project automatically
- Check back in a few days

**Note**: Access approval can take anywhere from a few hours to several days.

---

## Step 6: Set Up Authentication (Service Account)

You need a service account to authenticate your app. This is the **recommended method for production**.

### Create Service Account

1. In Google Cloud Console, go to **IAM & Admin** > **Service Accounts**
2. Click **"+ CREATE SERVICE ACCOUNT"**
3. Fill in details:
   - **Service account name**: `veo3-service` (or your choice)
   - **Service account ID**: Auto-generated
   - **Description**: "Service account for Veo 3 video generation"
4. Click **"CREATE AND CONTINUE"**

### Grant Permissions

1. In **"Grant this service account access to project"**:
   - Click **"Select a role"** dropdown
   - Search for **"Vertex AI User"**
   - Select **"Vertex AI User"** role
   - Click **"ADD ANOTHER ROLE"** (optional but recommended)
   - Add **"Storage Object Admin"** (if using GCS for video storage)
2. Click **"CONTINUE"**
3. Click **"DONE"**

### Create and Download Key

1. Click on your newly created service account
2. Go to **"KEYS"** tab
3. Click **"ADD KEY"** > **"Create new key"**
4. Select **"JSON"** format
5. Click **"CREATE"**
6. **Save the downloaded JSON file** - you'll need it!

**⚠️ Security Note**: 
- Keep this JSON file **SECRET** - it has full access to your project
- Don't commit it to Git
- Store it securely (e.g., in `backend/` directory, add to `.gitignore`)

---

## Step 7: Configure Your App

### Update `.env` File

Add these variables to your `backend/.env` file:

```env
# Required: Your Google Cloud Project ID
GOOGLE_CLOUD_PROJECT_ID=your-project-id-here

# Required: Path to service account JSON key file
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\your-service-account-key.json

# Optional: Location (default: us-central1)
GOOGLE_CLOUD_LOCATION=us-central1

# Optional: Model ID (default: veo-3)
VEO3_MODEL_ID=veo-3

# Optional: Google Cloud Storage for video storage
VEO3_STORAGE_URI=gs://your-bucket-name/videos/
```

### Example `.env` Entry

```env
GOOGLE_CLOUD_PROJECT_ID=veo3-video-generator-123456
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\veo3-service-account.json
GOOGLE_CLOUD_LOCATION=us-central1
```

### Install Required Python Package

Make sure `google-auth` is installed:

```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install google-auth
```

Or add to `requirements.txt`:
```
google-auth==2.27.0
```

---

## Step 8: Test Your Setup

### Restart Backend Server

1. Stop your backend server (Ctrl+C)
2. Restart it:
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python main.py
   ```

3. Look for these messages in the logs:
   ```
   [Veo3] ✓ Veo 3 service initialized (Google Cloud Vertex AI)
   [Veo3]   Project ID: your-project-id
   [Veo3]   Location: us-central1
   [Veo3]   Model: veo-3
   [Veo3]   Auth: Service Account
   ```

### Test via API

1. Check health endpoint:
   ```bash
   curl http://localhost:8000/
   ```
   Should show: `"veo3": "✓ Active"`

2. Test video generation:
   ```bash
   curl -X POST http://localhost:8000/api/veo3/generate \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "A beautiful sunset over the ocean",
       "duration": 8,
       "resolution": "1280x720"
     }'
   ```

---

## Troubleshooting

### Error: "GOOGLE_CLOUD_PROJECT_ID not set"
- ✅ Check `.env` file has `GOOGLE_CLOUD_PROJECT_ID=your-project-id`
- ✅ Restart backend server after changing `.env`

### Error: "Failed to get access token"
- ✅ Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- ✅ Verify JSON file exists and is readable
- ✅ Ensure service account has "Vertex AI User" role

### Error: "404 Model not found" or "veo-3 not available"
- ✅ Veo 3 access may not be approved yet
- ✅ Check [Vertex AI Models](https://console.cloud.google.com/vertex-ai/models) for availability
- ✅ Request access if not available
- ✅ Try a different region (us-central1 is recommended)

### Error: "Permission denied"
- ✅ Verify service account has "Vertex AI User" role
- ✅ Check IAM permissions in Google Cloud Console
- ✅ Ensure billing is enabled

### Error: "Billing account not found"
- ✅ Enable billing in Google Cloud Console
- ✅ Link billing account to your project
- ✅ Wait a few minutes for billing to activate

### Error: "API not enabled"
- ✅ Enable Vertex AI API in APIs & Services
- ✅ Wait 1-2 minutes after enabling
- ✅ Refresh the page

---

## Cost Management

### Free Credits
- **$300 free credit** for new accounts (90 days)
- Use this to test Veo 3 without charges

### Set Up Billing Alerts

1. Go to **Billing** > **Budgets & alerts**
2. Click **"CREATE BUDGET"**
3. Set budget amount (e.g., $50/month)
4. Configure alerts (email notifications)
5. Save budget

### Monitor Usage

1. Go to **Billing** > **Reports**
2. View current usage
3. Check **Vertex AI** costs
4. Set up daily/weekly reports

### Video Generation Costs

- Veo 3 is billed **per second** of generated video
- Check [Google Cloud Pricing](https://cloud.google.com/vertex-ai/pricing) for current rates
- Typical cost: ~$0.05-0.10 per second of video (varies by region)

---

## Quick Checklist

Before using Veo 3, verify:

- [ ] Google Cloud account created
- [ ] Billing enabled
- [ ] Project created
- [ ] Project ID saved
- [ ] Vertex AI API enabled
- [ ] Veo 3 access requested/approved
- [ ] Service account created
- [ ] Service account has "Vertex AI User" role
- [ ] Service account JSON key downloaded
- [ ] `GOOGLE_CLOUD_PROJECT_ID` in `.env`
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` in `.env`
- [ ] `google-auth` package installed
- [ ] Backend server restarted
- [ ] Veo 3 service shows as "✓ Active" in logs

---

## Next Steps

Once setup is complete:

1. **Test video generation** via the API
2. **Monitor costs** in Google Cloud Console
3. **Set up billing alerts** to avoid surprises
4. **Use Veo 3 in your app** - it's now integrated!

---

## Support Resources

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Veo Video Generation Guide](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation)
- [Google Cloud Support](https://cloud.google.com/support)

---

**Need Help?** If you encounter issues:
1. Check the troubleshooting section above
2. Review Google Cloud Console for error messages
3. Check backend logs for detailed error information
4. Contact Google Cloud Support if access issues persist




















