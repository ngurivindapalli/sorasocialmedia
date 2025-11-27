# Manual Posting Setup (No OAuth Required)

Since Instagram and LinkedIn OAuth require company verification, here are alternative ways to post videos using your credentials directly.

## ⚠️ Important Security Note

**We do NOT recommend storing user passwords on our servers.** All solutions below either:
- Run on your local machine
- Use temporary tokens
- Use browser automation that you control

---

## Option 1: Browser Automation Scripts (Recommended)

These scripts run on your computer and use your credentials directly. Your passwords are never sent to our server.

### For Instagram

1. **Install Playwright** (browser automation):
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Download the script**: `scripts/instagram_manual_poster.py`

3. **Run the script**:
   ```bash
   python scripts/instagram_manual_poster.py --username YOUR_USERNAME --video path/to/video.mp4 --caption "Your caption"
   ```
   
   You'll be prompted for your password (it's only used locally).

### For LinkedIn

1. **Install Playwright**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Download the script**: `scripts/linkedin_manual_poster.py`

3. **Run the script**:
   ```bash
   python scripts/linkedin_manual_poster.py --username YOUR_EMAIL --video path/to/video.mp4 --caption "Your caption"
   ```

---

## Option 2: Use Instagram Manual Entry (Already Available!)

Instagram already supports manual token entry. You can get an access token without company verification:

### Step 1: Get Instagram Access Token

1. **Use Facebook Graph API Explorer**:
   - Go to https://developers.facebook.com/tools/explorer/
   - You don't need to create a full app for this
   - Select "Get Token" → "Get User Access Token"
   - Select permissions: `instagram_basic`, `instagram_content_publish`
   - Generate token

2. **Or use Instagram Basic Display API**:
   - Create a simple Facebook App (doesn't require verification for personal use)
   - Get a short-lived token
   - Exchange it for a long-lived token (60 days)

### Step 2: Add Token in VideoHook

1. Go to **Settings** → **Social Media Connections**
2. Click **"Connect Instagram"**
3. Use the **"Manual Entry"** tab
4. Enter your Instagram username and access token
5. Save

---

## Option 3: Client-Side Browser Extension (Advanced)

We can create a browser extension that runs in your browser and uses your logged-in session to post videos. This way:
- Your credentials never leave your browser
- You're already logged in (no need to re-enter password)
- Posts happen through the normal web interface

### Implementation Steps:

1. **Create Chrome Extension** that:
   - Detects when you're on Instagram/LinkedIn
   - Adds a "Post from VideoHook" button
   - Takes video URL from VideoHook
   - Uploads and posts through the web interface

2. **How it works**:
   - VideoHook generates a video and provides a URL
   - You click "Post to Instagram" in VideoHook
   - Extension opens Instagram with pre-filled video
   - You click "Share" manually (or extension does it automatically)

---

## Option 4: Get Tokens via Credentials (Helper Script)

Instead of storing passwords, we can provide a helper script that:
1. Takes your username/password
2. Logs in via browser automation
3. Extracts an access token
4. You copy the token to VideoHook

This way, passwords are only used once to get a token.

---

## Recommended Approach

**For most users, I recommend Option 2 (Manual Token Entry):**

1. **Instagram**: Get a token from Facebook Graph API Explorer (no app verification needed for personal tokens)
2. **LinkedIn**: Get a token manually via OAuth once, save it in VideoHook

**For developers/advanced users:**

- Use Option 1 (Browser Automation Scripts) for complete control
- Or Option 3 (Browser Extension) for seamless experience

---

## Why We Can't Store Passwords Server-Side

1. **Security**: Storing passwords is a major security risk
2. **Legal**: Violates most platforms' terms of service
3. **Reliability**: Instagram/LinkedIn actively block automated logins
4. **Account Safety**: Could result in account bans

---

## Getting Started

Let me know which option you prefer, and I can:
1. Create the browser automation scripts (Option 1)
2. Set up the browser extension (Option 3)
3. Create a token extraction helper (Option 4)
4. Or improve the manual token entry flow (Option 2)



