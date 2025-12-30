# Fix Veo 3 Authentication Error 🔧

**Problem**: Getting `401 Authentication failed` because Vertex AI doesn't accept API keys - it needs OAuth 2.0 tokens or service accounts.

## Quick Fix (Choose One Method)

### Method 1: Service Account (Recommended - 5 minutes)

**Step 1**: Create Service Account
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts?project=aimarketing-480803
2. Click **"+ CREATE SERVICE ACCOUNT"**
3. Name: `veo3-service`
4. Click **"CREATE AND CONTINUE"**

**Step 2**: Grant Permissions
1. Role: **"Vertex AI User"**
2. Click **"CONTINUE"** then **"DONE"**

**Step 3**: Create Key
1. Click on the service account you just created
2. Go to **"KEYS"** tab
3. Click **"ADD KEY"** > **"Create new key"**
4. Choose **JSON**
5. Download the file

**Step 4**: Save JSON File
- Save it to: `backend/veo3-service-account.json`
- Or any location you prefer

**Step 5**: Update `.env` File

Remove this line:
```env
VEO3_API_KEY=AQ.Ab8RN6Lf5oLM8rkqh6bnQv4sHDNMqbLcu1KlGKvHvCo466OU0A
```

Add this (use your actual file path):
```env
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\veo3-service-account.json
```

**Step 6**: Restart Backend
- Stop server (Ctrl+C)
- Restart: `python main.py`

✅ **Done!** Should see: `[Veo3]   Auth: Service Account`

---

### Method 2: gcloud CLI (If you have it installed)

**Step 1**: Install gcloud (if needed)
- Download: https://cloud.google.com/sdk/docs/install

**Step 2**: Authenticate
```bash
gcloud auth login
gcloud config set project aimarketing-480803
```

**Step 3**: Update `.env`
```env
VEO3_USE_GCLOUD_AUTH=true
# Remove VEO3_API_KEY line
```

**Step 4**: Restart Backend

---

### Method 3: Get Fresh OAuth Token (Temporary - expires in 1 hour)

If you have `gcloud` installed:

```bash
gcloud auth print-access-token
```

Copy the token and update `.env`:
```env
VEO3_API_KEY=ya29.your-token-here
```

⚠️ **Note**: This token expires in 1 hour. Use Method 1 for permanent solution.

---

## What to Do Right Now

1. **Go to Google Cloud Console**: https://console.cloud.google.com/iam-admin/serviceaccounts?project=aimarketing-480803
2. **Create service account** (follow Method 1 above)
3. **Download JSON key**
4. **Update `.env` file** (remove VEO3_API_KEY, add GOOGLE_APPLICATION_CREDENTIALS)
5. **Restart backend server**

---

## Need Help?

See `VEO3_SERVICE_ACCOUNT_SETUP.md` for detailed step-by-step instructions with screenshots guidance.

















