# LinkedIn Connection Setup Guide

To connect LinkedIn and post videos from VideoHook, you need to set up LinkedIn OAuth. Here's how:

## Option 1: OAuth Flow (Recommended)

### Step 1: Create a LinkedIn App

1. **Go to LinkedIn Developers**:
   - Visit [LinkedIn Developers](https://www.linkedin.com/developers/)
   - Click "Create app" or "My Apps"

2. **Create Your App**:
   - Fill in app details:
     - **App name**: VideoHook (or your preferred name)
     - **LinkedIn Page**: Select or create a LinkedIn Page to associate with the app
     - **App logo**: Upload a logo (optional)
     - **App use case**: Select an appropriate use case
     - **Privacy Policy URL**: Add your privacy policy URL
     - **App terms**: Accept terms and conditions

3. **Configure OAuth Settings**:
   - In your app dashboard, go to **"Auth"** tab
   - Under **"Redirect URLs"**, add:
     ```
     http://localhost:8000/api/oauth/linkedin/callback
     ```
   - For production, also add:
     ```
     https://yourdomain.com/api/oauth/linkedin/callback
     ```

4. **Request API Products**:
   - Go to **"Products"** tab
   - Request access to:
     - ✅ **Sign In with LinkedIn using OpenID Connect**
     - ✅ **Share on LinkedIn** (for posting content)
   - Note: Some products may require verification/review

5. **Get Your Credentials**:
   - Go to **"Auth"** tab
   - Copy your **Client ID** and **Client Secret**
   - These are what you'll need for your backend

### Step 2: Add Credentials to Backend

Add these to your `backend/.env` file:

```env
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
BASE_URL=http://localhost:8000
```

### Step 3: Restart Backend Server

After adding credentials, restart your backend server so it picks up the new environment variables.

### Step 4: Connect in VideoHook

1. Open VideoHook dashboard
2. Go to **Settings** → **Social Media Connections**
3. Click **"Connect LinkedIn"** button
4. You'll be redirected to LinkedIn to authorize
5. Grant the requested permissions
6. After authorization, you'll be redirected back to VideoHook
7. Your LinkedIn account should now be connected!

---

## Option 2: Manual Entry (Alternative - Advanced)

If OAuth setup is complex, you can manually add a LinkedIn connection using an access token.

### Step 1: Get a LinkedIn Access Token

1. Use LinkedIn's OAuth 2.0 flow manually or via a tool
2. Get an access token with these permissions:
   - `openid`
   - `profile`
   - `email`
   - `w_member_social` (for posting content)

### Step 2: Get Your LinkedIn Person URN

Your LinkedIn Person URN looks like: `urn:li:person:abc123xyz`

You can get it by calling:
```
GET https://api.linkedin.com/v2/userinfo
Authorization: Bearer YOUR_ACCESS_TOKEN
```

The response will include your user ID, which you can format as `urn:li:person:{user_id}`.

### Step 3: Add Connection Manually

**Note**: Currently, VideoHook doesn't have a manual entry modal for LinkedIn like it does for Instagram. You would need to either:
1. Use OAuth (recommended)
2. Add a manual endpoint (we can add this if needed)

---

## Required Permissions

Your LinkedIn app needs these OAuth scopes:

- `openid` - Basic authentication
- `profile` - Access to profile information
- `email` - Access to email address
- `w_member_social` - Post content on behalf of the user

---

## Important Notes

### LinkedIn Account Requirements:
- ✅ Any LinkedIn account can be connected
- ✅ Personal and Company pages can post via API
- ✅ Must have granted appropriate permissions during OAuth

### Video Requirements:
- Format: MP4
- Maximum size: 200MB (for direct upload)
- Duration: Up to 10 minutes
- Recommended aspect ratio: 16:9 or 1:1

### Access Token Expiration:
- Access tokens typically expire in 60 days
- The system will attempt to use refresh tokens if available
- You may need to re-authorize if token expires

---

## Troubleshooting

### "LinkedIn OAuth not configured" error:
- Make sure `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` are in `backend/.env`
- Restart the backend server after adding credentials
- Check that the credentials are correct (no extra spaces)

### "Invalid redirect URI" error:
- Make sure the redirect URI in your LinkedIn app matches exactly:
  - `http://localhost:8000/api/oauth/linkedin/callback`
- Check for trailing slashes or typos
- Redirect URIs are case-sensitive

### "Insufficient permissions" error:
- Make sure you've requested the right products in LinkedIn App dashboard:
  - "Sign In with LinkedIn using OpenID Connect"
  - "Share on LinkedIn"
- Some products require LinkedIn review and approval

### OAuth redirect not working:
- Make sure backend is running on `http://localhost:8000`
- Check that the redirect URI in LinkedIn app matches exactly
- Look at browser console for errors

### "Failed to post" error:
- Check that your access token has `w_member_social` permission
- Verify your LinkedIn account is active
- Check backend logs for detailed error messages

---

## Testing Your Connection

After connecting:

1. Go to **Dashboard** → **LinkedIn Tools** (or any video generation page)
2. Generate or upload a video
3. Click **"Post to LinkedIn"**
4. Select your LinkedIn connection
5. Your video should be posted!

---

## Resources

- [LinkedIn Developers Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [LinkedIn OAuth 2.0 Guide](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [LinkedIn Share API](https://docs.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [LinkedIn Video Sharing](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/video-shares)

---

## Security Notes

- Never commit your `.env` file to version control
- Keep your Client Secret secure
- Use environment variables in production
- Rotate credentials if compromised
- Review OAuth permissions regularly



