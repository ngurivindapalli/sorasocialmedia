# Render Deployment Guide for Frontend

This guide will help you deploy the Vite frontend to Render as a static site.

## Prerequisites

1. A GitHub account with your repository pushed
2. A Render account (sign up at [render.com](https://render.com))
3. Your backend already deployed on Render (or elsewhere)

## Step-by-Step Setup

### 1. Ensure Your Code is on GitHub

```bash
git add .
git commit -m "Update Render configuration"
git push origin main
```

### 2. Deploy via Render Dashboard

#### Option A: Using render.yaml (Recommended)

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create both services:
   - Backend (web service)
   - Frontend (static site)

#### Option B: Manual Setup

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Static Site"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `sorasocialmedia-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`

### 3. Environment Variables

Add environment variables in Render dashboard:

**VITE_API_URL** - Your backend URL:
- If backend is on Render: `https://sorasocialmedia-backend.onrender.com`
- If backend is elsewhere: Your backend URL (e.g., `https://your-backend.railway.app`)

### 4. Deploy

Click **"Create Static Site"** and wait for deployment.

## Configuration Files

The project includes:
- `render.yaml` - Render Blueprint configuration (defines both backend and frontend)
- Frontend is configured as a `static` site type

## Important Notes

### Backend URL

You must set `VITE_API_URL` environment variable in Render to point to your backend:
- **Same Render account**: `https://sorasocialmedia-backend.onrender.com`
- **Different service**: Your backend URL

### CORS Configuration

Make sure your backend allows requests from your Render frontend domain:
- Add your Render frontend URL to backend CORS origins
- Example: `https://sorasocialmedia-frontend.onrender.com`

### React Router

The static site configuration will serve your React Router app correctly. Render automatically handles SPA routing.

## Troubleshooting

### Build Fails

1. Check build logs in Render dashboard
2. Verify `rootDir: frontend` is correct
3. Ensure all dependencies are in `frontend/package.json`
4. Check Node.js version (Render uses Node 18+ by default)

### API Calls Fail

1. Verify `VITE_API_URL` environment variable is set correctly
2. Check backend CORS settings include your Render frontend domain
3. Ensure backend is running and accessible

### 404 Errors on Routes

Static sites on Render automatically handle React Router. If you see 404s:
- Verify `staticPublishPath: dist` is set correctly
- Check that build is creating the `dist` folder
- Ensure `index.html` is in the dist folder

### PowerShell Error

If you see "powershell: not found":
- This means Render is trying to run the root `package.json` start script
- Make sure you're deploying the **static site** from the `frontend` directory
- The `render.yaml` configuration avoids this issue

## Automatic Deployments

Once connected:
- **Every push to `main` branch** = Automatic deployment
- Build logs available in Render dashboard

## Custom Domain (Optional)

1. Go to your static site settings in Render
2. Click **"Custom Domains"**
3. Add your domain
4. Follow DNS configuration instructions

## Multiple Environments

You can create separate static sites for staging/production:
- Use different branches or environments
- Set different `VITE_API_URL` values per environment

## Support

For issues:
- Check Render documentation: [render.com/docs](https://render.com/docs)
- Check build logs in Render dashboard
- Verify all environment variables are set
- Ensure backend is accessible

