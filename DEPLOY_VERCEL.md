# 🚀 Quick Vercel Deployment Guide

## Frontend Deployment (5 minutes)

### Option 1: Deploy via Vercel Dashboard (Easiest)

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub

2. **Click "Add New..." → "Project"**

3. **Import your GitHub repository**
   - Find `x-video-hook-generator` (or your repo name)
   - Click "Import"

4. **Configure Project Settings:**
   - **Root Directory:** `frontend` ⚠️ **CRITICAL!**
   - Framework: Vite (auto-detected)
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `dist` (auto-detected)

5. **Add Environment Variable:**
   - **Name:** `VITE_API_URL`
   - **Value:** Your backend URL (e.g., `https://your-backend.onrender.com` or your Vercel backend URL)
   - ✅ Check **ALL** environments (Production, Preview, Development)

6. **Click "Deploy"** and wait 1-2 minutes

### Option 2: Deploy via Vercel CLI (Faster for updates)

```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (your account)
# - Link to existing project? No (first time) or Yes (updates)
# - What's your project's name? aigis-marketing
# - In which directory is your code located? ./
# - Override settings? No

# Set environment variable
vercel env add VITE_API_URL
# Enter your backend URL when prompted
# Select: Production, Preview, Development

# Deploy to production
vercel --prod
```

## Backend Deployment Options

### Option A: Deploy Backend to Vercel (Serverless Functions)

Vercel supports Python serverless functions. Create `api/index.py`:

```python
# This would require refactoring - not recommended for quick deployment
```

**Not recommended** - requires significant refactoring.

### Option B: Deploy Backend to Render (Recommended - 5 minutes)

1. **Go to [render.com](https://render.com)** and sign in

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**

4. **Configure:**
   - **Name:** `aigis-marketing-backend`
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`

5. **Add Environment Variables:**
   - Copy all variables from `backend/.env`
   - Add them in Render dashboard

6. **Click "Create Web Service"**

7. **Get your backend URL** (e.g., `https://aigis-marketing-backend.onrender.com`)

8. **Update frontend environment variable:**
   - Go back to Vercel
   - Update `VITE_API_URL` to your Render backend URL

### Option C: Deploy Backend to Railway (Alternative)

1. **Go to [railway.app](https://railway.app)** and sign in

2. **Click "New Project" → "Deploy from GitHub repo"**

3. **Select your repository**

4. **Add service:**
   - Select `backend` directory
   - Railway auto-detects Python
   - Add environment variables from `backend/.env`

5. **Deploy** - Railway gives you a URL automatically

## Quick Deploy Script

Run this from project root:

```bash
# Frontend deployment
cd frontend
vercel --prod

# Or use the dashboard method above
```

## Environment Variables Checklist

### Frontend (Vercel):
- `VITE_API_URL` = Your backend URL

### Backend (Render/Railway):
- `OPENAI_API_KEY`
- `HYPERSPELL_API_KEY`
- `GOOGLE_CLOUD_PROJECT_ID` (if using image generation)
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` (if using image generation)
- Database URL (if using external DB)
- Any other keys from `backend/.env`

## After Deployment

1. **Test frontend:** Visit your Vercel URL
2. **Test backend:** Visit `https://your-backend-url/api/health`
3. **Test connection:** Try logging in or generating a post

## Updating After Deployment

**Frontend:**
```bash
cd frontend
git add .
git commit -m "Update frontend"
git push
# Vercel auto-deploys!
```

**Backend:**
```bash
cd backend
git add .
git commit -m "Update backend"
git push
# Render/Railway auto-deploys!
```

## Troubleshooting

- **Frontend build fails:** Check Root Directory is `frontend`
- **API calls fail:** Check `VITE_API_URL` is set correctly
- **CORS errors:** Make sure backend CORS includes your Vercel domain
- **Backend not starting:** Check environment variables in Render/Railway dashboard

