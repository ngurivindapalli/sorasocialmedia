# Deploy Frontend to Render (Manual Setup)

Since Render Blueprints don't support static sites in `render.yaml`, you need to deploy the frontend separately as a Static Site.

## Quick Setup Steps

### 1. Deploy Backend First (via Blueprint)

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will create the backend service from `render.yaml`
5. Wait for backend to deploy and note the URL (e.g., `https://sorasocialmedia-backend.onrender.com`)

### 2. Deploy Frontend as Static Site

1. In Render dashboard, click **"New +"** → **"Static Site"**
2. **Connect Repository**: Select your GitHub repository
3. **Configure Settings**:
   - **Name**: `sorasocialmedia-frontend` (or your preferred name)
   - **Branch**: `main`
   - **Root Directory**: `frontend` ⚠️ **IMPORTANT**
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

4. **Environment Variables**:
   - Click **"Add Environment Variable"**
   - **Key**: `VITE_API_URL`
   - **Value**: Your backend URL from step 1 (e.g., `https://sorasocialmedia-backend.onrender.com`)

5. Click **"Create Static Site"**

### 3. Wait for Deployment

- Render will install dependencies, build your Vite app, and deploy
- Your frontend will be available at `https://sorasocialmedia-frontend.onrender.com`

## Configuration Summary

| Setting | Value |
|---------|-------|
| **Service Type** | Static Site |
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |
| **Environment Variable** | `VITE_API_URL=https://sorasocialmedia-backend.onrender.com` |

## CORS Setup

Make sure your backend allows requests from your frontend domain:

In your backend CORS configuration, add:
```python
origins = [
    "https://sorasocialmedia-frontend.onrender.com",
    "http://localhost:3001",  # For local development
]
```

## Automatic Deployments

Both services will automatically redeploy when you push to your `main` branch.

## Custom Domain

1. Go to your static site settings
2. Click **"Custom Domains"**
3. Add your domain and follow DNS instructions

## Troubleshooting

### Build Fails

- Check that **Root Directory** is set to `frontend`
- Verify `frontend/package.json` exists and has all dependencies
- Check build logs for specific errors

### API Calls Fail

- Verify `VITE_API_URL` environment variable is set correctly
- Ensure backend URL is accessible (check backend service status)
- Verify CORS settings on backend

### 404 Errors on Routes

- Static sites on Render automatically handle React Router
- If issues persist, check that `dist/index.html` is generated correctly

## Alternative: Use Vercel for Frontend

If you prefer, you can:
1. Keep backend on Render
2. Deploy frontend to Vercel (see `VERCEL_SETUP.md`)
3. Set `VITE_API_URL` to your Render backend URL

