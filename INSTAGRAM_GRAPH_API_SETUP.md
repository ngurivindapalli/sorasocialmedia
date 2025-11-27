# Instagram Graph API Setup Guide

This guide explains how to set up Instagram Graph API to avoid blocking issues when running on cloud servers.

## Why Use Graph API?

- ✅ **No blocking** - Official API, won't get rate limited like scraping
- ✅ **Reliable** - Works consistently on cloud servers
- ✅ **Legal** - Official Instagram API, no ToS violations
- ✅ **Better data** - More structured and complete data

## Prerequisites

1. **Facebook Developer Account** - Free to create
2. **Instagram Business or Creator Account** - The account you want to analyze
3. **Facebook Page** - Connected to your Instagram account

## Setup Steps

### 1. Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"My Apps"** → **"Create App"**
3. Choose **"Business"** as the app type
4. Fill in app details:
   - App Name: Your app name
   - App Contact Email: Your email
   - Business Account: (optional)

### 2. Add Instagram Product

1. In your Facebook App dashboard, go to **"Add Products"**
2. Find **"Instagram"** and click **"Set Up"**
3. Choose **"Instagram Graph API"**

### 2.5. Select Use Cases

When prompted to select use cases, choose:

**✅ Recommended Use Cases:**
- **"Manage everything on your Page"** (Pages API) - This gives you access to Instagram Business accounts connected to your Facebook Page
- **"Access the Instagram Graph API"** (if available) - Direct access to Instagram content

**❌ Not Needed:**
- "Access the Threads API" - Only if you need Threads
- "Access the Live Video API" - Only for live streaming
- "Embed Facebook, Instagram and Threads content" (oEmbed) - Only for embedding, not data fetching

**Note:** The exact use case names may vary. Look for options that mention:
- Instagram content access
- Pages management
- Instagram Business accounts
- Content management (for Instagram)

### 3. Configure Instagram Basic Display

1. Go to **"Basic Display"** in the left sidebar
2. Click **"Create New App"**
3. Add **OAuth Redirect URIs**:
   - `http://localhost:8000/auth/instagram/callback` (for local testing)
   - Your production URL (if applicable)

### 4. Get Access Token

You have two options:

#### Option A: Long-Lived User Access Token (Recommended)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **"Generate Access Token"**
4. Select permissions:
   
   **From "Events Groups Pages" category:**
   - ✅ `pages_show_list` - Required: Lists your Facebook Pages
   - ✅ `business_management` - Recommended: Helps manage business accounts
   
   **Note:** `pages_read_engagement` might not be visible yet. This is normal! It may:
   - Appear after you connect a Facebook Page
   - Be added automatically when you add the Instagram product
   - Be available in a different category
   
   **Look for Instagram-specific permissions:**
   - Check other dropdown categories for "Instagram" permissions
   - Look for `instagram_basic` or similar Instagram permissions
   - These might be in a separate "Instagram" category
   
   **Don't worry if some permissions aren't visible yet** - you can add them later or they'll appear as you complete the setup.

5. **Important: Add `pages_read_engagement` Permission**
   
   This permission is **required** to access Instagram business accounts. If you get an error saying you need this permission:
   
   - Try searching for it in the permission dropdown
   - It might be in a different category
   - You may need to go through App Review (see troubleshooting below)
   - Or it might become available after connecting a Page
   
6. Copy the short-lived token
7. Exchange it for a long-lived token:
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={app-id}&
     client_secret={app-secret}&
     fb_exchange_token={short-lived-token}
   ```

#### Option B: Page Access Token

1. Go to your Facebook Page settings
2. Navigate to **"Instagram"** section
3. Connect your Instagram Business account
4. Get the Page Access Token from Graph API Explorer

### 5. Get Instagram Business Account ID

1. In Graph API Explorer, use your access token
2. Query: `GET /me/accounts?fields=instagram_business_account`
   - **If you see empty data `[]`**: You need to connect a Facebook Page first (see troubleshooting below)
   - **If you see pages**: Look for the `instagram_business_account.id` in the response
3. Alternative: If you know your Page ID, query directly:
   - `GET /{page-id}?fields=instagram_business_account`
4. Copy the `instagram_business_account.id` - this is your Instagram Account ID

**Troubleshooting Empty Results:**
- Make sure you have a Facebook Page created
- Connect your Instagram Business/Creator account to the Page
- Make sure the Page is connected to your Facebook App
- The Instagram account must be Business or Creator type (not personal)

### 6. Configure Your App

Add to your `backend/.env` file:

```env
# Instagram Graph API (Official API - No Blocking!)
# Use Page Access Token (recommended) or User Access Token
INSTAGRAM_PAGE_ACCESS_TOKEN=your_page_access_token_here  # Recommended - from /me/accounts response
# OR
INSTAGRAM_ACCESS_TOKEN=your_user_access_token_here  # Alternative - User token
INSTAGRAM_GRAPH_API_VERSION=v21.0
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id_here
```

**Note:** Page Access Tokens are often more reliable and have more permissions automatically. Use the `access_token` from the `/me/accounts` response.

## Using Graph API in Your App

The app will automatically use Graph API if `INSTAGRAM_ACCESS_TOKEN` is set. Otherwise, it falls back to scraping.

## Limitations

- **Business/Creator Accounts Only**: Graph API only works with Business or Creator Instagram accounts
- **Connected Accounts**: The Instagram account must be connected to your Facebook App
- **Permissions**: You need appropriate permissions to access user data
- **Rate Limits**: 200 requests per hour (but much more reliable than scraping)

## Testing

1. Set `INSTAGRAM_ACCESS_TOKEN` in your `.env`
2. Restart your backend server
3. Try analyzing an Instagram account
4. You should see `[IG Graph API]` in the logs instead of `[IG]`

## Troubleshooting

### "Access token is invalid"
- Make sure you're using a long-lived token
- Check that the token hasn't expired
- Verify the token has the right permissions

### "Missing pages_read_engagement permission" (Error #100)
This is a common issue. The `pages_read_engagement` permission is **required** and typically needs Facebook App Review.

**Solutions:**

1. **Request App Review (Recommended)**
   - Go to your App Dashboard → **App Review** → **Permissions and Features**
   - You'll see your current permissions listed (pages_show_list, business_management, etc.)
   - **Add the missing permission:**
     - Look for "Add Permissions" or "Request Permissions" button
     - Search for and add `pages_read_engagement`
     - OR request the **"Page Public Content Access"** feature (which grants this permission automatically)
   - Fill out the required information:
     - Use case description: "Analyzing Instagram videos for content creation and AI video generation"
     - Screenshots/video of your app
     - Privacy policy URL
   - Click "Next" to continue through the submission process
   - Submit for review (typically takes 2-7 business days)

2. **Use Scraping as Temporary Solution**
   - While waiting for App Review, continue using the scraping method
   - It works but may get blocked on cloud servers
   - Once App Review is approved, switch to Graph API

3. **Alternative: Use Instagram Basic Display API**
   - This is for personal accounts and has different limitations
   - Not ideal for business use cases

**Note:** Even Page Access Tokens require App Review for `pages_read_engagement`. This is a Facebook security requirement.

### "Cannot find user" or "Could not find Instagram user ID"

This error means the Graph API can't find the Instagram account. Here's how to fix it:

**Solution 1: Set INSTAGRAM_ACCOUNT_ID (Recommended)**
1. Get your Instagram Business Account ID (see step 5 in setup)
2. Add it to your `.env` file:
   ```env
   INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id_here
   ```
3. Restart your backend server

**Solution 2: Connect Account to Facebook App**
- The Instagram account must be a Business/Creator account
- The account must be connected to your Facebook App
- The account must be connected to a Facebook Page that's linked to your app

**Solution 3: Use Scraping Fallback**
- The app will automatically fall back to scraping if Graph API fails
- This works but may get blocked on cloud servers

### "Rate limit reached"
- Graph API has a limit of 200 requests/hour
- Implement caching to reduce API calls
- Wait before retrying

## Resources

- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)

