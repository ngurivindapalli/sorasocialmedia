# Redirect URLs for aigismarketing.com

## Overview
This document lists all the OAuth redirect URLs that need to be configured in your OAuth provider apps for aigismarketing.com.

## Environment Variables Required

Add these to your `.env` file (backend) and Render environment variables:

```bash
# Backend URL (for OAuth callbacks)
BASE_URL=https://aigismarketing.com

# Frontend URL (for redirects after OAuth)
FRONTEND_URL=https://aigismarketing.com
```

**Note:** If your backend is on a different subdomain (e.g., `api.aigismarketing.com`), use:
```bash
BASE_URL=https://api.aigismarketing.com
FRONTEND_URL=https://aigismarketing.com
```

## OAuth Redirect URLs by Platform

### 1. LinkedIn OAuth
**Redirect URI to add in LinkedIn App:**
```
https://aigismarketing.com/api/oauth/linkedin/callback
```
Or if backend is on a subdomain:
```
https://api.aigismarketing.com/api/oauth/linkedin/callback
```

**Where to add:**
1. Go to https://www.linkedin.com/developers/apps
2. Select your app
3. Go to "Auth" tab
4. Add the redirect URL under "Authorized redirect URLs for your app"

### 2. Instagram OAuth (Facebook Graph API)
**Redirect URI to add in Facebook App:**
```
https://aigismarketing.com/api/oauth/instagram/callback
```
Or if backend is on a subdomain:
```
https://api.aigismarketing.com/api/oauth/instagram/callback
```

**Where to add:**
1. Go to https://developers.facebook.com/apps
2. Select your app
3. Go to "Settings" → "Basic"
4. Add the redirect URI under "Valid OAuth Redirect URIs"

### 3. X (Twitter) OAuth
**Redirect URI to add in Twitter App:**
```
https://aigismarketing.com/api/oauth/x/callback
```
Or if backend is on a subdomain:
```
https://api.aigismarketing.com/api/oauth/x/callback
```

**Where to add:**
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Select your app
3. Go to "Settings" → "User authentication settings"
4. Add the redirect URI under "Callback URI / Redirect URL"

### 4. TikTok OAuth
**Redirect URI to add in TikTok App:**
```
https://aigismarketing.com/api/oauth/tiktok/callback
```
Or if backend is on a subdomain:
```
https://api.aigismarketing.com/api/oauth/tiktok/callback
```

**Where to add:**
1. Go to https://developers.tiktok.com/apps
2. Select your app
3. Go to "Basic Information" → "Platform information"
4. Add the redirect URI under "Redirect URL"

## Integration OAuth Redirect URLs

### Google Drive OAuth
**Redirect URI to add in Google Cloud Console:**
```
https://aigismarketing.com/api/integrations/google_drive/callback
```
Or if backend is on a subdomain:
```
https://api.aigismarketing.com/api/integrations/google_drive/callback
```

**Where to add:**
1. Go to https://console.cloud.google.com/apis/credentials
2. Select your OAuth 2.0 Client ID
3. Add the redirect URI under "Authorized redirect URIs"

### Notion OAuth
**Redirect URI to add in Notion Integration:**
```
https://aigismarketing.com/api/integrations/notion/callback
```
Or if backend is on a subdomain:
```
https://api.aigismarketing.com/api/integrations/notion/callback
```

**Where to add:**
1. Go to https://www.notion.so/my-integrations
2. Select your integration
3. Add the redirect URI under "Redirect URIs"

### Jira OAuth
**Redirect URI to add in Atlassian Developer Console:**
```
https://aigismarketing.com/api/integrations/jira/callback
```
Or if backend is on a subdomain:
```
https://api.aigismarketing.com/api/integrations/jira/callback
```

**Where to add:**
1. Go to https://developer.atlassian.com/console/myapps/
2. Select your app
3. Go to "Authorization" → "Callback URL"
4. Add the redirect URI

## Quick Setup Checklist

- [ ] Set `BASE_URL` in backend `.env` file
- [ ] Set `FRONTEND_URL` in backend `.env` file
- [ ] Add LinkedIn redirect URI to LinkedIn App
- [ ] Add Instagram redirect URI to Facebook App
- [ ] Add X redirect URI to Twitter App
- [ ] Add TikTok redirect URI to TikTok App
- [ ] Add Google Drive redirect URI to Google Cloud Console
- [ ] Add Notion redirect URI to Notion Integration
- [ ] Add Jira redirect URI to Atlassian Developer Console
- [ ] Update Render environment variables with `BASE_URL` and `FRONTEND_URL`
- [ ] Test OAuth flow for each platform

## Testing

After configuration, test each OAuth flow:

1. **LinkedIn:** Go to Settings → Connect LinkedIn
2. **Instagram:** Go to Settings → Connect Instagram
3. **X/Twitter:** Go to Settings → Connect X
4. **TikTok:** Go to Settings → Connect TikTok

You should be redirected to the OAuth provider, then back to:
```
https://aigismarketing.com/dashboard?tab=settings&connected={platform}
```

## Troubleshooting

**Error: "redirect_uri_mismatch"**
- Verify the redirect URI in your OAuth provider matches exactly (including https://)
- Check that `BASE_URL` environment variable is set correctly
- Make sure there are no trailing slashes

**Error: "Invalid redirect URI"**
- Some providers require the redirect URI to be added before it can be used
- Wait a few minutes after adding the redirect URI before testing

**Error: "Connection refused" or "Cannot reach server"**
- Verify your backend is accessible at the `BASE_URL`
- Check that your domain DNS is properly configured
- Ensure SSL certificate is valid (HTTPS required for OAuth)
