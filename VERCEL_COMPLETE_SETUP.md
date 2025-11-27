# Complete Vercel Setup Guide for VideoHook

This guide will help you deploy your Instagram Video Maker and Video Hook tools to Vercel so users can test them.

## Prerequisites

1. ✅ GitHub account with your repository
2. ✅ Vercel account (free at [vercel.com](https://vercel.com))
3. ✅ Backend deployed somewhere (Railway, Render, etc.)

## Quick Setup (5 Minutes)

### Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:
```bash
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

### Step 2: Deploy to Vercel

1. Go to **[vercel.com](https://vercel.com)** and sign in with GitHub
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. **IMPORTANT**: Click **"Edit"** next to "Root Directory"
   - Change from `./` to `frontend`
   - This tells Vercel to build from the frontend folder
5. Vercel will auto-detect:
   - ✅ Framework: Vite
   - ✅ Build Command: `npm run build`
   - ✅ Output Directory: `dist`
6. **Add Environment Variable**:
   - Click **"Environment Variables"**
   - Add: `VITE_API_URL`
   - Value: Your backend URL (e.g., `https://your-backend.railway.app`)
   - Make sure to check all environments (Production, Preview, Development)
7. Click **"Deploy"**

### Step 3: Wait for Deployment

- Build takes 1-2 minutes
- Your app will be live at `https://your-project.vercel.app`
- **Users land directly on Instagram Tools page** (already configured!)

## Configuration Summary

| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` |
| **Framework** | Vite |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Environment Variable** | `VITE_API_URL` = your backend URL |

## What Users Will See

When users visit your Vercel URL:
1. ✅ They land directly on the **Instagram Tools** page (no landing page)
2. ✅ Can immediately start testing:
   - Single User Analysis
   - Multi-User Analysis  
   - **Informational Video Generation** (Instagram username + duration)
3. ✅ All features work as expected

## Backend Connection

Your frontend needs to connect to your backend. Set the `VITE_API_URL` environment variable:

### Option 1: Backend on Railway
```
VITE_API_URL=https://your-app.railway.app
```

### Option 2: Backend on Render
```
VITE_API_URL=https://your-backend.onrender.com
```

### Option 3: Backend on Other Service
```
VITE_API_URL=https://your-backend-url.com
```

## CORS Setup (Backend)

Make sure your backend allows requests from Vercel. Add to your backend CORS settings:

```python
origins = [
    "https://your-project.vercel.app",  # Your Vercel URL
    "https://*.vercel.app",              # All Vercel preview deployments
    "http://localhost:3001",             # Local development
]
```

## Automatic Deployments

Once connected:
- ✅ **Every push to `main`** = Auto-deploy to production
- ✅ **Pull requests** = Auto-deploy preview URLs
- ✅ **Zero downtime** deployments

## Testing Checklist

After deployment, test:
1. ✅ Visit your Vercel URL
2. ✅ Verify you land on Instagram Tools page
3. ✅ Test Single User Analysis
4. ✅ Test Informational Video Generation:
   - Enter Instagram username
   - Set video duration (5-16 seconds)
   - Generate video
5. ✅ Check that videos appear and don't disappear
6. ✅ Verify API calls work (check browser console)

## Custom Domain (Optional)

To use your own domain:
1. Go to Vercel project settings
2. Click **"Domains"**
3. Add your domain (e.g., `videohook.com`)
4. Follow DNS instructions
5. Update backend CORS to include your custom domain

## Environment Variables

Add these in Vercel dashboard under **Settings → Environment Variables**:

| Variable | Value | Required |
|----------|-------|----------|
| `VITE_API_URL` | Your backend URL | ✅ Yes |

## Troubleshooting

### Build Fails
- ✅ Check Root Directory is set to `frontend`
- ✅ Verify `frontend/package.json` exists
- ✅ Check build logs for specific errors

### API Calls Fail (404/500)
- ✅ Verify `VITE_API_URL` is set correctly
- ✅ Check backend is running and accessible
- ✅ Verify CORS settings on backend
- ✅ Test backend URL directly in browser

### Users See Landing Page
- ✅ Check that Dashboard defaults to Instagram tab (already configured)
- ✅ App.jsx should redirect `/` to `/dashboard`
- ✅ Dashboard should default to `instagram` tab

### Video Disappears
- ✅ This should be fixed (video URL preservation is implemented)
- ✅ Check browser console for errors
- ✅ Verify video generation completes successfully

### CORS Errors
```
Access to XMLHttpRequest blocked by CORS policy
```
**Fix**: Add your Vercel domain to backend CORS origins

## Updating the App

To update your deployed app:
```bash
# Make your changes
git add .
git commit -m "Update features"
git push origin main
```

Vercel automatically:
1. Detects the push
2. Builds the new version
3. Deploys it (zero downtime)

## Sharing with Users

Your app is ready to share:
1. Copy your Vercel URL: `https://your-project.vercel.app`
2. Share with users
3. They can immediately start testing!

## Support

- 📖 [Vercel Docs](https://vercel.com/docs)
- 🔍 Check build logs in Vercel dashboard
- 🐛 Check browser console for errors
- 📧 Check backend logs if API calls fail

---

## Quick Reference

**Deploy URL**: `https://your-project.vercel.app`
**Backend URL**: Set in `VITE_API_URL` environment variable
**Root Directory**: `frontend`
**Build Time**: ~1-2 minutes

