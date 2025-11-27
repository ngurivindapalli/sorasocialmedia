# How to Enable Veo 3 in Google Cloud

## Step 1: Enable Vertex AI API

1. Go to [Google Cloud Console - APIs & Services](https://console.cloud.google.com/apis/library?project=igvideogen)
2. Search for **"Vertex AI API"**
3. Click **"Enable"** (if not already enabled)
4. Wait a few minutes for it to activate

## Step 2: Verify Vertex AI API is Enabled

1. Go to [APIs & Services > Enabled APIs](https://console.cloud.google.com/apis/dashboard?project=igvideogen)
2. Look for **"Vertex AI API"** in the list
3. If it's not there, go back to Step 1

## Step 3: Check Vertex AI Studio (Not Model Registry)

**Important:** Veo 3 won't appear in the Model Registry. It's a publisher model accessed via API.

1. Go to [Vertex AI Studio](https://console.cloud.google.com/vertex-ai/studio?project=igvideogen)
2. Look for **"Video"** or **"Veo"** in the available model types
3. This confirms if Veo 3 is available in your project

## Step 4: Verify Your Service Account Has Permissions

1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts?project=igvideogen)
2. Find your service account (the one used in `GOOGLE_APPLICATION_CREDENTIALS`)
3. Make sure it has the **"Vertex AI User"** role:
   - Click on the service account
   - Go to **"Permissions"** tab
   - Look for **"Vertex AI User"** role
   - If missing, click **"Grant Access"** and add the role

## Step 5: Test the API

Once everything is set up, try generating a video again. The app will:
- Use service account authentication ✅
- Call the Veo 3 API endpoint
- If Veo 3 is available → Use it
- If not available (404) → Fall back to Sora 2 ✅

## Troubleshooting

### Still Getting 404?

**Option A: Contact Google Cloud Support**
1. Go to [Google Cloud Support](https://cloud.google.com/support)
2. Request access to "Veo 3" or "Vertex AI Video Generation"
3. Mention your project ID: `igvideogen`

**Option B: Try a Different Region**
- Veo 3 might only be available in certain regions
- Currently using: `us-central1`
- You can try other regions by setting `GOOGLE_CLOUD_LOCATION` in `.env`

**Option C: Continue with Sora 2**
- The app automatically falls back to Sora 2
- Sora 2 is working and generating videos ✅
- You can use the app while waiting for Veo 3 access

## Quick Checklist

- [ ] Vertex AI API is enabled
- [ ] Service account has "Vertex AI User" role
- [ ] `GOOGLE_APPLICATION_CREDENTIALS` is set correctly
- [ ] `GOOGLE_CLOUD_PROJECT_ID=igvideogen` is set
- [ ] Backend server is restarted

## Current Status

✅ **Authentication:** Working (service account)
✅ **Fallback:** Working (Sora 2)
❌ **Veo 3:** Not available in project yet (404 error)

The app is fully functional with Sora 2. Once Veo 3 is available, it will automatically use it!


