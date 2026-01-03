# 🚨 URGENT FIX: Redirect Loop - Step by Step

## The Problem
GoDaddy is redirecting www → non-www, AND Vercel is also redirecting, creating a loop.

## ✅ SIMPLEST FIX: Remove www Entirely (5 minutes)

### Step 1: Remove www from Vercel

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click your project
3. Go to **Settings** → **Domains**
4. Find `www.aigismarketing.com`
5. Click the **three dots (⋯)** → **Remove**
6. Confirm removal
7. **Keep only `aigismarketing.com`** (non-www)

### Step 2: Remove www from GoDaddy DNS

1. Go to [godaddy.com](https://godaddy.com) → Log in
2. Go to **My Products** → Click **DNS** (next to aigismarketing.com)
3. **Find and DELETE:**
   - Any **CNAME record** for `www`
   - Any **A record** for `www`
   - Any **Forwarding** rules for `www`
4. **Keep only:**
   - **A Record** for `@` (root) pointing to Vercel's IP
   - That's it!

### Step 3: Remove GoDaddy Forwarding (CRITICAL!)

1. In GoDaddy DNS page, scroll down
2. Look for **"Forwarding"** section
3. **DELETE ALL forwarding rules** (especially www → non-www)
4. Save changes

### Step 4: Clear Browser Cache

1. **Chrome/Edge:** Press `Ctrl + Shift + Delete`
2. Select **"Cached images and files"**
3. Time range: **"All time"**
4. Click **"Clear data"**

### Step 5: Wait 5-10 Minutes

DNS changes need time to propagate. Wait 5-10 minutes, then test:
- ✅ `https://aigismarketing.com` should work
- ❌ `https://www.aigismarketing.com` will show error (that's OK - we removed it)

---

## 🔄 ALTERNATIVE: Keep Both www and non-www (More Complex)

If you NEED www to work, follow these exact steps:

### Step 1: Remove ALL GoDaddy Forwarding Rules

1. GoDaddy → DNS → Scroll to **"Forwarding"** section
2. **DELETE EVERYTHING** in forwarding
3. Save

### Step 2: Configure Vercel Properly

1. Vercel Dashboard → Your Project → Settings → Domains
2. You should see:
   - `aigismarketing.com` (primary)
   - `www.aigismarketing.com` (should redirect to non-www)
3. If `www` shows "Invalid Configuration", remove it and add it back
4. Vercel will automatically set up www → non-www redirect

### Step 3: Fix GoDaddy DNS (Exact Records)

In GoDaddy DNS, you should have **EXACTLY** these records:

**A Record:**
- Type: `A`
- Name: `@`
- Value: `76.76.21.21` (or whatever IP Vercel shows)
- TTL: `600`

**CNAME Record:**
- Type: `CNAME`
- Name: `www`
- Value: `cname.vercel-dns.com` (or value Vercel shows)
- TTL: `600`

**NO OTHER RECORDS FOR www!**

### Step 4: Verify No Forwarding

1. GoDaddy DNS → Scroll down
2. **"Forwarding"** section should be **EMPTY**
3. If there are any forwarding rules, **DELETE THEM**

### Step 5: Wait and Test

1. Wait 15-30 minutes
2. Clear browser cache
3. Test:
   - `https://aigismarketing.com` → Should work
   - `https://www.aigismarketing.com` → Should redirect to non-www (one redirect, not a loop)

---

## 🧪 How to Test (Without Browser Cache)

Use this command to test without browser cache:

**Windows PowerShell:**
```powershell
curl -I https://www.aigismarketing.com
```

**What you should see:**
- `HTTP/1.1 301 Moved Permanently` or `HTTP/1.1 302 Found` (GOOD - one redirect)
- `Location: https://aigismarketing.com` (GOOD - redirects to non-www)

**What you DON'T want to see:**
- Multiple redirects
- `ERR_TOO_MANY_REDIRECTS`

---

## ✅ Quick Checklist

- [ ] Removed `www.aigismarketing.com` from Vercel (if using simple fix)
- [ ] Removed CNAME for `www` from GoDaddy DNS
- [ ] **DELETED ALL forwarding rules in GoDaddy** ⚠️ CRITICAL
- [ ] Only have A record for `@` in GoDaddy
- [ ] Cleared browser cache
- [ ] Waited 10-15 minutes
- [ ] Tested `https://aigismarketing.com`

---

## 🆘 Still Not Working?

1. **Check Vercel Domain Status:**
   - Vercel → Settings → Domains
   - Should show "Valid Configuration" for `aigismarketing.com`

2. **Check DNS Propagation:**
   - Visit [dnschecker.org](https://dnschecker.org)
   - Enter `aigismarketing.com`
   - Check that A record points to Vercel's IP

3. **Contact Vercel Support:**
   - They can check domain configuration on their end
   - [vercel.com/support](https://vercel.com/support)

---

## 💡 Why This Happens

**The Loop:**
1. User visits `www.aigismarketing.com`
2. GoDaddy forwarding rule redirects: `www` → `aigismarketing.com`
3. Vercel redirects: `aigismarketing.com` → `www.aigismarketing.com` (if configured)
4. Loop repeats forever → `ERR_TOO_MANY_REDIRECTS`

**The Fix:**
- Remove GoDaddy forwarding (let Vercel handle redirects)
- OR remove www entirely (simplest)

---

## 📝 TTL Explanation

**TTL = Time To Live** (not "time to load")
- How long DNS servers cache your DNS records
- `600` = 10 minutes (standard, good value)
- Lower TTL = faster DNS updates but more queries
- Higher TTL = slower DNS updates but fewer queries
- **600 is perfect** - not the problem!








