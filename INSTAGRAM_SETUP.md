# Instagram Posting Setup Guide

To post videos to Instagram from VideoHook, you need to set up Instagram API access. Here are the steps:

## Option 1: Manual Entry (Easiest - No OAuth Setup Required)

### Step 1: Get an Instagram Access Token

1. **Create a Facebook App** (Instagram uses Facebook Graph API):
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Click "My Apps" → "Create App"
   - Choose "Business" as the app type
   - Complete the basic setup

2. **Add Instagram Basic Display**:
   - In your Facebook App, go to "Products" → Add "Instagram Basic Display"
   - Configure OAuth redirect URIs: `http://localhost:8000/api/oauth/instagram/callback`
   - Add `http://localhost:3001` to Valid OAuth Redirect URIs

3. **Get an Access Token**:
   - Use the [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - Select your app
   - Generate a User Access Token with these permissions:
     - `instagram_basic`
     - `instagram_content_publish`
     - `pages_show_list`
     - `pages_read_engagement`
   - Or use Facebook's Access Token Tool to create a long-lived token (60 days)

4. **Get Your Instagram Account ID**:
   - Use the Graph API: `GET https://graph.instagram.com/me?fields=id,username&access_token=YOUR_TOKEN`
   - Or get it from your Instagram Business account settings

### Step 2: Add Connection in VideoHook

1. Open VideoHook dashboard
2. Go to Settings → Social Media Connections
3. Click "Connect Instagram"
4. Choose "Manual Entry" tab
5. Enter:
   - **Instagram Username**: Your Instagram handle (without @)
   - **Access Token**: The token you got from Facebook
   - **Account ID** (optional): Your Instagram account ID (system will try to fetch it if left blank)
6. Click "Save Connection"

You're done! You can now post videos to Instagram.

---

## Option 2: OAuth Flow (Automatic - Recommended for Production)

### Step 1: Set Up Facebook App (Same as Option 1, but configure OAuth)

1. Create a Facebook App at [Facebook Developers](https://developers.facebook.com/)
2. Add "Instagram Basic Display" product
3. Configure these settings:
   - **App ID**: Your Facebook App ID
   - **App Secret**: Your Facebook App Secret
   - **Valid OAuth Redirect URIs**: `http://localhost:8000/api/oauth/instagram/callback`

### Step 2: Add Credentials to Backend

Add these to your `backend/.env` file:

```env
INSTAGRAM_CLIENT_ID=your_facebook_app_id
INSTAGRAM_CLIENT_SECRET=your_facebook_app_secret
BASE_URL=http://localhost:8000
```

### Step 3: Connect in VideoHook

1. Open VideoHook dashboard
2. Go to Settings → Social Media Connections
3. Click "Connect Instagram"
4. Choose "OAuth (Recommended)" tab
5. Click "Connect with Instagram OAuth"
6. You'll be redirected to Instagram to authorize
7. After authorization, you'll be redirected back and connected

---

## Required Permissions

Your Instagram access token needs these permissions:
- `instagram_basic` - Basic Instagram account access
- `instagram_content_publish` - Post videos/content
- `pages_show_list` - List connected Facebook Pages
- `pages_read_engagement` - Read engagement data

---

## Important Notes

### Instagram Account Requirements:
- ✅ You need an **Instagram Business** or **Instagram Creator** account
- ❌ Personal Instagram accounts cannot post via API
- Your Instagram account must be connected to a Facebook Page

### Video Requirements:
- Format: MP4
- Maximum size: 4GB
- Duration: Up to 90 seconds for Reels
- Aspect ratio: 9:16 (portrait) recommended for Reels

### Access Token Expiration:
- Short-lived tokens: 1 hour
- Long-lived tokens: 60 days
- System Access Tokens: Can be renewed indefinitely (requires app review)

---

## Troubleshooting

### "Invalid access token" error:
- Token may have expired
- Token may not have required permissions
- Get a new token from Facebook Graph API Explorer

### "Account ID not found" error:
- Make sure your Instagram account is a Business/Creator account
- Verify the account is connected to a Facebook Page
- Check that the access token has correct permissions

### "OAuth not configured" error:
- Make sure `INSTAGRAM_CLIENT_ID` and `INSTAGRAM_CLIENT_SECRET` are in `backend/.env`
- Restart the backend server after adding credentials
- Check that redirect URI matches exactly: `http://localhost:8000/api/oauth/instagram/callback`

---

## Testing Your Connection

After connecting:
1. Go to Dashboard → Instagram Tools
2. Generate or upload a video
3. Click "Post to Instagram"
4. Your video should be posted!

---

## Resources

- [Facebook Graph API Documentation](https://developers.facebook.com/docs/instagram-api/)
- [Instagram Content Publishing API](https://developers.facebook.com/docs/instagram-api/guides/content-publishing/)
- [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)



