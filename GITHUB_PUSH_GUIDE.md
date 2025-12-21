# 🚀 Push to GitHub - Quick Guide

## ✅ Pre-Push Checklist

- [x] `.env` files are in `.gitignore` ✅
- [x] GCP credential JSON files are in `.gitignore` ✅
- [x] `.env.example` created with placeholders ✅
- [x] `SECRETS_SETUP.md` created with instructions ✅

---

## 📤 Push to GitHub

### Step 1: Stage All Changes

```bash
git add .
```

### Step 2: Commit

```bash
git commit -m "Add Aigis Marketing features: landing page, dashboard, marketing post generator, brand context, competitor analysis"
```

### Step 3: Push to GitHub

```bash
git push origin main
```

**Or if you need to set upstream:**

```bash
git push -u origin main
```

---

## 🔐 Setting Up Secrets After Push

### For Local Development

1. Copy `.env.example` to `.env`:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. Edit `.env` and add your actual API keys

3. For GCP credentials:
   - Download your service account JSON from Google Cloud Console
   - Save as `backend/gcp-credentials.json` (or any name)
   - Add to `.env`: `GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json`
   - **This file is already in `.gitignore`** ✅

### For Production (Render/Vercel)

See `SECRETS_SETUP.md` for detailed instructions on:
- Setting environment variables in Render (backend)
- Setting environment variables in Vercel (frontend)
- Using `GOOGLE_SERVICE_ACCOUNT_JSON` for GCP credentials

---

## ⚠️ Important Notes

1. **Never commit `.env` files** - They're in `.gitignore` ✅
2. **Never commit credential JSON files** - They're in `.gitignore` ✅
3. **Use `.env.example` as a template** - It has placeholder values
4. **For production, use environment variables** in Render/Vercel dashboards

---

## 🎯 What Gets Pushed

✅ **Will be pushed:**
- All source code
- Configuration files (package.json, requirements.txt, etc.)
- `.env.example` (with placeholders)
- Documentation files
- Static assets

❌ **Will NOT be pushed:**
- `.env` files (actual secrets)
- `*.json` credential files
- `node_modules/`
- `venv/`
- Database files
- Temporary files

---

## 🔍 Verify Before Pushing

Run this to see what will be committed:

```bash
git status
```

Make sure you don't see:
- ❌ `.env`
- ❌ `credentials.json`
- ❌ `service-account-*.json`
- ❌ `gcp-key-*.json`

---

## 📝 After Pushing

1. **Set up secrets in Render** (backend):
   - Go to Render dashboard
   - Add environment variables (see `SECRETS_SETUP.md`)

2. **Set up secrets in Vercel** (frontend):
   - Go to Vercel dashboard
   - Add `VITE_API_URL` environment variable

3. **Deploy!**
   - Render will auto-deploy on push (if connected)
   - Vercel will auto-deploy on push (if connected)

---

## 🆘 Troubleshooting

### "File is too large"
- Check if you're accidentally committing large files
- Use `git rm --cached <file>` to unstage

### "Authentication failed"
- Make sure you have GitHub credentials set up
- Use `git config --global user.name` and `git config --global user.email`

### "Remote not found"
- Add remote: `git remote add origin https://github.com/yourusername/yourrepo.git`
- Or use SSH: `git remote add origin git@github.com:yourusername/yourrepo.git`

