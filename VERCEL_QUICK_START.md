# Vercel Quick Start - Get Your App Running NOW!

Your backend is already live at: `https://sorasocialmedia-1.onrender.com/`

Now let's deploy your frontend to Vercel and connect it to your backend.

---

## 🚀 Step-by-Step: Deploy to Vercel (5 Minutes)

### Step 1: Go to Vercel

1. Go to **[vercel.com](https://vercel.com)**
2. Click **"Sign Up"** (or "Log In" if you have an account)
3. Sign up with your **GitHub account** (easiest way)

### Step 2: Import Your Project

1. After logging in, click **"Add New..."** → **"Project"**
2. You'll see a list of your GitHub repositories
3. Find and click on **`sorasocialmedia`** (or your repo name)
4. Click **"Import"**

### Step 3: Configure Project Settings

Vercel will try to auto-detect your settings. **IMPORTANT:** You need to change one thing:

1. Look for **"Root Directory"** field
2. Click **"Edit"** next to it
3. Change from `./` to **`frontend`** ⚠️ **This is critical!**
4. Vercel will auto-detect:
   - ✅ Framework: Vite
   - ✅ Build Command: `npm run build`
   - ✅ Output Directory: `dist`

### Step 4: Add Environment Variable (CRITICAL!)

This connects your frontend to your backend:

1. Scroll down to **"Environment Variables"** section
2. Click **"Add New"**
3. Add this variable:
   - **Name:** `VITE_API_URL`
   - **Value:** `https://sorasocialmedia-1.onrender.com`
   - ✅ Check **ALL** environments:
     - ✅ Production
     - ✅ Preview
     - ✅ Development
4. Click **"Save"**

### Step 5: Deploy!

1. Scroll to the bottom
2. Click **"Deploy"**
3. Wait 1-2 minutes for the build
4. 🎉 **Your app will be live!**

---

## ✅ After Deployment

### Your App URLs:

- **Production:** `https://your-project-name.vercel.app`
- **Preview:** Automatically created for each push

### Test Your App:

1. Visit your Vercel URL
2. You should land on the **Instagram Tools** page
3. Try creating an informational video:
   - Enter an Instagram username
   - Set video duration (e.g., 8 seconds)
   - Click "Create Informational Video"
4. Check browser console (F12) for any errors

---

## 🔧 Troubleshooting

### Build Fails

- ✅ Check **Root Directory** is set to `frontend`
- ✅ Check build logs in Vercel dashboard
- ✅ Verify all dependencies are in `frontend/package.json`

### API Calls Fail (404/500)

1. ✅ Verify `VITE_API_URL` environment variable is set correctly
2. ✅ Check it's set to: `https://sorasocialmedia-1.onrender.com` (no trailing slash)
3. ✅ Make sure you checked all environments (Production, Preview, Development)
4. ✅ Test backend directly: Visit `https://sorasocialmedia-1.onrender.com/api/health`
5. ✅ Redeploy frontend after adding environment variable

### CORS Errors

Your backend already allows Vercel domains. If you see CORS errors:
1. Check backend is running: `https://sorasocialmedia-1.onrender.com/api/health`
2. Verify backend CORS includes `https://*.vercel.app`

---

## 📋 Quick Checklist

Before deploying:
- ✅ Root Directory = `frontend`
- ✅ `VITE_API_URL` = `https://sorasocialmedia-1.onrender.com`
- ✅ Environment variable checked for all environments

After deploying:
- ✅ Visit your Vercel URL
- ✅ Test Instagram video generation
- ✅ Check browser console for errors

---

## 🔄 Updating Later

After initial setup, to update your app:
1. Just push to GitHub: `git push origin main`
2. Vercel automatically redeploys!
3. No need to manually redeploy (unless you change environment variables)

---

## 📞 Need Help?

- Check build logs in Vercel dashboard
- Check backend logs in Render dashboard
- Test backend health: `https://sorasocialmedia-1.onrender.com/api/health`
- Test backend API docs: `https://sorasocialmedia-1.onrender.com/docs`

---

## 🎯 Summary

**What you need:**
1. Vercel account (free)
2. Root Directory = `frontend`
3. Environment Variable: `VITE_API_URL = https://sorasocialmedia-1.onrender.com`
4. Click Deploy!

**That's it!** Your app will be live and ready for users to test! 🚀

