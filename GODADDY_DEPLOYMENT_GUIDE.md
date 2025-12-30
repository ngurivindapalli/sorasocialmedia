# 🚀 Deploying to GoDaddy (aigismarketing.com)

This guide will help you deploy your Aigis Marketing app and connect your GoDaddy domain `aigismarketing.com`.

## ⚠️ Important: GoDaddy Hosting Limitations

GoDaddy's traditional shared hosting is **not suitable** for:
- React/Vite frontend applications
- Python FastAPI backends
- Modern Node.js applications

## ✅ Recommended Approach: Hybrid Deployment

**Best Solution**: Deploy to modern platforms, then point your GoDaddy domain to them.

### Architecture:
- **Frontend** → Deploy to **Vercel** (free, perfect for React)
- **Backend** → Deploy to **Render** or **Railway** (free tier available)
- **Domain** → Point `aigismarketing.com` from GoDaddy to Vercel

---

## 📋 Step-by-Step Deployment

### Step 1: Deploy Frontend to Vercel

1. **Push your code to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in
   - Click **"Add New Project"**
   - Import your GitHub repository
   - **Root Directory**: Set to `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - Click **"Deploy"**

3. **Add Environment Variables in Vercel**:
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     VITE_API_URL=https://your-backend.onrender.com
     ```
   - (You'll update this after deploying the backend)

4. **Get your Vercel URL**: 
   - After deployment, you'll get: `https://your-project.vercel.app`
   - Save this URL for later

---

### Step 2: Deploy Backend to Render

1. **Go to Render.com** and sign up/login

2. **Create a New Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Configure:
     - **Name**: `aigis-marketing-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `cd backend && pip install -r requirements.txt`
     - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Root Directory**: `backend`

3. **Add Environment Variables in Render**:
   - Go to Environment tab
   - Add all variables from your `backend/.env`:
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
   - For `GOOGLE_SERVICE_ACCOUNT_JSON`, paste your entire GCP JSON on one line

4. **Deploy**:
   - Click **"Create Web Service"**
   - Wait for deployment to complete
   - Get your backend URL: `https://your-backend.onrender.com`

5. **Update Frontend Environment Variable**:
   - Go back to Vercel
   - Update `VITE_API_URL` to your Render backend URL
   - Redeploy the frontend

---

### Step 3: Connect GoDaddy Domain to Vercel

1. **In Vercel Dashboard**:
   - Go to your project → **Settings** → **Domains**
   - Click **"Add Domain"**
   - Enter: `aigismarketing.com`
   - Click **"Add"**

2. **Vercel will show you DNS records**:
   - You'll see something like:
     ```
     Type: A
     Name: @
     Value: 76.76.21.21
     
     Type: CNAME
     Name: www
     Value: cname.vercel-dns.com
     ```

3. **In GoDaddy DNS Settings**:
   - Log in to [GoDaddy.com](https://godaddy.com)
   - Go to **My Products** → **DNS** (for aigismarketing.com)
   - **Delete existing A records** for `@` and `www`
   - **Add new records**:
     - **Type**: `A`
     - **Name**: `@`
     - **Value**: `76.76.21.21` (use the IP from Vercel)
     - **TTL**: `600`
     
     - **Type**: `CNAME`
     - **Name**: `www`
     - **Value**: `cname.vercel-dns.com` (use the value from Vercel)
     - **TTL**: `600`

4. **Wait for DNS Propagation**:
   - DNS changes can take 5 minutes to 48 hours
   - Usually takes 15-30 minutes
   - Check status: https://dnschecker.org

5. **Verify in Vercel**:
   - Once DNS propagates, Vercel will show "Valid Configuration"
   - Your site will be live at `https://aigismarketing.com`

---

### Step 4: Update OAuth Redirect URIs

After deployment, update your OAuth redirect URIs:

1. **Google Drive** (Google Cloud Console):
   - Go to https://console.cloud.google.com/apis/credentials
   - Edit your OAuth 2.0 Client
   - Add redirect URI: `https://your-backend.onrender.com/api/integrations/google_drive/callback`
   - Save

2. **Update Render Environment Variables**:
   - Update `GOOGLE_DRIVE_REDIRECT_URI` to your production backend URL
   - Update `FRONTEND_URL` to `https://aigismarketing.com`
   - Redeploy backend

---

## 🔄 Alternative: Backend Subdomain

If you want to use a subdomain for the backend:

1. **Create subdomain in GoDaddy**:
   - Add DNS record:
     - **Type**: `CNAME`
     - **Name**: `api`
     - **Value**: `your-backend.onrender.com`
     - **TTL**: `600`

2. **Update Render**:
   - In Render, add custom domain: `api.aigismarketing.com`
   - Follow Render's instructions to verify

3. **Update Frontend**:
   - Set `VITE_API_URL=https://api.aigismarketing.com`

---

## 📝 Quick Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Render
- [ ] Environment variables added to both platforms
- [ ] GoDaddy DNS records updated
- [ ] OAuth redirect URIs updated
- [ ] Domain verified in Vercel
- [ ] Site accessible at https://aigismarketing.com

---

## 🆘 Troubleshooting

### "Domain not resolving"
- Wait 15-30 minutes for DNS propagation
- Check DNS records match Vercel's requirements exactly
- Use https://dnschecker.org to verify DNS propagation

### "Backend not accessible"
- Check Render service is running (not sleeping)
- Verify environment variables are set correctly
- Check Render logs for errors

### "OAuth not working"
- Verify redirect URIs match exactly (including https://)
- Check environment variables in Render
- Ensure backend URL is accessible

### "CORS errors"
- Verify `FRONTEND_URL` in backend matches your domain
- Check backend CORS middleware includes your domain

---

## 💰 Cost Estimate

- **Vercel**: Free (Hobby plan) - Perfect for frontend
- **Render**: Free tier available (sleeps after 15 min inactivity)
  - Or $7/month for always-on service
- **GoDaddy**: Domain only (you already own it)
- **Total**: $0-7/month

---

## 🎯 Next Steps After Deployment

1. Test the site at https://aigismarketing.com
2. Test user signup/login
3. Test document upload
4. Test Google Drive integration
5. Test marketing post generation
6. Monitor Render logs for any errors

---

## 📚 Additional Resources

- [Vercel Domain Documentation](https://vercel.com/docs/concepts/projects/domains)
- [Render Documentation](https://render.com/docs)
- [GoDaddy DNS Help](https://www.godaddy.com/help/manage-dns-records-680)






