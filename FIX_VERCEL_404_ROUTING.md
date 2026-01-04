# 🔧 Fix: Vercel 404 Errors on Routes (e.g., /signup)

## The Problem
Routes like `/signup`, `/terms-of-service`, etc. are showing 404 errors even though they're defined in React Router.

## Root Cause
Vercel needs to be configured to serve `index.html` for all routes (SPA routing), but static assets should still be served normally.

## Solution Steps

### Step 1: Verify Vercel Project Settings

1. **Go to Vercel Dashboard:**
   - [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click your project

2. **Check Root Directory:**
   - Settings → General → Root Directory
   - Should be: `frontend`
   - If not, change it to `frontend` and save

3. **Check Build Settings:**
   - Settings → General → Build & Development Settings
   - Framework Preset: `Vite`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install`

### Step 2: Verify vercel.json Location

Since Root Directory is `frontend`, Vercel will look for:
- ✅ `frontend/vercel.json` (this is what we have)
- ❌ Root `vercel.json` (might be ignored, but could cause confusion)

### Step 3: Current Configuration

Your `frontend/vercel.json` should have:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Step 4: Manual Redeploy

1. **Vercel Dashboard → Deployments**
2. Click **three dots (⋯)** on latest deployment
3. Click **"Redeploy"**
4. **Turn OFF** "Use existing Build Cache"
5. Click **"Redeploy"**

### Step 5: Clear Browser Cache

After deployment:
1. Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Or clear cache completely

### Step 6: Test Routes

After redeploy, test:
- `https://aigismarketing.com/` → Landing page
- `https://aigismarketing.com/signup` → Signup page
- `https://aigismarketing.com/terms-of-service` → Terms page
- `https://aigismarketing.com/privacy-policy` → Privacy page

## Alternative: Remove Root vercel.json

If it still doesn't work, the root `vercel.json` might be interfering:

1. **Delete or rename root `vercel.json`:**
   ```bash
   git mv vercel.json vercel.json.backup
   git commit -m "Move root vercel.json to avoid conflicts"
   git push
   ```

2. **Redeploy in Vercel**

## Why This Happens

Vercel serves static files from the `dist` folder. When you visit `/signup`, Vercel looks for:
1. A file at `/signup` or `/signup.html` → Not found (404)
2. Should fall back to rewrite rule → Serve `/index.html`
3. React Router then handles the route client-side

If the rewrite isn't working, you get 404 errors.

## Still Not Working?

1. **Check Vercel Build Logs:**
   - Deployments → Latest → Build Logs
   - Look for errors or warnings

2. **Verify dist folder structure:**
   - After build, `dist` should contain:
     - `index.html`
     - `assets/` folder with JS/CSS files

3. **Test locally:**
   ```bash
   cd frontend
   npm run build
   npm run preview
   ```
   - Visit `http://localhost:4173/signup`
   - Should work (if it doesn't, the issue is in the code, not Vercel)

4. **Contact Vercel Support:**
   - [vercel.com/support](https://vercel.com/support)
   - Include deployment URL and error screenshots









