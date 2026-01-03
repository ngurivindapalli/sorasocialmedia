# 🔧 Vercel Deployment Troubleshooting

## Common Issues and Fixes

### Issue 1: Build Fails

**Symptoms:**
- Deployment shows "Build Failed" in Vercel dashboard
- Error logs show build errors

**Solutions:**

1. **Check Root Directory:**
   - Vercel Dashboard → Settings → General
   - **Root Directory** should be: `frontend`
   - If it's `.` or empty, change it to `frontend`

2. **Check Build Settings:**
   - **Framework Preset:** Vite (or auto-detect)
   - **Build Command:** `npm run build` (should auto-detect)
   - **Output Directory:** `dist` (should auto-detect)
   - **Install Command:** `npm install` (should auto-detect)

3. **Check for Missing Dependencies:**
   - Look at build logs for "Module not found" errors
   - Make sure all dependencies are in `package.json`

4. **Check Node Version:**
   - Vercel Settings → General → Node.js Version
   - Should be `18.x` or `20.x` (latest LTS)

### Issue 2: Landing Page Not Showing

**Symptoms:**
- Site loads but shows dashboard or 404
- Root path `/` doesn't show landing page

**Solutions:**

1. **Verify Routing:**
   - Check `frontend/src/App.jsx`
   - Root route should be: `<Route path="/" element={<LandingPage />} />`

2. **Check Vercel Rewrites:**
   - `frontend/vercel.json` should have rewrites to `/index.html`
   - This is already configured correctly

3. **Clear Browser Cache:**
   - Hard refresh: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
   - Or clear cache completely

4. **Check Deployment:**
   - Make sure latest commit is deployed
   - Vercel Dashboard → Deployments → Check latest is successful

### Issue 3: 404 Errors on Routes

**Symptoms:**
- Direct URL access (e.g., `/dashboard`) shows 404
- Only root path works

**Solution:**
- This is fixed by the `rewrites` rule in `vercel.json`
- Make sure `vercel.json` has:
  ```json
  "rewrites": [
    {
      "source": "/((?!static-posts|assets|.*\\.(js|css|png|jpg|jpeg|gif|svg|ico|json|webp|mp4|webm)).*)",
      "destination": "/index.html"
    }
  ]
  ```

### Issue 4: Environment Variables Missing

**Symptoms:**
- Build succeeds but app doesn't work
- API calls fail

**Solution:**
- Vercel Dashboard → Settings → Environment Variables
- Add: `VITE_API_URL` = Your backend URL
- Make sure to select all environments (Production, Preview, Development)

### Issue 5: Build Timeout

**Symptoms:**
- Build takes too long and times out

**Solution:**
- Check `package.json` for unnecessary dependencies
- Remove unused packages
- Optimize build process

## Quick Verification Checklist

- [ ] Root Directory in Vercel is set to `frontend`
- [ ] Build Command is `npm run build`
- [ ] Output Directory is `dist`
- [ ] `frontend/src/App.jsx` has landing page as default route
- [ ] `frontend/vercel.json` exists and has rewrites
- [ ] Environment variables are set in Vercel
- [ ] Latest commit is pushed to GitHub
- [ ] Latest deployment in Vercel is successful

## How to Check Vercel Logs

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click your project
3. Go to **Deployments** tab
4. Click on the latest deployment
5. Click **"View Function Logs"** or check the build logs
6. Look for error messages (usually in red)

## Common Build Errors

### "Module not found"
- **Fix:** Check `package.json` has all dependencies
- Run `npm install` locally to verify

### "Cannot find module"
- **Fix:** Check import paths in code
- Verify all files exist

### "Build command failed"
- **Fix:** Check build logs for specific error
- Try building locally: `cd frontend && npm run build`

### "Deployment failed"
- **Fix:** Check all settings above
- Verify GitHub connection
- Check Vercel project settings

## Still Not Working?

1. **Check Vercel Status:**
   - Visit [vercel-status.com](https://vercel-status.com)
   - Make sure Vercel isn't having issues

2. **Redeploy:**
   - Vercel Dashboard → Deployments
   - Click three dots on latest deployment
   - Click "Redeploy"

3. **Contact Support:**
   - Vercel Support: [vercel.com/support](https://vercel.com/support)
   - Include deployment logs and error messages








