# Fix Google Drive OAuth "Failed to exchange code for token" Error

## 🔴 Error: `400: Failed to exchange code for token`

This error occurs when the OAuth token exchange fails. Common causes:

## 🔍 Common Causes

### 1. **Redirect URI Mismatch** (Most Common)

The redirect URI used in the token exchange **must exactly match**:
- The redirect URI in the authorization URL
- The redirect URI configured in Google Cloud Console

**Check:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Click on your OAuth 2.0 Client ID
4. Check **Authorized redirect URIs**

**Must match exactly:**
```
https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
```

**Common mistakes:**
- ❌ `http://` instead of `https://`
- ❌ Trailing slash: `/callback/` instead of `/callback`
- ❌ Different domain/subdomain
- ❌ Missing `/api/integrations/google_drive/callback` path

### 2. **Environment Variable Mismatch**

**Check Render Environment Variables:**
```
GOOGLE_DRIVE_REDIRECT_URI=https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
```

**Must match exactly** what's in Google Cloud Console.

### 3. **Code Already Used or Expired**

- Authorization codes are **single-use** (can only be exchanged once)
- Codes expire after **10 minutes**
- If you refresh the page or try again, you need a new authorization code

**Fix:** Start the OAuth flow again from the beginning.

### 4. **Invalid Client ID or Secret**

**Check Render Environment Variables:**
```
GOOGLE_DRIVE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret
```

**Verify:**
- Client ID and Secret are correct
- They match the OAuth client in Google Cloud Console
- No extra spaces or quotes around values

### 5. **App Not Published/Verified**

If your app is still in "Testing" mode:
- Only test users can authorize
- Make sure your Google account is added as a test user

**Fix:** Add your email to test users in OAuth consent screen, or publish the app.

## 🔧 Step-by-Step Fix

### Step 1: Verify Redirect URI in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project: **aimarketing-480803**
3. Navigate to **APIs & Services** → **Credentials**
4. Click on your OAuth 2.0 Client ID
5. Check **Authorized redirect URIs** section
6. **Must have exactly:**
   ```
   https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
   ```

### Step 2: Verify Render Environment Variables

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your backend service
3. Go to **Environment** tab
4. Verify these variables are set:

```
GOOGLE_DRIVE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_DRIVE_CLIENT_SECRET=your-client-secret
GOOGLE_DRIVE_REDIRECT_URI=https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
BACKEND_URL=https://sorasocialmedia-1.onrender.com
```

**Important:** 
- No quotes around values
- No trailing spaces
- Must use `https://` (not `http://`)
- Must match Google Cloud Console exactly

### Step 3: Restart Render Service

After updating environment variables:
1. Go to Render Dashboard
2. Click **Manual Deploy** → **Clear build cache & deploy**
3. Wait for deployment to complete

### Step 4: Test OAuth Flow

1. Try connecting Google Drive again
2. Complete the authorization
3. Should redirect back successfully

## 🐛 Debugging

### Check Backend Logs

Look for these log messages in Render logs:

```
[GoogleDrive] Exchanging code for token...
[GoogleDrive] Redirect URI: https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
[GoogleDrive] Token exchange failed with status 400
[GoogleDrive] Error detail: redirect_uri_mismatch
```

### Common Error Messages

**`redirect_uri_mismatch`:**
- Redirect URI doesn't match Google Cloud Console
- Fix: Update Google Cloud Console or environment variable

**`invalid_grant`:**
- Code already used or expired
- Fix: Start OAuth flow again

**`invalid_client`:**
- Client ID or Secret is wrong
- Fix: Check environment variables

**`unauthorized_client`:**
- Client ID not authorized for this redirect URI
- Fix: Add redirect URI to Google Cloud Console

## ✅ Verification Checklist

- [ ] Redirect URI in Google Cloud Console matches exactly
- [ ] `GOOGLE_DRIVE_REDIRECT_URI` in Render matches Google Cloud Console
- [ ] `GOOGLE_DRIVE_CLIENT_ID` is set correctly in Render
- [ ] `GOOGLE_DRIVE_CLIENT_SECRET` is set correctly in Render
- [ ] `BACKEND_URL` is set to `https://sorasocialmedia-1.onrender.com`
- [ ] Render service has been restarted after environment variable changes
- [ ] Using `https://` (not `http://`) for all URLs
- [ ] No trailing slashes in redirect URI
- [ ] App is published or your email is in test users

## 📝 Quick Fix Template

If you need to update the redirect URI:

1. **Google Cloud Console:**
   - Add: `https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback`

2. **Render Environment Variables:**
   ```
   GOOGLE_DRIVE_REDIRECT_URI=https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
   ```

3. **Restart Render service**

4. **Try again**

## 🔗 Related Files

- `backend/services/google_drive_service.py` - OAuth implementation
- `backend/main.py` - OAuth callback endpoint
- `GOOGLE_DRIVE_OAUTH_SETUP.md` - Initial setup guide

