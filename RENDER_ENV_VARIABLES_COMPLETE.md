# 🔧 Complete Render Environment Variables Setup

## 📋 Required Environment Variables for Backend (Render)

### Core API Keys (REQUIRED)

```
OPENAI_API_KEY
sk-proj-your-openai-api-key-here
```
**Required for:** SEO/AEO Tracker, Aigis Marketing, Video Generation, Content Creation

```
ANTHROPIC_API_KEY
sk-ant-your-anthropic-key-here
```
**Optional but recommended** for Claude features

---

### Authentication (REQUIRED)

```
JWT_SECRET_KEY
your-random-secret-key-minimum-32-characters-long
```
**Generate with:** `openssl rand -hex 32` or any random string generator (32+ chars)

---

### Google Cloud Platform / Veo 3 / Image Generation (REQUIRED)

```
GOOGLE_CLOUD_PROJECT_ID
your-gcp-project-id
```
**Example:** `aimarketing-480803` or `igvideogen`

```
GOOGLE_SERVICE_ACCOUNT_JSON
{"type":"service_account","project_id":"your-project","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```
**Important:** Paste the ENTIRE JSON on ONE line (no line breaks). Get this from Google Cloud Console → IAM & Admin → Service Accounts → Create Key → JSON

```
GOOGLE_CLOUD_LOCATION
us-central1
```
**Optional:** Defaults to `us-central1` if not set

---

### Memory Service / Hyperspell (REQUIRED)

```
HYPERSPELL_API_KEY
your-hyperspell-api-key-here
```
**Required for:** User context, memory storage, brand context

```
HYPERSPELL_USER_ID
your-hyperspell-user-id
```
**Optional:** If you have a specific user ID

---

### AWS S3 (Optional - for Memory Service)

```
AWS_ACCESS_KEY_ID
your-aws-access-key-id
```
**Only needed if using S3 for memory storage**

```
AWS_SECRET_ACCESS_KEY
your-aws-secret-access-key
```
**Only needed if using S3 for memory storage**

```
AWS_S3_BUCKET
your-s3-bucket-name
```
**Only needed if using S3 for memory storage**

```
AWS_REGION
us-east-1
```
**Only needed if using S3 for memory storage**

---

### Database (Optional - defaults to SQLite)

```
DATABASE_URL
postgresql://user:password@host:port/dbname
```
**Optional:** If you want to use PostgreSQL instead of SQLite. If not set, uses SQLite file.

---

### Frontend URL (REQUIRED for CORS)

```
FRONTEND_URL
https://your-frontend-domain.com
```
**Set to your Vercel/frontend URL** (e.g., `https://your-app.vercel.app`)

```
BACKEND_URL
https://your-backend.onrender.com
```
**Set to your Render backend URL** (e.g., `https://your-backend.onrender.com`)

---

### Integrations (Optional)

#### Notion Integration
```
NOTION_SECRET
your-notion-integration-token
```
**OR use OAuth:**
```
NOTION_CLIENT_ID
your-notion-oauth-client-id

NOTION_CLIENT_SECRET
your-notion-oauth-client-secret

NOTION_REDIRECT_URI
https://your-backend.onrender.com/api/integrations/notion/callback
```

#### Google Drive Integration
```
GOOGLE_DRIVE_CLIENT_ID
your-google-drive-client-id

GOOGLE_DRIVE_CLIENT_SECRET
your-google-drive-client-secret

GOOGLE_DRIVE_REDIRECT_URI
https://your-backend.onrender.com/api/integrations/google_drive/callback
```

#### LinkedIn OAuth
```
LINKEDIN_CLIENT_ID
your-linkedin-client-id

LINKEDIN_CLIENT_SECRET
your-linkedin-client-secret

LINKEDIN_REDIRECT_URI
https://your-backend.onrender.com/api/auth/linkedin/callback
```

#### Jira Integration
```
JIRA_SERVER_URL
https://your-domain.atlassian.net

JIRA_EMAIL
your-email@example.com

JIRA_API_TOKEN
your-jira-api-token
```

---

### Social Media APIs (Optional)

```
X_BEARER_TOKEN
your-x-twitter-bearer-token
```
**For X/Twitter API integration**

```
INSTAGRAM_USERNAME
your-instagram-username
```
**Optional:** For Instagram scraping

```
INSTAGRAM_PASSWORD
your-instagram-password
```
**Optional:** For Instagram scraping (not recommended - use OAuth instead)

---

### Email/SMTP (Optional)

```
SMTP_HOST
smtp.gmail.com

SMTP_PORT
587

SMTP_USER
your-email@gmail.com

SMTP_PASSWORD
your-app-password
```

---

### Advanced Options (Optional)

```
OPENAI_FINE_TUNED_MODEL
ft:gpt-4-0125:your-org:model-name:abc123
```
**If using a fine-tuned OpenAI model**

```
SORA_MODEL
sora-2
```
**Default Sora model preference**

```
SORA_MODEL_PRO
sora-2-pro
```
**Pro Sora model for high-quality videos**

```
VEO3_MODEL_ID
veo-3
```
**Veo 3 model ID**

```
VEO3_API_KEY
your-veo3-api-key
```
**If using API key auth for Veo 3 (instead of service account)**

---

## 🚀 Quick Setup Checklist for Render

### Step 1: Go to Render Dashboard
1. Navigate to your Backend Service
2. Click on **Environment** tab
3. Click **"Add Environment Variable"** for each variable below

### Step 2: Add Required Variables (Copy-Paste These)

**1. OpenAI API Key:**
- Key: `OPENAI_API_KEY`
- Value: `sk-proj-your-actual-key`

**2. JWT Secret:**
- Key: `JWT_SECRET_KEY`
- Value: Generate with `openssl rand -hex 32` or use a random 32+ character string

**3. Google Cloud Project ID:**
- Key: `GOOGLE_CLOUD_PROJECT_ID`
- Value: `your-project-id` (e.g., `aimarketing-480803`)

**4. Google Service Account JSON:**
- Key: `GOOGLE_SERVICE_ACCOUNT_JSON`
- Value: Paste your ENTIRE service account JSON (all on one line, no breaks)

**5. Hyperspell API Key:**
- Key: `HYPERSPELL_API_KEY`
- Value: `your-hyperspell-key`

**6. Frontend URL:**
- Key: `FRONTEND_URL`
- Value: `https://your-frontend.vercel.app` (your actual frontend URL)

**7. Backend URL:**
- Key: `BACKEND_URL`
- Value: `https://your-backend.onrender.com` (your actual Render backend URL)

### Step 3: Add Optional Variables (As Needed)

- `ANTHROPIC_API_KEY` - If using Claude
- `DATABASE_URL` - If using PostgreSQL
- `AWS_*` variables - If using S3 for memory
- Integration keys (Notion, Google Drive, LinkedIn, Jira)
- Social media API keys

### Step 4: Save and Deploy

1. Click **"Save Changes"**
2. Render will automatically rebuild and deploy
3. Check logs to verify everything starts correctly

---

## ✅ Verification

After deployment, check your Render logs. You should see:

```
[API] Using OpenAI API key: sk-proj-...
[API] SEO/AEO service initialized
[API] User context service initialized with Memory (S3 + Mem0)
[API] Starting server on port 8000
```

If you see errors about missing variables, add them to the Environment tab.

---

## 🔒 Security Notes

1. **Never commit `.env` files** - They're in `.gitignore` ✅
2. **All secrets are stored in Render's Environment Variables** - Not in code
3. **Service Account JSON** must be on ONE line when pasting
4. **JWT_SECRET_KEY** should be a strong random string (32+ characters)
5. **Rotate keys regularly** for security

---

## 📝 New Features Requiring Environment Variables

### SEO/AEO Tracker
- Requires: `OPENAI_API_KEY`
- Uses: OpenAI API for ChatGPT testing and prompt generation

### Step-by-Step Aigis Marketing
- Requires: `OPENAI_API_KEY`
- Optional: `ANTHROPIC_API_KEY` for Claude features
- Uses: OpenAI for content generation at each step

---

## 🆘 Troubleshooting

**Error: "OpenAI API key required"**
→ Add `OPENAI_API_KEY` to Render environment variables

**Error: "GOOGLE_CLOUD_PROJECT_ID not set"**
→ Add `GOOGLE_CLOUD_PROJECT_ID` with your GCP project ID

**Error: "Service account key file not found"**
→ Add `GOOGLE_SERVICE_ACCOUNT_JSON` with full JSON content (one line)

**Error: "HYPERSPELL_API_KEY not set"**
→ Add `HYPERSPELL_API_KEY` to environment variables

**CORS errors in frontend**
→ Make sure `FRONTEND_URL` is set to your actual frontend domain

**401 Unauthorized errors**
→ Check that all API keys are correct and not expired

---

## 📚 Additional Resources

- See `ENV_VARIABLES_COPY_PASTE.md` for more examples
- See `RENDER_ENV_SETUP.md` for detailed setup instructions
- Check Render logs for specific error messages

