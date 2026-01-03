# Vercel Environment Variables Setup

## 🔧 Required Environment Variable for Frontend

Your frontend needs to know where your backend API is located.

### **VITE_API_URL**

**Value:** `https://sorasocialmedia-1.onrender.com`

This tells your frontend (deployed on Vercel) where to send API requests.

## 📝 How to Set in Vercel

1. **Go to Vercel Dashboard:**
   - Navigate to your project
   - Click on **Settings** → **Environment Variables**

2. **Add the Variable:**
   - Click **"Add New"**
   - **Key:** `VITE_API_URL`
   - **Value:** `https://sorasocialmedia-1.onrender.com`
   - **Environment:** Select all (Production, Preview, Development)
   - Click **"Save"**

3. **Redeploy:**
   - After adding the variable, Vercel will automatically trigger a new deployment
   - Or manually trigger a redeploy from the **Deployments** tab

## ✅ Verification

After deployment, check the browser console:
- You should see: `[API] Mode: production API_URL: https://sorasocialmedia-1.onrender.com`
- Login should work without connection errors

## 🐛 Troubleshooting

### If login still doesn't work:

1. **Check Browser Console:**
   - Open DevTools (F12)
   - Look for `[API]` logs
   - Check for CORS errors or network errors

2. **Verify Backend is Running:**
   - Visit: `https://sorasocialmedia-1.onrender.com/api/health`
   - Should return: `{"status": "ok"}`

3. **Check CORS:**
   - Backend CORS is configured to allow all origins (`"*"`)
   - If you see CORS errors, check backend logs on Render

4. **Verify Environment Variable:**
   - In Vercel, go to Settings → Environment Variables
   - Confirm `VITE_API_URL` is set correctly
   - Make sure it's enabled for the correct environment (Production/Preview)

## 📋 Quick Checklist

- [ ] `VITE_API_URL` set in Vercel to `https://sorasocialmedia-1.onrender.com`
- [ ] Environment variable enabled for all environments
- [ ] Project redeployed after adding variable
- [ ] Backend is live on Render
- [ ] Browser console shows correct API URL

## 🔗 Related Files

- `frontend/src/utils/api.js` - API configuration
- `frontend/src/utils/auth.js` - Authentication utilities
- `RENDER_ENV_VARIABLES_COMPLETE.md` - Backend environment variables


