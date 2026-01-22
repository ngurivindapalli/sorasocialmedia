# How to Test LinkedIn Posting

## Quick Test Script

I've created a test script (`test_linkedin_post.py`) that will:
1. Check for active LinkedIn connections
2. Create a test post
3. Post it to LinkedIn
4. Return the post URL

## Prerequisites

1. ✅ LinkedIn OAuth credentials set (`LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`)
2. ✅ LinkedIn redirect URL added to LinkedIn Developer Portal
3. ✅ LinkedIn account connected via OAuth
4. ✅ Backend running (local or production)

## Usage

### Option 1: Test with Local Backend

1. **Start your backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **In another terminal, run the test script:**
   ```bash
   python test_linkedin_post.py
   ```

### Option 2: Test with Production Backend

1. **Set environment variable:**
   ```bash
   # Windows PowerShell
   $env:API_URL="https://your-backend.onrender.com"
   
   # Or edit test_linkedin_post.py and change:
   API_URL = "https://your-backend.onrender.com"
   ```

2. **Run the script:**
   ```bash
   python test_linkedin_post.py
   ```

## What the Script Does

1. **Checks for LinkedIn connections:**
   - Calls `/api/connections` endpoint
   - Filters for active LinkedIn connections
   - Shows available connections

2. **Creates a test post:**
   - Text-only post with test caption
   - Includes hashtags: #TestPost #AigisMarketing #LinkedInAPI

3. **Posts to LinkedIn:**
   - Uses `/api/post/video` endpoint
   - Posts to first available LinkedIn connection
   - Returns post URL if successful

## Expected Output

### Success:
```
============================================================
LinkedIn Test Post Script
============================================================

Step 1: Checking for LinkedIn connections...
OK: Found 1 LinkedIn connection(s):
   - ID: 1, Username: your-username

Step 2: Using connection ID: 1
   Username: your-username

Step 3: Creating test post...

Posting to LinkedIn (connection ID: 1)...
Caption: Test Post from Aigis Marketing...

POST SUCCESSFUL!
   Post ID: urn:li:ugcPost:1234567890
   Post URL: https://www.linkedin.com/feed/update/1234567890/
   Platform: linkedin

============================================================
SUCCESS! Test post created and published to LinkedIn
View your post: https://www.linkedin.com/feed/update/1234567890/
============================================================
```

### If No Connection Found:
```
ERROR: No active LinkedIn connections found

To connect LinkedIn:
   1. Go to: https://aigismarketing.com/dashboard?tab=settings
   2. Click 'Connect LinkedIn'
   3. Complete OAuth flow
```

## Troubleshooting

### "No connection could be made"
- **Solution:** Backend is not running
- Start backend: `cd backend && python main.py`

### "No active LinkedIn connections found"
- **Solution:** Connect LinkedIn account first
- Go to: `https://aigismarketing.com/dashboard?tab=settings`
- Click "Connect LinkedIn" and complete OAuth

### "401 Unauthorized" or "Invalid access token"
- **Solution:** Access token expired
- Disconnect and reconnect LinkedIn account
- LinkedIn tokens typically last 60 days

### "Insufficient permissions" or "w_member_social not available"
- **Solution:** LinkedIn app needs Marketing Developer Platform access
- Go to LinkedIn Developer Portal → Your App → Products
- Request `w_member_social` permission

### "redirect_uri_mismatch"
- **Solution:** Redirect URL doesn't match
- Verify redirect URL in LinkedIn Developer Portal matches exactly:
  - `https://aigismarketing.com/api/oauth/linkedin/callback`

## Manual Test via API

You can also test manually using curl or Postman:

```bash
# 1. Get connections
curl http://localhost:8000/api/connections

# 2. Post to LinkedIn (replace CONNECTION_ID)
curl -X POST http://localhost:8000/api/post/video \
  -H "Content-Type: application/json" \
  -d '{
    "connection_ids": [CONNECTION_ID],
    "caption": "Test post from API",
    "video_url": null,
    "image_url": null
  }'
```

## Next Steps

After successful test:
1. ✅ LinkedIn posting is working
2. ✅ You can now use the marketing post generator with LinkedIn platform
3. ✅ You can post videos/images via the API

## Notes

- The test post is a simple text post
- For video/image posts, provide `video_url` or `image_url` in the payload
- Posts are published immediately (no draft mode)
- Check your LinkedIn feed to verify the post appears
