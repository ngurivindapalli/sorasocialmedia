# How to Get Your Backend URL

This guide shows you where to find your backend URL or how to deploy your backend if you haven't yet.

## Option 1: Backend Already Deployed

If your backend is already deployed, find your URL here:

### 🚂 Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click on your backend service/project
3. Click on the **"Settings"** tab
4. Scroll down to **"Domains"** section
5. Your backend URL will be shown (e.g., `https://your-app.railway.app`)
   - Railway automatically creates a URL like: `https://your-service-production-xxxx.up.railway.app`

**Quick Check:**
- Look for a URL in the format: `https://*.up.railway.app` or `https://*.railway.app`
- This is your backend URL!

### 🌐 Render

1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in
2. Click on your backend service (named `sorasocialmedia-backend` if using render.yaml)
3. Your URL is shown at the top in the format: `https://sorasocialmedia-backend.onrender.com`
   - Or check the **"Settings"** tab → **"Domains"** section

**Quick Check:**
- Render URLs are typically: `https://your-service-name.onrender.com`

### 🦋 Heroku

1. Go to [dashboard.heroku.com](https://dashboard.heroku.com)
2. Click on your app
3. Click **"Settings"** tab
4. Scroll to **"Domains"** section
5. Your URL is shown as: `https://your-app-name.herokuapp.com`

### ☁️ Google Cloud / AWS / Azure

1. Go to your cloud provider's console
2. Navigate to your service/app
3. Look for the **"URL"**, **"Endpoint"**, or **"Domain"** section
4. Copy the provided URL

---

## Option 2: Deploy Backend Now

If your backend isn't deployed yet, here are quick deployment options:

### 🚂 Railway (Recommended - Easiest)

**Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

**Step 2: Login**
```bash
railway login
```

**Step 3: Deploy Backend**
```bash
cd backend
railway init
railway up
```

**Step 4: Get Your URL**
```bash
railway domain
```

Or check the Railway dashboard - your URL will be shown there.

**Step 5: Set Environment Variables**
In Railway dashboard → Your service → Variables:
- `OPENAI_API_KEY` = your OpenAI key
- `GOOGLE_CLOUD_PROJECT_ID` = for Veo 3 (optional)
- Add any other required environment variables

**Your backend URL will be:** `https://your-service-production-xxxx.up.railway.app`

---

### 🌐 Render (Free Tier Available)

**Step 1: Deploy via Blueprint**
1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will automatically deploy the backend from `render.yaml`
5. Wait for deployment to complete

**Step 2: Get Your URL**
- Your backend URL will be: `https://sorasocialmedia-backend.onrender.com`
- Or check the service dashboard for the exact URL

**Step 3: Set Environment Variables**
In Render dashboard → Your backend service → Environment:
- Add `OPENAI_API_KEY`
- Add `GOOGLE_CLOUD_PROJECT_ID` (if using Veo 3)

**Your backend URL will be:** `https://sorasocialmedia-backend.onrender.com`

---

### 🔍 Testing Your Backend URL

Once you have your backend URL, test it:

1. **Health Check:**
   ```
   https://your-backend-url.com/api/health
   ```
   Should return: `{"status": "healthy"}`

2. **API Docs:**
   ```
   https://your-backend-url.com/docs
   ```
   Should show FastAPI Swagger documentation

---

## Quick Reference: Where to Find Your URL

| Platform | Where to Find | URL Format |
|----------|---------------|------------|
| **Railway** | Dashboard → Service → Settings → Domains | `https://*.up.railway.app` |
| **Render** | Dashboard → Service → Top of page | `https://*.onrender.com` |
| **Heroku** | Dashboard → App → Settings → Domains | `https://*.herokuapp.com` |
| **Vercel** | Dashboard → Project → Settings → Domains | `https://*.vercel.app` |
| **AWS** | Console → Service → Endpoint | Varies |
| **GCP** | Console → Service → URL | Varies |

---

## For Vercel Frontend Setup

Once you have your backend URL:

1. Go to your Vercel project dashboard
2. Go to **Settings** → **Environment Variables**
3. Add:
   - **Name:** `VITE_API_URL`
   - **Value:** Your backend URL (e.g., `https://your-backend.railway.app`)
4. Make sure to check all environments (Production, Preview, Development)
5. Redeploy your frontend

---

## Troubleshooting

### "Cannot connect to backend"

1. ✅ Verify backend URL is correct
2. ✅ Test backend URL directly in browser: `https://your-backend-url.com/api/health`
3. ✅ Check backend is running (green status in dashboard)
4. ✅ Verify CORS settings allow your Vercel domain

### "CORS error"

Add your Vercel frontend URL to backend CORS:
```python
origins = [
    "https://your-frontend.vercel.app",
    "https://*.vercel.app",  # For preview deployments
]
```

### "Backend URL not working"

1. Check backend logs in your hosting dashboard
2. Verify environment variables are set correctly
3. Make sure backend service is running (not sleeping)

---

## Recommended Setup

**For Testing:**
- Frontend: Vercel (free, fast)
- Backend: Railway (free tier, easy setup)

**For Production:**
- Frontend: Vercel
- Backend: Railway (paid) or Render (paid) for better reliability

---

## Need Help?

- Railway: [railway.app/docs](https://docs.railway.app)
- Render: [render.com/docs](https://render.com/docs)
- Check backend logs in your hosting platform dashboard

