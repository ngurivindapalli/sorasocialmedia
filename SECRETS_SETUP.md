# 🔐 Secrets Management Guide

This guide explains how to securely manage API keys and credentials for this project.

## ⚠️ Important Security Notes

- **NEVER commit `.env` files or credential JSON files to GitHub**
- All secrets are stored as environment variables
- Use different methods for local development vs. production deployment

---

## 📋 Required Secrets

### Backend Secrets

1. **OpenAI API Key** - `OPENAI_API_KEY`
2. **Google Cloud Platform (GCP) Service Account** - `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_SERVICE_ACCOUNT_JSON`
3. **Hyperspell API Key** - `HYPERSPELL_API_KEY`
4. **JWT Secret** - `JWT_SECRET_KEY`
5. **Database URL** - `DATABASE_URL` (optional, defaults to SQLite)

### Frontend Secrets

1. **Backend API URL** - `VITE_API_URL` (e.g., `https://your-backend.onrender.com`)

---

## 🏠 Local Development Setup

### Step 1: Create `.env` file

```bash
cd backend
cp .env.example .env
```

### Step 2: Fill in your secrets

Edit `backend/.env` and add your actual API keys:

```env
OPENAI_API_KEY=sk-...
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
HYPERSPELL_API_KEY=your_hyperspell_key
JWT_SECRET_KEY=your_random_secret_key
```

### Step 3: GCP Service Account Setup

**Option A: Use JSON file (Local Development)**

1. Download your GCP service account JSON key from Google Cloud Console
2. Save it as `backend/gcp-credentials.json` (or any name)
3. Add to `.env`:
   ```env
   GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
   ```
4. **Make sure `gcp-credentials.json` is in `.gitignore`** ✅ (already done)

**Option B: Use JSON content directly (For Deployment)**

1. Open your service account JSON file
2. Copy the entire JSON content
3. Add to `.env`:
   ```env
   GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key":"..."}
   ```
   (Use single line, no line breaks)

---

## ☁️ Production Deployment (Render/Vercel)

### Render.com (Backend)

1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. Add each secret as an environment variable:

   | Variable Name | Value | Notes |
   |--------------|-------|-------|
   | `OPENAI_API_KEY` | `sk-...` | Your OpenAI API key |
   | `GOOGLE_SERVICE_ACCOUNT_JSON` | `{"type":"service_account",...}` | Full JSON content (single line) |
   | `HYPERSPELL_API_KEY` | `...` | Your Hyperspell API key |
   | `JWT_SECRET_KEY` | `...` | Random secret string |
   | `DATABASE_URL` | `postgresql://...` | (If using PostgreSQL) |

4. **For GCP JSON:**
   - Open your service account JSON file
   - Copy the entire JSON (all on one line)
   - Paste into `GOOGLE_SERVICE_ACCOUNT_JSON` in Render
   - **Do NOT use line breaks**

### Vercel (Frontend)

1. Go to your Vercel project dashboard
2. Navigate to **Settings** → **Environment Variables**
3. Add:

   | Variable Name | Value |
   |--------------|-------|
   | `VITE_API_URL` | `https://your-backend.onrender.com` |

4. ✅ Check all environments (Production, Preview, Development)
5. Redeploy after adding variables

---

## 🔑 Getting Your GCP Service Account Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click on your service account (or create one)
5. Go to **Keys** tab
6. Click **Add Key** → **Create new key**
7. Choose **JSON** format
8. Download the file
9. **Keep this file secure!** Never commit it to git.

---

## ✅ Verification

### Test Local Setup

```bash
cd backend
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OpenAI:', '✓' if os.getenv('OPENAI_API_KEY') else '✗'); print('GCP:', '✓' if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON') else '✗')"
```

### Test Production

- Backend: Visit `https://your-backend.onrender.com/api/health`
- Frontend: Check browser console for API connection errors

---

## 🚨 Security Checklist

- [ ] `.env` is in `.gitignore` ✅
- [ ] `*.json` credential files are in `.gitignore` ✅
- [ ] `.env.example` exists with placeholder values ✅
- [ ] No secrets committed to git
- [ ] Production secrets are set in Render/Vercel dashboards
- [ ] GCP service account has minimal required permissions
- [ ] JWT secret is strong and random

---

## 📝 Notes

- The code supports both `GOOGLE_APPLICATION_CREDENTIALS` (file path) and `GOOGLE_SERVICE_ACCOUNT_JSON` (JSON content)
- For local development, use file path
- For Render/Vercel, use JSON content (easier to manage)
- All environment variables are loaded from `.env` in development
- Production uses environment variables set in deployment platform

---

## 🆘 Troubleshooting

### "Service account key file not found"
- Check `GOOGLE_APPLICATION_CREDENTIALS` path is correct
- Or use `GOOGLE_SERVICE_ACCOUNT_JSON` with full JSON content

### "Invalid JSON" error
- Make sure JSON is on a single line (no line breaks)
- Validate JSON at [jsonlint.com](https://jsonlint.com/)

### "Authentication failed"
- Verify service account has correct permissions
- Check that the JSON key hasn't expired
- Ensure `google-auth` is installed: `pip install google-auth`

