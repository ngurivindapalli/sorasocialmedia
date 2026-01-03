# Troubleshooting Integration Connection Issues

## "Not Found" Error When Connecting Notion/Google Drive

### Common Causes:

1. **Not Logged In** - Integration endpoints require authentication
2. **Wrong API URL** - Frontend not pointing to correct backend
3. **Backend Not Running** - Render service might be sleeping
4. **CORS Issues** - Backend not allowing frontend domain

## Quick Fixes:

### 1. Check if You're Logged In
- Make sure you're logged into the application
- Check browser console for authentication errors
- Try logging out and back in

### 2. Verify API URL in Vercel
Go to Vercel Dashboard → Your Project → Settings → Environment Variables

**Check:**
- `VITE_API_URL` should be: `https://sorasocialmedia-1.onrender.com`
- Make sure there's NO trailing slash
- Make sure it's set for Production environment

### 3. Test Backend Directly
Open in browser:
```
https://sorasocialmedia-1.onrender.com/api/health
```

Should return: `{"status":"ok"}`

### 4. Check Browser Console
Open Developer Tools (F12) → Console tab
- Look for errors when clicking "Connect Notion" or "Connect Google Drive"
- Check Network tab to see the actual request/response

### 5. Verify Environment Variables in Render
Go to Render Dashboard → Your Backend Service → Environment

**Required variables:**
```
GOOGLE_DRIVE_CLIENT_ID=your_client_id
GOOGLE_DRIVE_CLIENT_SECRET=your_client_secret
GOOGLE_DRIVE_REDIRECT_URI=https://sorasocialmedia-1.onrender.com/api/integrations/google_drive/callback
NOTION_CLIENT_ID=your_client_id
NOTION_CLIENT_SECRET=your_client_secret
NOTION_REDIRECT_URI=https://sorasocialmedia-1.onrender.com/api/integrations/notion/callback
BACKEND_URL=https://sorasocialmedia-1.onrender.com
FRONTEND_URL=https://aigismarketing.com
```

### 6. Test Endpoint Directly (with auth token)
If you have a valid auth token, test:
```
GET https://sorasocialmedia-1.onrender.com/api/integrations/notion/authorize
Headers: Authorization: Bearer YOUR_TOKEN
```

### 7. Check Render Logs
Go to Render Dashboard → Your Backend Service → Logs
- Look for errors when the request is made
- Check if the service is running

### 8. Common Error Messages:

**"Not Found" (404)**
- Endpoint doesn't exist or wrong URL
- Check: `/api/integrations/{platform}/authorize` exists

**"Unauthorized" (401)**
- Not logged in
- Invalid/expired token
- Solution: Log in again

**"OAuth not configured" (400)**
- Missing CLIENT_ID or CLIENT_SECRET in Render environment
- Solution: Add environment variables in Render

**"Invalid redirect URI"**
- Redirect URI in Google/Notion doesn't match Render URL
- Solution: Update redirect URI in OAuth provider

## Debug Steps:

1. **Open Browser Console** (F12)
2. **Click "Connect Notion" or "Connect Google Drive"**
3. **Check Console for:**
   - Request URL
   - Response status code
   - Error message
4. **Check Network Tab:**
   - Find the `/api/integrations/...` request
   - Check Request Headers (Authorization token)
   - Check Response (error message)

## Still Not Working?

1. Check Render service is running (not sleeping)
2. Verify all environment variables are set
3. Check CORS settings in backend allow `aigismarketing.com`
4. Try redeploying backend on Render
5. Clear browser cache and cookies







