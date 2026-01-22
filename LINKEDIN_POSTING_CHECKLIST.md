# LinkedIn Posting Checklist

## ✅ What You've Done
- [x] Added redirect URL to LinkedIn Developer Portal

## 🔧 What You Still Need to Do

### 1. Set LinkedIn OAuth Credentials (Required)

Add these to your backend `.env` file and Render environment variables:

```bash
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
BASE_URL=https://aigismarketing.com
FRONTEND_URL=https://aigismarketing.com
```

**Where to find these:**
1. Go to: https://www.linkedin.com/developers/apps
2. Click on your app
3. Go to **"Auth"** tab
4. Copy:
   - **Client ID** → Use as `LINKEDIN_CLIENT_ID`
   - **Client Secret** → Use as `LINKEDIN_CLIENT_SECRET`

### 2. Verify LinkedIn App Permissions

Make sure your LinkedIn app has the required permissions:

1. Go to: https://www.linkedin.com/developers/apps
2. Click your app → **"Products"** tab
3. Ensure **"Sign In with LinkedIn using OpenID Connect"** is added
4. Go to **"Auth"** tab
5. Verify **"w_member_social"** is in the OAuth 2.0 scopes
   - This permission is required for posting to LinkedIn

**Note:** If `w_member_social` is not available, you may need to:
- Request access from LinkedIn
- Apply for Marketing Developer Platform access
- Some permissions require LinkedIn approval

### 3. Connect Your LinkedIn Account

After setting credentials, connect your LinkedIn account:

1. Go to: https://aigismarketing.com/dashboard?tab=settings
2. Find **"LinkedIn"** section
3. Click **"Connect LinkedIn"** button
4. You'll be redirected to LinkedIn to authorize
5. After authorization, you'll be redirected back
6. Your LinkedIn account should now show as "Connected"

### 4. Test Posting

Once connected, you can post:

1. Generate a marketing post (with LinkedIn as platform)
2. Or use the `/api/post/video` endpoint with your LinkedIn connection ID
3. Check if the post appears on your LinkedIn feed

---

## 🧪 Quick Test

### Test OAuth Connection:
1. Visit: `https://aigismarketing.com/api/oauth/linkedin/authorize?platform=linkedin`
2. You should be redirected to LinkedIn
3. After authorizing, you should be redirected back to:
   ```
   https://aigismarketing.com/dashboard?tab=settings&connected=linkedin
   ```

### Test Posting:
1. Make sure you have a LinkedIn connection in your database
2. Use the `/api/post/video` endpoint with:
   - `connection_ids`: [your_linkedin_connection_id]
   - `video_url`: URL to your video
   - `caption`: Your post caption

---

## 🆘 Troubleshooting

### "LinkedIn OAuth not configured"
- ✅ Make sure `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` are set in your `.env` file
- ✅ Restart your backend after adding environment variables
- ✅ If using Render, make sure environment variables are saved and service is redeployed

### "redirect_uri_mismatch"
- ✅ Verify the redirect URL in LinkedIn matches exactly: `https://aigismarketing.com/api/oauth/linkedin/callback`
- ✅ Make sure there are no trailing slashes
- ✅ Wait 2-3 minutes after adding redirect URL before testing

### "Insufficient permissions" or "w_member_social not available"
- ✅ Your LinkedIn app may need Marketing Developer Platform access
- ✅ Go to LinkedIn Developer Portal → Your App → Products
- ✅ Check if you need to apply for additional permissions
- ✅ Some permissions require LinkedIn review/approval

### "Connection not found" when posting
- ✅ Make sure you've connected your LinkedIn account via OAuth first
- ✅ Check `/api/connections` endpoint to see if LinkedIn connection exists
- ✅ Verify the connection is active (`is_active: true`)

### Post fails with "401 Unauthorized"
- ✅ Your access token may have expired
- ✅ Disconnect and reconnect your LinkedIn account
- ✅ LinkedIn tokens typically last 60 days

---

## 📋 Final Checklist

Before you can post to LinkedIn:

- [ ] `LINKEDIN_CLIENT_ID` set in backend `.env` and Render
- [ ] `LINKEDIN_CLIENT_SECRET` set in backend `.env` and Render
- [ ] `BASE_URL` set to `https://aigismarketing.com` (or your backend URL)
- [ ] `FRONTEND_URL` set to `https://aigismarketing.com`
- [ ] Redirect URL added in LinkedIn Developer Portal
- [ ] `w_member_social` permission granted in LinkedIn app
- [ ] LinkedIn account connected via OAuth flow
- [ ] Backend restarted/redeployed with new environment variables
- [ ] Test OAuth connection works
- [ ] Test posting works

---

## ✅ Ready to Post?

Once all checklist items are complete:
1. Your LinkedIn account is connected
2. You can generate marketing posts with LinkedIn as the platform
3. You can post videos/images to LinkedIn via the API

**Next Steps:**
- Generate a marketing post and select "LinkedIn" as the platform
- Or use the Post Video button with your LinkedIn connection selected
