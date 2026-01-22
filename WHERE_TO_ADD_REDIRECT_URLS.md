# Where to Add Redirect URLs for aigismarketing.com

## ⚠️ Important: GoDaddy is NOT where you add redirect URLs

**GoDaddy is only for:**
- Domain registration (aigismarketing.com)
- DNS management (pointing domain to Vercel/Render)

**Redirect URLs are added in each OAuth provider's developer console** (LinkedIn, Facebook, Twitter, etc.)

---

## 📍 Where to Add Each Redirect URL

### 1. LinkedIn OAuth

**Redirect URL to add:**
```
https://aigismarketing.com/api/oauth/linkedin/callback
```
(Or `https://api.aigismarketing.com/api/oauth/linkedin/callback` if backend is on subdomain)

**Where to add it:**
1. Go to: https://www.linkedin.com/developers/apps
2. Click on your app (or create a new one)
3. Click on the **"Auth"** tab (left sidebar)
4. Scroll down to **"Authorized redirect URLs for your app"**
5. Click **"+ Add redirect URL"**
6. Paste: `https://aigismarketing.com/api/oauth/linkedin/callback`
7. Click **"Update"** at the bottom

**Screenshot location:** Auth tab → Authorized redirect URLs section

---

### 2. Instagram OAuth (Facebook Graph API)

**Redirect URL to add:**
```
https://aigismarketing.com/api/oauth/instagram/callback
```
(Or `https://api.aigismarketing.com/api/oauth/instagram/callback` if backend is on subdomain)

**Where to add it:**
1. Go to: https://developers.facebook.com/apps
2. Click on your app (or create a new one)
3. Click **"Settings"** → **"Basic"** (left sidebar)
4. Scroll down to **"Valid OAuth Redirect URIs"**
5. Click **"+ Add URI"**
6. Paste: `https://aigismarketing.com/api/oauth/instagram/callback`
7. Click **"Save Changes"**

**Screenshot location:** Settings → Basic → Valid OAuth Redirect URIs

---

### 3. X (Twitter) OAuth

**Redirect URL to add:**
```
https://aigismarketing.com/api/oauth/x/callback
```
(Or `https://api.aigismarketing.com/api/oauth/x/callback` if backend is on subdomain)

**Where to add it:**
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Click on your app (or create a new one)
3. Click **"Settings"** → **"User authentication settings"**
4. Scroll to **"Callback URI / Redirect URL"**
5. Click **"+ Add"** or edit existing
6. Paste: `https://aigismarketing.com/api/oauth/x/callback`
7. Click **"Save"**

**Screenshot location:** Settings → User authentication settings → Callback URI

---

### 4. TikTok OAuth

**Redirect URL to add:**
```
https://aigismarketing.com/api/oauth/tiktok/callback
```
(Or `https://api.aigismarketing.com/api/oauth/tiktok/callback` if backend is on subdomain)

**Where to add it:**
1. Go to: https://developers.tiktok.com/apps
2. Click on your app (or create a new one)
3. Click **"Basic Information"** → **"Platform information"**
4. Find **"Redirect URL"** section
5. Click **"+ Add"** or edit existing
6. Paste: `https://aigismarketing.com/api/oauth/tiktok/callback`
7. Click **"Save"**

**Screenshot location:** Basic Information → Platform information → Redirect URL

---

### 5. Google Drive OAuth

**Redirect URL to add:**
```
https://aigismarketing.com/api/integrations/google_drive/callback
```
(Or `https://api.aigismarketing.com/api/integrations/google_drive/callback` if backend is on subdomain)

**Where to add it:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your **OAuth 2.0 Client ID** (or create a new one)
3. Scroll to **"Authorized redirect URIs"**
4. Click **"+ ADD URI"**
5. Paste: `https://aigismarketing.com/api/integrations/google_drive/callback`
6. Click **"SAVE"**

**Screenshot location:** Credentials → OAuth 2.0 Client ID → Authorized redirect URIs

---

### 6. Notion OAuth

**Redirect URL to add:**
```
https://aigismarketing.com/api/integrations/notion/callback
```
(Or `https://api.aigismarketing.com/api/integrations/notion/callback` if backend is on subdomain)

**Where to add it:**
1. Go to: https://www.notion.so/my-integrations
2. Click on your integration (or create a new one)
3. Scroll to **"Redirect URIs"** section
4. Click **"+ Add redirect URI"**
5. Paste: `https://aigismarketing.com/api/integrations/notion/callback`
6. Click **"Save changes"**

**Screenshot location:** Integration settings → Redirect URIs

---

### 7. Jira OAuth (Atlassian)

**Redirect URL to add:**
```
https://aigismarketing.com/api/integrations/jira/callback
```
(Or `https://api.aigismarketing.com/api/integrations/jira/callback` if backend is on subdomain)

**Where to add it:**
1. Go to: https://developer.atlassian.com/console/myapps/
2. Click on your app (or create a new one)
3. Click **"Authorization"** (left sidebar)
4. Find **"Callback URL"** section
5. Click **"+ Add callback URL"**
6. Paste: `https://aigismarketing.com/api/integrations/jira/callback`
7. Click **"Save changes"**

**Screenshot location:** Authorization → Callback URL

---

## 🔧 What You DO Configure in GoDaddy

GoDaddy is only used for **DNS management** (pointing your domain to Vercel/Render):

1. **Log in to GoDaddy:** https://godaddy.com
2. **Go to:** My Products → Click **"DNS"** (next to aigismarketing.com)
3. **Add DNS records** (from Vercel):
   - **A Record:** `@` → Vercel IP address
   - **CNAME Record:** `www` → `cname.vercel-dns.com`
4. **Save** and wait 15-30 minutes for DNS to propagate

**See:** `GODADDY_DEPLOYMENT_GUIDE.md` for detailed DNS setup

---

## ✅ Quick Checklist

- [ ] LinkedIn: Added redirect URL in LinkedIn Developer Portal
- [ ] Instagram: Added redirect URL in Facebook Developer Console
- [ ] X/Twitter: Added redirect URL in Twitter Developer Portal
- [ ] TikTok: Added redirect URL in TikTok Developer Portal
- [ ] Google Drive: Added redirect URL in Google Cloud Console
- [ ] Notion: Added redirect URL in Notion Integrations
- [ ] Jira: Added redirect URL in Atlassian Developer Console
- [ ] GoDaddy: Updated DNS records to point to Vercel
- [ ] Render: Set `BASE_URL` and `FRONTEND_URL` environment variables
- [ ] Tested OAuth flow for each platform

---

## 🧪 Testing

After adding redirect URLs, test each OAuth flow:

1. Go to: https://aigismarketing.com/dashboard?tab=settings
2. Click **"Connect"** for any platform
3. You should be redirected to the OAuth provider
4. After authorization, you should be redirected back to:
   ```
   https://aigismarketing.com/dashboard?tab=settings&connected={platform}
   ```

---

## 🆘 Common Issues

**"redirect_uri_mismatch" error:**
- ✅ Check the redirect URL matches EXACTLY (including `https://`)
- ✅ Make sure there are no trailing slashes
- ✅ Verify you saved the changes in the OAuth provider console
- ✅ Wait 2-3 minutes after adding before testing

**"Invalid redirect URI" error:**
- ✅ Some providers require the redirect URI to be added before it can be used
- ✅ Make sure the domain is accessible (not just localhost)
- ✅ Verify SSL certificate is valid (HTTPS required)

**OAuth not redirecting back:**
- ✅ Check `BASE_URL` environment variable in Render matches your backend URL
- ✅ Check `FRONTEND_URL` environment variable in Render matches `https://aigismarketing.com`
- ✅ Verify backend is accessible at the `BASE_URL`

---

## 📚 Need More Help?

- **LinkedIn:** https://docs.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/sign-in-with-linkedin-v2
- **Instagram/Facebook:** https://developers.facebook.com/docs/instagram-basic-display-api/guides/getting-access-tokens-and-permissions
- **Twitter/X:** https://developer.twitter.com/en/docs/authentication/oauth-2-0
- **TikTok:** https://developers.tiktok.com/doc/oauth-kit-web/
- **Google:** https://developers.google.com/identity/protocols/oauth2
- **Notion:** https://developers.notion.com/docs/authorization
- **Jira:** https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/
