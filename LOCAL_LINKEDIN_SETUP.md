# Local LinkedIn OAuth Setup Guide

## Quick Setup Steps

### 1. Update LinkedIn Developer Portal

Add **BOTH** redirect URLs to your LinkedIn app:

1. Go to: https://www.linkedin.com/developers/apps
2. Click your app → **"Auth"** tab
3. Under **"Authorized redirect URLs for your app"**, add:
   - `http://localhost:8000/api/oauth/linkedin/callback` (for local testing)
   - `https://aigismarketing.com/api/oauth/linkedin/callback` (for production)
4. Click **"Update"**

### 2. Update Backend Environment Variables

Make sure your `backend/.env` file has:

```bash
# LinkedIn OAuth (add your credentials)
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Backend URL (for local testing)
BASE_URL=http://localhost:8000

# Frontend URL (for redirect after OAuth)
FRONTEND_URL=http://localhost:3000
```

### 3. Start Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Start Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3000/
```

### 5. Test LinkedIn Connection

1. Open browser: http://localhost:3000
2. Go to: **Settings** tab
3. Find **"Social Media Connections"** section
4. Click **"Connect LinkedIn"** button
5. You'll be redirected to LinkedIn
6. Authorize the app
7. You'll be redirected back to: `http://localhost:3000/dashboard?tab=settings&connected=linkedin`
8. You should see "✓ Successfully connected LinkedIn!"

## Verification

After connecting, verify:

1. **Check connections:**
   ```bash
   curl http://localhost:8000/api/connections
   ```
   Should show your LinkedIn connection with `"platform": "linkedin"` and `"is_active": true`

2. **Test posting:**
   ```bash
   python test_linkedin_post.py
   ```

## Troubleshooting

### "redirect_uri_mismatch"
- ✅ Make sure `http://localhost:8000/api/oauth/linkedin/callback` is added in LinkedIn Developer Portal
- ✅ Verify `BASE_URL=http://localhost:8000` in backend `.env`
- ✅ Restart backend after changing `.env`

### "LinkedIn OAuth not configured"
- ✅ Check `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` are in `.env`
- ✅ Restart backend

### "Failed to connect LinkedIn"
- ✅ Check backend is running on port 8000
- ✅ Check backend logs for errors
- ✅ Verify LinkedIn app has `w_member_social` permission

### Frontend can't reach backend
- ✅ Check `VITE_API_URL` in frontend (should be `http://localhost:8000` or empty for default)
- ✅ Check CORS is enabled in backend (should allow `http://localhost:3000`)

## Next Steps

Once connected locally:
1. ✅ Test posting with `test_linkedin_post.py`
2. ✅ Generate a marketing post with LinkedIn platform
3. ✅ Post videos/images to LinkedIn
