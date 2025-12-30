# Veo 3 Service Account Setup - Quick Guide 🔑

Your API key isn't working because Vertex AI requires OAuth 2.0 authentication. Let's set up a service account (the recommended method).

## Quick Setup (5 minutes)

### Step 1: Create Service Account in Google Cloud

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Make sure you're in project: **aimarketing-480803**
3. Navigate to **IAM & Admin** > **Service Accounts**
4. Click **"+ CREATE SERVICE ACCOUNT"**

### Step 2: Configure Service Account

1. **Service account name**: `veo3-service` (or any name you prefer)
2. **Service account ID**: Will auto-generate
3. **Description**: "Service account for Veo 3 video generation"
4. Click **"CREATE AND CONTINUE"**

### Step 3: Grant Permissions

1. In **"Grant this service account access to project"**:
   - Click **"Select a role"** dropdown
   - Search for **"Vertex AI User"**
   - Select **"Vertex AI User"** role
   - Click **"ADD ANOTHER ROLE"** (optional)
   - Add **"Storage Object Admin"** (if you plan to use Google Cloud Storage)
2. Click **"CONTINUE"**
3. Click **"DONE"** (skip optional step)

### Step 4: Create and Download JSON Key

1. Click on your newly created service account (e.g., `veo3-service@aimarketing-480803.iam.gserviceaccount.com`)
2. Go to **"KEYS"** tab
3. Click **"ADD KEY"** > **"Create new key"**
4. Select **"JSON"** format
5. Click **"CREATE"**
6. **The JSON file will download automatically** - save it!

### Step 5: Save JSON Key File

1. Move the downloaded JSON file to your `backend` folder
2. Name it something like: `veo3-service-account.json`
3. **Full path example**: 
   ```
   C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\veo3-service-account.json
   ```

### Step 6: Update `.env` File

Open `backend/.env` and update it:

**Remove or comment out:**
```env
# VEO3_API_KEY=AQ.Ab8RN6Lf5oLM8rkqh6bnQv4sHDNMqbLcu1KlGKvHvCo466OU0A
```

**Add or update:**
```env
GOOGLE_CLOUD_PROJECT_ID=aimarketing-480803
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\veo3-service-account.json
GOOGLE_CLOUD_LOCATION=us-central1
```

**Important**: Use the **actual path** to your downloaded JSON file!

### Step 7: Restart Backend Server

1. Stop the backend server (Ctrl+C in the PowerShell window)
2. Restart it:
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python main.py
   ```

### Step 8: Verify It Works

Look for these messages in the logs:

```
[Veo3] ✓ Veo 3 service initialized (Google Cloud Vertex AI)
[Veo3]   Project ID: aimarketing-480803
[Veo3]   Location: us-central1
[Veo3]   Model: veo-3
[Veo3]   Auth: Service Account
```

**No more 401 errors!** ✅

---

## Alternative: Quick gcloud CLI Method

If you have `gcloud` CLI installed, you can use this faster method:

### Step 1: Install gcloud CLI (if not installed)

Download from: https://cloud.google.com/sdk/docs/install

### Step 2: Authenticate

```bash
gcloud auth login
gcloud config set project aimarketing-480803
```

### Step 3: Update `.env`

```env
GOOGLE_CLOUD_PROJECT_ID=aimarketing-480803
VEO3_USE_GCLOUD_AUTH=true
# Remove VEO3_API_KEY
```

### Step 4: Restart Backend

This method uses your personal Google account credentials.

---

## Troubleshooting

### "File not found" error
- ✅ Check the path to JSON file is correct
- ✅ Use forward slashes `/` or double backslashes `\\` in Windows paths
- ✅ Make sure the file exists at that location

### "Permission denied"
- ✅ Verify service account has "Vertex AI User" role
- ✅ Check IAM permissions in Google Cloud Console

### Still getting 401 errors
- ✅ Make sure `VEO3_API_KEY` is removed/commented out
- ✅ Verify `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- ✅ Restart backend server after changes

---

## Security Notes

⚠️ **Keep your service account JSON file SECRET!**

- Don't commit it to Git
- Add to `.gitignore`:
  ```
  *.json
  !package*.json
  veo3-service-account.json
  ```
- Store it securely
- Don't share it publicly

---

## What Changed?

**Before (Not Working):**
```env
VEO3_API_KEY=AQ.Ab8RN6Lf5oLM8rkqh6bnQv4sHDNMqbLcu1KlGKvHvCo466OU0A
```

**After (Working):**
```env
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
# VEO3_API_KEY removed
```

Service account authentication is more secure and permanent than API keys!

---

**Need help?** Follow the steps above and your Veo 3 authentication will work! 🚀

















