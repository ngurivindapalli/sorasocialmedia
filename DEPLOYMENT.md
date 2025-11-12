# 🚀 Deploying to Vercel

This guide will help you deploy your Instagram → Sora Video Generator to Vercel.

## Prerequisites

- GitHub account
- Vercel account (free tier works!)
- OpenAI API key

## Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit - Instagram Sora Generator"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Vercel

### Option A: Via Vercel Dashboard (Easiest)

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Add environment variable:
   - Name: `OPENAI_API_KEY`
   - Value: Your OpenAI API key (starts with `sk-proj-...`)
6. Click **"Deploy"**

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel

# Follow the prompts and add your OPENAI_API_KEY when asked
```

## Step 3: Configure Environment Variables

After deployment, add your environment variables in the Vercel dashboard:

1. Go to your project settings
2. Navigate to **"Environment Variables"**
3. Add:
   - **OPENAI_API_KEY**: Your OpenAI API key

## Important Notes

### Backend Limitations on Vercel

⚠️ **Vercel has serverless function limitations:**
- **10-second timeout** on Hobby plan (60s on Pro)
- Sora video generation can take 30-120 seconds
- **Solution**: Video generation will timeout on Vercel

### Recommended Architecture for Production

For a production app with long-running tasks like Sora video generation, consider:

1. **Keep Frontend on Vercel** (works great!)
2. **Deploy Backend Separately**:
   - **Railway.app** (recommended - easy Python hosting)
   - **Render.com** (free tier available)
   - **AWS Lambda** with increased timeout
   - **Google Cloud Run**
   - **DigitalOcean App Platform**

### Quick Fix: Deploy Backend to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Navigate to backend
cd backend

# Initialize and deploy
railway init
railway up

# Get your backend URL (e.g., https://your-app.railway.app)
# Update frontend/.env.production:
# VITE_API_URL=https://your-app.railway.app
```

## Alternative: Frontend-Only Deployment

If you want to deploy just the frontend to Vercel and run the backend locally:

1. Update `frontend/.env.production`:
   ```
   VITE_API_URL=http://your-backend-url.com
   ```

2. Deploy backend to Railway/Render
3. Deploy frontend to Vercel

## Project Structure

```
x-video-hook-generator/
├── frontend/           # React + Vite app
│   ├── .env.local      # Local development (http://localhost:8000)
│   └── .env.production # Production (uses /api or external URL)
├── backend/            # FastAPI Python server
│   └── main.py
├── vercel.json         # Vercel configuration
└── .vercelignore       # Files to ignore during deployment
```

## Post-Deployment

After deployment:
1. Visit your Vercel URL
2. Test the landing page
3. Try analyzing an Instagram account
4. Note: Sora generation may timeout on Vercel free tier

## Troubleshooting

### "Failed to analyze videos"
- Check your OPENAI_API_KEY is set correctly
- Check Vercel function logs in dashboard

### "Timeout error"
- Sora generation takes too long for Vercel serverless
- Consider deploying backend to Railway/Render

### CORS errors
- Ensure `vercel.json` has correct routes
- Check backend CORS middleware includes your domain

## Need Help?

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
