# Google Drive OAuth Setup Guide

## 🔴 Problem: Error 403: access_denied

Your Render backend (`sorasocialmedia-1.onrender.com`) needs to be configured in Google Cloud Console's OAuth consent screen to allow Google Drive access.

## 📋 Step-by-Step Setup

### Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com/
2. Select your project: **aimarketing-480803** (or create a new one)
3. Make sure **APIs & Services** is enabled

### Step 2: Enable Google Drive API

1. Go to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click on it and click **Enable**

### Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** (unless you have a Google Workspace account)
3. Click **Create**

#### Fill in the OAuth Consent Screen:

**App Information:**
- **App name:** `Aigis Marketing` (or your app name)
- **User support email:** `nagurivindapalli@gmail.com` (your email)
- **App logo:** (Optional - upload a logo if you have one)

**App domain:**
- **Application home page:** `https://sorasocialmedia-1.onrender.com`
- **Application privacy policy link:** (Optional - can use your website)
- **Application terms of service link:** (Optional)

**Authorized domains:**
- Click **+ ADD DOMAIN**
- Add: `onrender.com` (this allows all Render subdomains)
- Also add: `sorasocialmedia-1.onrender.com` (specific domain)

**Developer contact information:**
- **Email addresses:** `nagurivindapalli@gmail.com`
- Click **Save and Continue**

### Step 4: Add Scopes

1. Click **Add or Remove Scopes**
2. In the filter box, search for:
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.metadata.readonly`
3. Check both scopes
4. Click **Update**
5. Click **Save and Continue**

### Step 5: Add Test Users (IMPORTANT!)

Since your app is in "Testing" mode, you need to add test users:

1. Under **Test users**, click **+ ADD USERS**
2. Add your email: `ngurivindapalli@gmail.com`
3. Add any other emails that need access
4. Click **Add**
5. Click **Save and Continue**

### Step 6: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
3. If prompted, select **Web application**
4. Fill in:
   - **Name:** `Aigis Marketing - Google Drive`
   - **Authorized JavaScript origins:**
     - `https://sorasocialmedia-1.onrender.com`
     - `http://localhost:8000` (for local development)
   - **Authorized redirect URIs:**
     - `https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback`
     - `http://localhost:8000/api/integrations/google_drive/callback` (for local development)
5. Click **Create**
6. **IMPORTANT:** Copy the **Client ID** and **Client Secret** immediately (you won't see the secret again!)

### Step 7: Add Environment Variables to Render

1. Go to your Render Dashboard → Your Backend Service → **Environment**
2. Add these variables:

```
GOOGLE_DRIVE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret-here
GOOGLE_DRIVE_REDIRECT_URI=https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
```

3. Click **Save Changes**
4. Render will automatically redeploy

### Step 8: Verify Setup

1. After Render redeploys, try connecting Google Drive again
2. You should see the OAuth consent screen
3. Click **Continue** to grant permissions
4. The app should now have access to Google Drive

## 🔧 Troubleshooting

### Still Getting 403 Error?

1. **Check Test Users:**
   - Make sure your email is added as a test user in OAuth consent screen
   - Go to **OAuth consent screen** → **Test users** → Verify your email is listed

2. **Check Authorized Domains:**
   - Go to **OAuth consent screen** → **Authorized domains**
   - Make sure `onrender.com` is listed

3. **Check Redirect URI:**
   - Go to **Credentials** → Your OAuth client → **Edit**
   - Verify redirect URI matches exactly: `https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback`

4. **Check Scopes:**
   - Go to **OAuth consent screen** → **Scopes**
   - Verify both Drive scopes are added

5. **App Status:**
   - If still in "Testing", only test users can access
   - To allow all users, you need to submit for verification (takes 1-2 weeks)
   - For now, add all users who need access as test users

### Common Issues

**Issue:** "Redirect URI mismatch"
- **Fix:** Make sure the redirect URI in Google Console matches exactly what's in your code
- Check `GOOGLE_DRIVE_REDIRECT_URI` environment variable

**Issue:** "Access blocked: app is in testing mode"
- **Fix:** Add the user's email to **Test users** in OAuth consent screen

**Issue:** "Invalid client"
- **Fix:** Verify `GOOGLE_DRIVE_CLIENT_ID` and `GOOGLE_DRIVE_CLIENT_SECRET` are set correctly in Render

## 📝 Quick Checklist

- [ ] Google Drive API enabled
- [ ] OAuth consent screen configured
- [ ] App domain: `sorasocialmedia-1.onrender.com` added
- [ ] Authorized domain: `onrender.com` added
- [ ] Scopes added: `drive.readonly` and `drive.metadata.readonly`
- [ ] Test users added (your email)
- [ ] OAuth credentials created (Client ID + Secret)
- [ ] Redirect URI configured: `https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback`
- [ ] Environment variables set in Render:
  - `GOOGLE_DRIVE_CLIENT_ID`
  - `GOOGLE_DRIVE_CLIENT_SECRET`
  - `GOOGLE_DRIVE_REDIRECT_URI`
- [ ] Render service redeployed

## 🚀 Production (Optional - For Public Access)

If you want to allow all users (not just test users):

1. Go to **OAuth consent screen**
2. Click **PUBLISH APP**
3. Note: Google may require verification if you request sensitive scopes
4. This process can take 1-2 weeks

For now, **Testing mode with test users is sufficient** for your use case.

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [OAuth Consent Screen Guide](https://support.google.com/cloud/answer/10311615)


   