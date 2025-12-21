# 📋 Environment Variables - Copy & Paste

## 🎯 Quick Copy-Paste for Local Development (.env file)

Copy this into your `backend/.env` file:

```env
# ============================================
# REQUIRED - Core API Keys
# ============================================
OPENAI_API_KEY=sk-your-openai-api-key-here
HYPERSPELL_API_KEY=your-hyperspell-api-key-here

# ============================================
# REQUIRED - Google Cloud Platform (GCP)
# Choose ONE method below:
# ============================================

# Method 1: JSON file path (Local development)
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json

# Method 2: Full JSON content (For Render/Vercel - paste entire JSON on one line)
# GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}

# ============================================
# REQUIRED - Authentication
# ============================================
JWT_SECRET_KEY=your-random-secret-key-change-this-in-production-min-32-chars

# ============================================
# OPTIONAL - Database (defaults to SQLite)
# ============================================
# DATABASE_URL=sqlite:///./videohook.db
# Or for PostgreSQL: DATABASE_URL=postgresql://user:password@host:port/dbname

# ============================================
# OPTIONAL - Anthropic (Claude)
# ============================================
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# ============================================
# REQUIRED - GCP Project Settings
# ============================================
GOOGLE_CLOUD_PROJECT_ID=aimarketing-480803
# VEO3_PROJECT_ID=aimarketing-480803  # Alternative to above
# VEO3_LOCATION=us-central1
# VEO3_API_KEY=your-veo3-api-key-if-using-api-key-auth
# IMAGEN_MODEL_ID=imagen-4.0-generate-001
# VEO3_MODEL_ID=veo-3

# ============================================
# OPTIONAL - OpenAI Fine-Tuned Model
# ============================================
# OPENAI_FINE_TUNED_MODEL=ft:gpt-4-0125:your-org:model-name:abc123

# ============================================
# OPTIONAL - Instagram Scraping
# ============================================
# INSTAGRAM_USERNAME=your-instagram-username
# INSTAGRAM_PASSWORD=your-instagram-password

# ============================================
# OPTIONAL - LinkedIn OAuth
# ============================================
# LINKEDIN_CLIENT_ID=your-linkedin-client-id
# LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
# LINKEDIN_REDIRECT_URI=http://localhost:3001/auth/linkedin/callback

# ============================================
# OPTIONAL - Email (SMTP)
# ============================================
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# ============================================
# OPTIONAL - X (Twitter) API
# ============================================
# X_BEARER_TOKEN=your-x-bearer-token

# ============================================
# OPTIONAL - Stable Diffusion (Alternative to Imagen)
# ============================================
# STABLE_DIFFUSION_API_KEY=your-stable-diffusion-key
# STABLE_DIFFUSION_URL=https://api.stability.ai

# ============================================
# OPTIONAL - Frontend URL (for CORS)
# ============================================
# FRONTEND_URL=http://localhost:3001
```

---

## ☁️ For Render.com (Backend) - Copy Each Line

When adding environment variables in Render dashboard, copy each variable name and value separately:

### Required Variables:

```
OPENAI_API_KEY
sk-your-openai-api-key-here
```

```
HYPERSPELL_API_KEY
your-hyperspell-api-key-here
```

```
GOOGLE_SERVICE_ACCOUNT_JSON
{"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```
*(Paste your entire GCP service account JSON on ONE line, no line breaks)*

```
JWT_SECRET_KEY
your-random-secret-key-change-this-in-production-min-32-chars
```

### Optional Variables:

```
ANTHROPIC_API_KEY
sk-ant-your-anthropic-key-here
```

```
GOOGLE_CLOUD_PROJECT_ID
your-gcp-project-id
```

```
VEO3_LOCATION
us-central1
```

```
DATABASE_URL
postgresql://user:password@host:port/dbname
```

---

## 🎨 For Vercel (Frontend) - Copy Each Line

When adding environment variables in Vercel dashboard:

### Required Variable:

```
VITE_API_URL
https://your-backend.onrender.com
```
*(Replace with your actual Render backend URL)*

**Important:** Check all environments (Production, Preview, Development) when adding!

---

## 🔑 How to Get Your Keys

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)

### Hyperspell API Key
1. Go to your Hyperspell dashboard
2. Navigate to API Keys section
3. Copy your API key

### GCP Service Account JSON
1. Go to https://console.cloud.google.com/
2. Select your project
3. Navigate to **IAM & Admin** → **Service Accounts**
4. Click on your service account (or create one)
5. Go to **Keys** tab → **Add Key** → **Create new key**
6. Choose **JSON** format
7. Download the file
8. Open the file and copy the entire JSON content (all on one line)

### JWT Secret Key
Generate a random string (minimum 32 characters):
- Use: `openssl rand -hex 32` (Linux/Mac)
- Or use: https://randomkeygen.com/
- Or any random string generator

---

## ✅ Quick Checklist

**For Local Development:**
- [ ] Copy the `.env` template above
- [ ] Fill in `OPENAI_API_KEY`
- [ ] Fill in `HYPERSPELL_API_KEY`
- [ ] Add GCP credentials (file path or JSON)
- [ ] Generate and add `JWT_SECRET_KEY`
- [ ] Save as `backend/.env`

**For Render (Backend):**
- [ ] Add `OPENAI_API_KEY`
- [ ] Add `HYPERSPELL_API_KEY`
- [ ] Add `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON on one line)
- [ ] Add `JWT_SECRET_KEY`
- [ ] Add `DATABASE_URL` (if using PostgreSQL)

**For Vercel (Frontend):**
- [ ] Add `VITE_API_URL` (your Render backend URL)
- [ ] Check all environments (Production, Preview, Development)

---

## 🚨 Important Notes

1. **Never commit `.env` files to git** ✅ (already in `.gitignore`)
2. **GCP JSON must be on ONE line** when using `GOOGLE_SERVICE_ACCOUNT_JSON`
3. **JWT_SECRET_KEY** should be a strong random string (32+ characters)
4. **VITE_API_URL** must start with `https://` for production
5. All environment variables are case-sensitive

---

## 📝 Example Values (DO NOT USE IN PRODUCTION)

```env
OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
HYPERSPELL_API_KEY=hyp_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
JWT_SECRET_KEY=my-super-secret-jwt-key-change-this-in-production-12345
VITE_API_URL=https://sorasocialmedia-1.onrender.com
```

*(These are examples - use your actual keys!)*

