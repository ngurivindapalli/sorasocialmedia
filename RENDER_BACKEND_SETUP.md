# Deploy Backend to Render (Free Tier) - Complete Guide

This guide will walk you through deploying your FastAPI backend to Render's free tier so you can use it with your Vercel frontend.

## Prerequisites

1. ✅ GitHub account with your repository
2. ✅ Render account (sign up free at [render.com](https://render.com))
3. ✅ Your backend code in the `backend/` folder

## Step 1: Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account (easiest)
4. Authorize Render to access your repositories

## Step 2: Deploy Backend - Manual Setup (Free Tier)

**Note:** Blueprints may require payment. For free tier, use manual setup instead:

### Manual Setup (Free Tier Recommended)

1. **Create New Web Service:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click **"New +"** button (top right)
   - Select **"Web Service"** (NOT Blueprint)

2. **Connect Repository:**
   - Click **"Connect Repository"** or **"Connect GitHub"**
   - Authorize Render if needed
   - Find and select your repository (`sorasocialmedia` or your repo name)
   - Click **"Connect"**

3. **Configure Service Settings:**
   
   **Basic Settings:**
   - **Name:** `sorasocialmedia-backend` (or any name you prefer)
   - **Region:** Choose closest to you (or leave default)
   - **Branch:** `main`
   - **Root Directory:** `backend` ⚠️ **IMPORTANT - Change from `./` to `backend`**
   
   **Build Settings:**
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Choose FREE Instance Type:**
   - Scroll down to **"Instance Type"** section
   - **Select "Free"** ⚠️ **This is important - don't select a paid plan!**
   - You'll see it says "Free - 750 hours/month"

5. **Set Environment Variables:**
   - Scroll down to **"Environment Variables"** section
   - Click **"Add Environment Variable"** for each:
     
     **Required:**
     - `OPENAI_API_KEY` = Your OpenAI API key
     
     **Optional (for Veo 3):**
     - `GOOGLE_CLOUD_PROJECT_ID` = Your Google Cloud project ID
     - `VEO3_USE_GCLOUD_AUTH` = `true` (if using gcloud CLI)
     - `GOOGLE_APPLICATION_CREDENTIALS` = Path to service account JSON (if using)
     
     **Optional (for Instagram features):**
     - `INSTAGRAM_USERNAME` = Your Instagram username
     - `INSTAGRAM_PASSWORD` = Your Instagram password
     
     **Optional (for LinkedIn features):**
     - `LINKEDIN_CLIENT_ID` = Your LinkedIn client ID
     - `LINKEDIN_CLIENT_SECRET` = Your LinkedIn client secret

6. **Deploy:**
   - Review all settings
   - Make sure **"Free"** instance type is selected
   - Click **"Create Web Service"**
   - Render will start building and deploying
   - This takes about 3-5 minutes

7. **Get Your Backend URL:**
   - Once deployment completes, you'll see your service dashboard
   - Your backend URL will be shown at the top
   - It will be: `https://sorasocialmedia-backend.onrender.com` (or your chosen name)
   - **Copy this URL** - you'll need it for your Vercel frontend!

---

### Alternative: Blueprint Setup (May Require Payment)

If the blueprint method doesn't work, you can set it up manually:

1. **Create New Web Service:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click **"New +"** → **"Web Service"**

2. **Connect Repository:**
   - Click **"Connect Repository"**
   - Select your repository
   - Click **"Connect"**

3. **Configure Service:**
   - **Name:** `sorasocialmedia-backend`
   - **Region:** Choose closest to you (or leave default)
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables:**
   - Scroll down to **"Environment Variables"** section
   - Click **"Add Environment Variable"** for each:
     - `OPENAI_API_KEY` = your key
     - Add other optional variables as needed

5. **⚠️ IMPORTANT: Choose FREE Instance Type:**
   - Scroll down to **"Instance Type"** section
   - **Select "Free"** (shows "Free - 750 hours/month")
   - **DO NOT** select any paid plans (Starter, Standard, etc.)
   - Click **"Create Web Service"**

6. **Wait for Deployment:**
   - Build takes 3-5 minutes
   - Watch the logs to see progress

---

## Step 3: Important Render Free Tier Notes

### ⚠️ Free Tier Limitations:

1. **Service Sleeps After 15 Minutes of Inactivity:**
   - First request after sleep takes ~30 seconds (cold start)
   - Subsequent requests are fast
   - **Solution:** Use a service like [UptimeRobot](https://uptimerobot.com) to ping your backend every 10 minutes (free)

2. **750 Free Hours Per Month:**
   - Usually enough for development/testing
   - Shared across all your services

3. **No Custom Domain on Free Tier:**
   - Your URL will be: `https://sorasocialmedia-backend.onrender.com`
   - That's fine for testing!

### 🔄 Keep Service Awake (Optional):

To prevent cold starts, set up a free uptime monitor:

1. Sign up at [UptimeRobot.com](https://uptimerobot.com) (free)
2. Add a monitor:
   - **URL:** `https://sorasocialmedia-backend.onrender.com/api/health`
   - **Type:** HTTP(s)
   - **Interval:** 5 minutes
3. This will ping your backend every 5 minutes to keep it awake

---

## Step 4: Test Your Backend

Once deployment is complete:

1. **Health Check:**
   - Visit: `https://sorasocialmedia-backend.onrender.com/api/health`
   - Should return: `{"status": "healthy"}`

2. **API Documentation:**
   - Visit: `https://sorasocialmedia-backend.onrender.com/docs`
   - Should show FastAPI Swagger UI

3. **Test an Endpoint:**
   - Try: `https://sorasocialmedia-backend.onrender.com/api/`
   - Should show API info

---

## Step 5: Update Vercel Frontend

Now that your backend is deployed, update your Vercel frontend:

1. **Go to Vercel Dashboard:**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click on your frontend project

2. **Add Environment Variable:**
   - Go to **Settings** → **Environment Variables**
   - Click **"Add New"**
   - **Name:** `VITE_API_URL`
   - **Value:** `https://sorasocialmedia-backend.onrender.com`
   - ✅ Check all environments (Production, Preview, Development)
   - Click **"Save"**

3. **Redeploy:**
   - Go to **Deployments** tab
   - Click the three dots on latest deployment
   - Click **"Redeploy"**
   - Or just push a new commit to trigger auto-deploy

---

## Step 6: Update Backend CORS

Make sure your backend allows requests from Vercel:

Your `backend/main.py` already includes Vercel in CORS, but verify it has:

```python
allow_origins=[
    "https://your-frontend.vercel.app",  # Your Vercel URL
    "https://*.vercel.app",              # All Vercel preview deployments
    # ... other origins
]
```

If needed, update and redeploy.

---

## Configuration Summary

| Setting | Value |
|---------|-------|
| **Service Name** | `sorasocialmedia-backend` |
| **Type** | Web Service |
| **Runtime** | Python 3 |
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |
| **Your Backend URL** | `https://sorasocialmedia-backend.onrender.com` |

---

## Environment Variables Checklist

Set these in Render dashboard → Your service → Environment:

### Required:
- ✅ `OPENAI_API_KEY` - Your OpenAI API key

### Optional (for specific features):
- 🔹 `GOOGLE_CLOUD_PROJECT_ID` - For Veo 3 video generation
- 🔹 `GOOGLE_APPLICATION_CREDENTIALS` - Google Cloud service account JSON path
- 🔹 `VEO3_USE_GCLOUD_AUTH` - `true` if using gcloud CLI auth
- 🔹 `INSTAGRAM_USERNAME` - For Instagram features
- 🔹 `INSTAGRAM_PASSWORD` - For Instagram features
- 🔹 `LINKEDIN_CLIENT_ID` - For LinkedIn features
- 🔹 `LINKEDIN_CLIENT_SECRET` - For LinkedIn features

---

## Troubleshooting

### Build Fails

1. **Check Build Logs:**
   - Go to Render dashboard → Your service → Logs
   - Look for error messages

2. **Common Issues:**
   - Missing dependencies in `requirements.txt`
   - Python version mismatch
   - Missing environment variables

3. **Fix:**
   - Check `backend/requirements.txt` has all packages
   - Verify Python version in Render matches your local

### Service Won't Start

1. **Check Logs:**
   - Render dashboard → Logs tab
   - Look for startup errors

2. **Common Issues:**
   - Wrong start command
   - Missing environment variables
   - Port configuration issue

3. **Fix:**
   - Start command should be: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Make sure all required env vars are set

### 500 Errors / API Not Working

1. **Check Application Logs:**
   - Render dashboard → Logs
   - Look for Python errors

2. **Test Health Endpoint:**
   - Visit: `https://sorasocialmedia-backend.onrender.com/api/health`
   - If this works, backend is running

3. **Check Environment Variables:**
   - Verify all required variables are set correctly
   - Check for typos in variable names

### Service Keeps Sleeping

**Solution:** Set up UptimeRobot (free):
1. Go to [uptimerobot.com](https://uptimerobot.com)
2. Add HTTP monitor pointing to: `https://sorasocialmedia-backend.onrender.com/api/health`
3. Set interval to 5 minutes
4. Service will stay awake!

---

## Next Steps

1. ✅ Backend deployed to Render
2. ✅ Backend URL copied: `https://sorasocialmedia-backend.onrender.com`
3. ✅ Update Vercel frontend with `VITE_API_URL`
4. ✅ Test the full stack!

---

## Need Help?

- 📖 [Render Documentation](https://render.com/docs)
- 🔍 Check Render dashboard logs
- 💬 Render Community: [community.render.com](https://community.render.com)

---

## Quick Reference

**Your Backend URL:** `https://sorasocialmedia-backend.onrender.com`

**Health Check:** `https://sorasocialmedia-backend.onrender.com/api/health`

**API Docs:** `https://sorasocialmedia-backend.onrender.com/docs`

**Vercel Environment Variable:** `VITE_API_URL=https://sorasocialmedia-backend.onrender.com`

