# 🚀 Quick Vercel Deployment (2 Minutes)

## Fastest Method: Vercel Dashboard

### Step 1: Go to Vercel
1. Visit **[vercel.com](https://vercel.com)** and sign in
2. Click **"Add New..."** → **"Project"**

### Step 2: Import Repository
1. Find your GitHub repository (`x-video-hook-generator`)
2. Click **"Import"**

### Step 3: Configure (CRITICAL!)
1. **Root Directory:** Click "Edit" and change to **`frontend`** ⚠️
2. Framework: Vite (auto-detected)
3. Build Command: `npm run build` (auto-detected)
4. Output Directory: `dist` (auto-detected)

### Step 4: Add Environment Variable
1. Scroll to **"Environment Variables"**
2. Click **"Add New"**
3. Add:
   - **Name:** `VITE_API_URL`
   - **Value:** Your backend URL (e.g., `https://your-backend.onrender.com`)
   - ✅ Check **ALL** environments (Production, Preview, Development)
4. Click **"Save"**

### Step 5: Deploy!
1. Click **"Deploy"** at the bottom
2. Wait 1-2 minutes
3. 🎉 **Done!**

---

## Alternative: Vercel CLI (If Installed)

```bash
# Install CLI (if not installed)
npm i -g vercel

# Navigate to frontend
cd frontend

# Deploy
vercel --prod

# Follow prompts:
# - Set up and deploy? Yes
# - Link to existing project? (Choose based on your needs)
# - What's your project's name? aigis-marketing

# Add environment variable
vercel env add VITE_API_URL
# Enter your backend URL
# Select: Production, Preview, Development

# Redeploy with env var
vercel --prod
```

---

## Backend Deployment

Deploy backend separately to **Render** or **Railway**:

### Render.com (Recommended)
1. Go to [render.com](https://render.com)
2. **New +** → **Web Service**
3. Connect GitHub repo
4. Configure:
   - **Root Directory:** `backend`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
5. Add all environment variables from `backend/.env`
6. Deploy!

---

## After Deployment

1. **Frontend URL:** `https://your-project.vercel.app`
2. **Backend URL:** `https://your-backend.onrender.com`
3. **Update `VITE_API_URL`** in Vercel to point to your backend URL

---

## Quick Checklist

- [ ] Root Directory = `frontend`
- [ ] `VITE_API_URL` environment variable set
- [ ] Backend deployed (Render/Railway)
- [ ] Backend URL added to `VITE_API_URL`
- [ ] Test deployment!

