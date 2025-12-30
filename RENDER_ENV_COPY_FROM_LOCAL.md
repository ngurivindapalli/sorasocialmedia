# 📋 Copy Environment Variables from Local .env to Render

## 📍 Your .env File Location

```
C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\.env
```

## ✅ Required Variables to Copy to Render

Copy these from your `.env` file to Render Dashboard → Environment Variables:

### 1. Core API Keys (REQUIRED)

**OPENAI_API_KEY**
- Copy the full value from your `.env`
- Required for: SEO/AEO Tracker, Aigis Marketing, all AI features

**ANTHROPIC_API_KEY**
- Copy the full value from your `.env`
- Optional but recommended for Claude features

**HYPERSPELL_API_KEY**
- Copy the full value from your `.env`
- Required for: Memory service, user context, brand context

### 2. Google Cloud Platform (REQUIRED)

**GOOGLE_CLOUD_PROJECT_ID**
- Value: `aimarketing-480803`
- Copy this exact value

**GOOGLE_SERVICE_ACCOUNT_JSON**
- ⚠️ **IMPORTANT:** This might be in `GOOGLE_APPLICATION_CREDENTIALS` as a file path
- If you have a service account JSON file, open it and copy the ENTIRE JSON content
- Paste it as ONE line (no line breaks) in Render
- If you don't have this, you need to create a service account in Google Cloud Console

**GOOGLE_CLOUD_LOCATION**
- Value: `us-central1`
- Optional: Defaults to this if not set

### 3. Authentication (REQUIRED)

**JWT_SECRET_KEY**
- ⚠️ **Check if this exists in your .env**
- If not, generate one: `openssl rand -hex 32` or use a random 32+ character string
- Required for user authentication

### 4. URLs (REQUIRED)

**FRONTEND_URL**
- Set to: `https://your-frontend-domain.vercel.app` (your actual Vercel URL)
- Required for CORS

**BACKEND_URL**
- Set to: `https://your-backend.onrender.com` (your actual Render URL)
- Required for API calls

### 5. AWS S3 (Optional - if using S3 for memory)

**AWS_ACCESS_KEY_ID**
- Copy from your `.env`

**AWS_SECRET_ACCESS_KEY**
- Copy from your `.env`

**AWS_S3_BUCKET**
- Value: `x-video-hook-mem0-20251228193510`
- Copy from your `.env`

**AWS_REGION**
- Value: `us-east-1`
- Copy from your `.env`

### 6. Integrations (Optional)

**NOTION_SECRET**
- Copy from your `.env`
- For Notion integration

**PERPLEXITY_API_KEY**
- Copy from your `.env`
- For web search features

**GEMINI_API_KEY**
- Copy from your `.env`
- For Gemini AI features

## 🚨 Important Notes

### GOOGLE_SERVICE_ACCOUNT_JSON

Your `.env` has `GOOGLE_APPLICATION_CREDENTIALS` pointing to a file path. For Render, you need:

1. **Find your service account JSON file** (the path in `GOOGLE_APPLICATION_CREDENTIALS`)
2. **Open that JSON file**
3. **Copy the ENTIRE contents** (all on one line)
4. **Paste into Render** as `GOOGLE_SERVICE_ACCOUNT_JSON`

Example format:
```json
{"type":"service_account","project_id":"aimarketing-480803","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

### DO NOT Copy These to Render

- `INSTAGRAM_PASSWORD` - Not needed on Render (use OAuth)
- `GOOGLE_APPLICATION_CREDENTIALS` - This is a file path, not the JSON content
- Any local file paths

## 📝 Step-by-Step: Copying to Render

1. **Open your `.env` file:**
   ```
   C:\Users\Noel\Downloads\claudehookproject\x-video-hook-generator\backend\.env
   ```

2. **Go to Render Dashboard:**
   - Navigate to your Backend Service
   - Click **Environment** tab
   - Click **"Add Environment Variable"**

3. **For each variable above:**
   - Copy the **Key** name
   - Copy the **Value** from your `.env`
   - Paste into Render
   - Click **"Add"**

4. **Special handling for GOOGLE_SERVICE_ACCOUNT_JSON:**
   - Find the JSON file path from `GOOGLE_APPLICATION_CREDENTIALS`
   - Open that file
   - Copy entire JSON content
   - Paste as ONE line in Render

5. **Save and Deploy:**
   - Click **"Save Changes"**
   - Render will automatically rebuild

## ✅ Quick Checklist

- [ ] OPENAI_API_KEY
- [ ] ANTHROPIC_API_KEY (optional)
- [ ] HYPERSPELL_API_KEY
- [ ] GOOGLE_CLOUD_PROJECT_ID (`aimarketing-480803`)
- [ ] GOOGLE_SERVICE_ACCOUNT_JSON (from JSON file)
- [ ] JWT_SECRET_KEY (generate if missing)
- [ ] FRONTEND_URL (your Vercel URL)
- [ ] BACKEND_URL (your Render URL)
- [ ] AWS_* variables (if using S3)
- [ ] NOTION_SECRET (optional)
- [ ] PERPLEXITY_API_KEY (optional)
- [ ] GEMINI_API_KEY (optional)

## 🔍 Finding Your Service Account JSON

If `GOOGLE_APPLICATION_CREDENTIALS` points to a file, find it:

1. Check the path in your `.env`: `GOOGLE_APPLICATION_CREDENTIALS=...`
2. Navigate to that file location
3. Open the `.json` file
4. Copy all contents
5. Paste into Render as `GOOGLE_SERVICE_ACCOUNT_JSON`

If you don't have the file, create a new service account:
1. Go to Google Cloud Console
2. IAM & Admin → Service Accounts
3. Create Service Account → Create Key → JSON
4. Download and use that JSON

