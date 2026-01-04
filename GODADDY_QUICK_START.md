# 🚀 Quick Start: Deploy to GoDaddy (aigismarketing.com)

## TL;DR - 3 Steps

1. **Deploy Frontend to Vercel** (5 min)
2. **Deploy Backend to Render** (10 min)  
3. **Point GoDaddy Domain to Vercel** (5 min)

---

## Step 1: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → Sign in with GitHub
2. Click **"Add New Project"** → Import your GitHub repo
3. **Settings:**
   - Root Directory: `frontend`
   - Build Command: `npm run build` (auto)
   - Output Directory: `dist` (auto)
4. **Environment Variable:**
   - Name: `VITE_API_URL`
   - Value: `https://your-backend.onrender.com` (you'll update this after Step 2)
5. Click **"Deploy"**
6. **Save your Vercel URL**: `https://your-project.vercel.app`

---

## Step 2: Deploy Backend to Render

1. Go to [render.com](https://render.com) → Sign in with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. **Settings:**
   - Name: `aigis-marketing-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type: Free** ⚠️
5. **Environment Variables** (add all from your `backend/.env`):
   ```
   OPENAI_API_KEY=sk-...
   HYPERSPELL_API_KEY=...
   JWT_SECRET_KEY=...
   GOOGLE_CLOUD_PROJECT_ID=aimarketing-480803
   GOOGLE_DRIVE_CLIENT_ID=1076225983154-s584rfppe6ep9gg0b14vqhkv26p1enig.apps.googleusercontent.com
   GOOGLE_DRIVE_CLIENT_SECRET=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
   GOOGLE_DRIVE_REDIRECT_URI=https://your-backend.onrender.com/api/integrations/google_drive/callback
   FRONTEND_URL=https://aigismarketing.com
   BACKEND_URL=https://your-backend.onrender.com
   ```
   - For `GOOGLE_SERVICE_ACCOUNT_JSON`, paste entire JSON on one line
6. Click **"Create Web Service"**
7. **Save your backend URL**: `https://your-backend.onrender.com`

---

## Step 3: Connect GoDaddy Domain

### In Vercel:
1. Go to your project → **Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter: `aigismarketing.com`
4. Vercel will show you DNS records to add

### In GoDaddy:
1. Log in to [GoDaddy.com](https://godaddy.com)
2. Go to **My Products** → Click **DNS** (next to aigismarketing.com)
3. **Delete existing A and CNAME records** for `@` and `www`
4. **Add new records** (use values from Vercel):
   - **A Record:**
     - Type: `A`
     - Name: `@`
     - Value: `76.76.21.21` (use IP from Vercel)
     - TTL: `600`
   - **CNAME Record:**
     - Type: `CNAME`
     - Name: `www`
     - Value: `cname.vercel-dns.com` (use value from Vercel)
     - TTL: `600`
5. **Save** and wait 15-30 minutes for DNS to propagate

### Update Vercel Environment Variable:
1. Go back to Vercel → Your project → **Settings** → **Environment Variables**
2. Update `VITE_API_URL` to your Render backend URL
3. **Redeploy** the frontend

---

## Step 4: Update OAuth Redirect URIs

### Google Drive:
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Edit your OAuth 2.0 Client
3. Add redirect URI: `https://your-backend.onrender.com/api/integrations/google_drive/callback`
4. Save

### Update Render Environment:
1. Go to Render → Your backend service → **Environment**
2. Update `GOOGLE_DRIVE_REDIRECT_URI` to your production backend URL
3. Update `FRONTEND_URL` to `https://aigismarketing.com`
4. **Redeploy** backend

---

## ✅ Done!

Your site should be live at:
- **Frontend**: https://aigismarketing.com
- **Backend**: https://your-backend.onrender.com

---

## 🔧 Troubleshooting

**Domain not working?**
- Wait 15-30 min for DNS propagation
- Check DNS records match Vercel exactly
- Verify in Vercel dashboard that domain shows "Valid Configuration"

**Backend not responding?**
- Render free tier sleeps after 15 min - first request takes ~30 sec
- Use [UptimeRobot](https://uptimerobot.com) (free) to ping every 5 min

**CORS errors?**
- Backend already allows `aigismarketing.com` in CORS
- Make sure `FRONTEND_URL` in backend matches your domain

---

## 📚 Full Guide

See `GODADDY_DEPLOYMENT_GUIDE.md` for detailed instructions.









