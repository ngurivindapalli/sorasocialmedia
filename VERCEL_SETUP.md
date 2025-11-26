# Vercel Deployment Guide

This guide will help you deploy the frontend of this project to Vercel.

## Prerequisites

1. A GitHub account
2. A Vercel account (sign up at [vercel.com](https://vercel.com))
3. Your project pushed to GitHub

## Step-by-Step Setup

### 1. Push Your Code to GitHub

Make sure your code is pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Connect to Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository:
   - Click **"Import Git Repository"**
   - Select your repository (`sorasocialmedia` or your repo name)
   - Click **"Import"**

### 3. Configure Project Settings

Vercel should auto-detect the settings, but verify:

**Framework Preset:** `Vite`

**Root Directory:** `frontend`

**Build Command:** `npm run build`

**Output Directory:** `dist`

**Install Command:** `npm install`

### 4. Environment Variables (Optional)

If your frontend needs environment variables, add them in Vercel:

1. In the project settings, go to **"Environment Variables"**
2. Add any variables your app needs, for example:
   - `VITE_API_URL` - Your backend API URL (e.g., `https://your-backend.railway.app` or `http://localhost:8000` for local)

**Note:** Since your backend is separate, make sure to set `VITE_API_URL` to point to your backend server URL.

### 5. Deploy

1. Click **"Deploy"**
2. Wait for the build to complete
3. Your app will be live at `https://your-project.vercel.app`

## Configuration Files

The project includes:
- `vercel.json` - Vercel configuration (already configured)
- `.vercelignore` - Files to ignore during deployment

## Important Notes

### Backend API URL

Since your backend runs separately (likely on Railway, Render, or another service), you need to:

1. **Set the `VITE_API_URL` environment variable in Vercel** to point to your backend
2. Or update `frontend/src/utils/api.js` to use your production backend URL

### CORS Configuration

Make sure your backend allows requests from your Vercel domain. Update your backend CORS settings to include:
```python
origins = [
    "https://your-project.vercel.app",
    "http://localhost:3001",  # For local development
]
```

## Automatic Deployments

Once connected:
- **Every push to `main` branch** = Automatic production deployment
- **Pull requests** = Automatic preview deployments

## Troubleshooting

### Build Fails

1. Check the build logs in Vercel dashboard
2. Ensure all dependencies are in `frontend/package.json`
3. Verify Node.js version (Vercel uses Node 18+ by default)

### API Calls Fail

1. Check `VITE_API_URL` environment variable is set correctly
2. Verify backend CORS settings allow your Vercel domain
3. Check backend is running and accessible

### 404 Errors on Routes

The `vercel.json` includes a rewrite rule to handle React Router. If you see 404s:
- Verify the rewrite rule in `vercel.json` is correct
- Check that `outputDirectory` is set to `frontend/dist`

## Updating Your Deployment

Simply push to GitHub:
```bash
git push origin main
```

Vercel will automatically:
1. Detect the push
2. Build your project
3. Deploy the new version

## Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Click **"Domains"**
3. Add your custom domain
4. Follow DNS configuration instructions

## Support

For issues:
- Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)
- Check build logs in Vercel dashboard
- Verify all environment variables are set

