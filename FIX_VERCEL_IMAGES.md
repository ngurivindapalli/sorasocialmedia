# 🖼️ Fix Images Not Loading on Vercel

## Problem

Images in `frontend/public/static-posts/images/` are not loading on Vercel deployment.

## Root Cause

Vite serves files from the `public` folder at the root URL. The rewrite rule in `vercel.json` was interfering with static asset serving.

## ✅ Solution Applied

### 1. Fixed `vercel.json`

**Removed the problematic rewrite rule:**
```json
{
  "source": "/static-posts/(.*)",
  "destination": "/static-posts/$1"
}
```

This rewrite was unnecessary and could interfere with static file serving.

**Added proper headers for static assets:**
```json
{
  "source": "/static-posts/(.*)",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=31536000, immutable"
    }
  ]
}
```

### 2. How Vite Serves Public Files

Files in `frontend/public/` are automatically:
- Copied to `dist/` during build
- Served from the root URL in production
- Accessible at `/static-posts/images/marketing-post-1.png`

### 3. Image Paths

The code correctly uses:
- JSON file: `/static-posts/posts.json`
- Images: `/static-posts/images/marketing-post-1.png` through `marketing-post-10.png`

## 🔍 Verify Images Are Included

### Check Build Output

After building, check `frontend/dist/static-posts/`:
```bash
cd frontend
npm run build
ls dist/static-posts/images/
```

You should see all 10 PNG files.

### Check on Vercel

1. Go to your Vercel deployment
2. Open browser DevTools (F12)
3. Go to Network tab
4. Reload the page
5. Look for requests to `/static-posts/images/marketing-post-*.png`
6. Check if they return 200 (success) or 404 (not found)

## 🚀 After Fix

1. **Push changes to GitHub:**
   ```bash
   git add frontend/vercel.json
   git commit -m "Fix Vercel image serving - remove interfering rewrite rule"
   git push origin main
   ```

2. **Vercel will auto-deploy** with the fix

3. **Verify images load:**
   - Visit your Vercel URL
   - Check the landing page
   - Images should appear in the falling gallery

## 📝 Image File Structure

```
frontend/
  public/
    static-posts/
      images/
        marketing-post-1.png
        marketing-post-2.png
        ...
        marketing-post-10.png
      posts.json
```

**In production (Vercel):**
```
https://your-app.vercel.app/static-posts/images/marketing-post-1.png
```

## 🆘 If Images Still Don't Load

### Check 1: Are images in the build?
- Go to Vercel deployment → Build Logs
- Check if `static-posts` folder is copied to `dist/`

### Check 2: Are paths correct?
- Open browser console
- Look for 404 errors for image files
- Verify the paths match what's in `posts.json`

### Check 3: Vercel build settings
- Make sure `Output Directory` is set to `dist`
- Make sure `Build Command` is `npm run build`
- Make sure `Root Directory` is set to `frontend`

### Check 4: File size limits
- Vercel has a 50MB limit per file
- Check if any images exceed this

## ✅ Expected Behavior

After the fix:
- ✅ Images load from `/static-posts/images/marketing-post-*.png`
- ✅ No 404 errors in browser console
- ✅ Images appear in the falling gallery animation
- ✅ All 10 images cycle through the 4 visible slots

