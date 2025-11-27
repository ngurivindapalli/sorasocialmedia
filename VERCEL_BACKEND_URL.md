# Your Backend URL

## ✅ Backend Deployed Successfully!

Your backend is now running on Render:

**Backend URL:** `https://sorasocialmedia-1.onrender.com/`

**Health Check:** `https://sorasocialmedia-1.onrender.com/api/health`

**API Docs:** `https://sorasocialmedia-1.onrender.com/docs`

---

## 🔗 Connect Your Vercel Frontend

### Step 1: Add Environment Variable in Vercel

1. Go to your Vercel project: [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click on your frontend project
3. Go to **Settings** → **Environment Variables**
4. Click **"Add New"**
5. Add:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://sorasocialmedia-1.onrender.com`
   - ✅ Check all environments (Production, Preview, Development)
6. Click **"Save"**

### Step 2: Redeploy Frontend

1. Go to **Deployments** tab
2. Click the **three dots (⋯)** on the latest deployment
3. Click **"Redeploy"**
   - OR just push a new commit to trigger auto-deploy

### Step 3: Test the Connection

1. Visit your Vercel URL (e.g., `https://your-project.vercel.app`)
2. Open browser DevTools (F12) → Console
3. Try using the Instagram video generator
4. Check that API calls are going to your Render backend

---

## 🧪 Test Your Backend

### Health Check
```
https://sorasocialmedia-1.onrender.com/api/health
```

### API Documentation
```
https://sorasocialmedia-1.onrender.com/docs
```

### Test Endpoint
```
https://sorasocialmedia-1.onrender.com/
```

---

## 🔧 Backend Configuration

Your backend is configured with:
- ✅ OpenAI API integration
- ✅ GPT-4 Vision for video analysis
- ✅ Structured outputs for consistent prompts
- ✅ Batch API support
- ✅ Fine-tuning endpoints available

---

## 📝 Environment Variable Summary

**For Vercel Frontend:**
```
VITE_API_URL=https://sorasocialmedia-1.onrender.com
```

**For Backend (already set in Render):**
- `OPENAI_API_KEY` ✅
- Add other variables as needed in Render dashboard

---

## 🚀 You're Ready!

Your backend is live and ready to use. Just connect your Vercel frontend and you're all set!

**Next:** Update Vercel environment variable and redeploy frontend.

