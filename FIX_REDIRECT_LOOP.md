# 🔧 Fix: ERR_TOO_MANY_REDIRECTS on www.aigismarketing.com

## Problem

You're seeing `ERR_TOO_MANY_REDIRECTS` because there's a redirect loop between `www.aigismarketing.com` and `aigismarketing.com`.

## Quick Fix (Choose One Method)

### Method 1: Fix in Vercel Dashboard (Recommended - 2 minutes)

1. **Go to Vercel Dashboard:**
   - Visit [vercel.com/dashboard](https://vercel.com/dashboard)
   - Click on your project

2. **Go to Settings → Domains:**
   - You should see both `aigismarketing.com` and `www.aigismarketing.com`

3. **Remove www version:**
   - Click the three dots (⋯) next to `www.aigismarketing.com`
   - Click **"Remove"**
   - Confirm removal

4. **Add www back with proper redirect:**
   - Click **"Add Domain"**
   - Enter: `www.aigismarketing.com`
   - Vercel will automatically redirect www → non-www
   - Wait for DNS verification

5. **Update GoDaddy DNS:**
   - Go to GoDaddy → DNS settings
   - **Remove any CNAME for www** that points to Vercel
   - **Add a new CNAME:**
     - Type: `CNAME`
     - Name: `www`
     - Value: `cname.vercel-dns.com` (or the value Vercel shows)
     - TTL: `600`

6. **Wait 15-30 minutes** for DNS to propagate

---

### Method 2: Fix in GoDaddy DNS (Alternative)

If Method 1 doesn't work, fix it in GoDaddy:

1. **Go to GoDaddy DNS Settings:**
   - Log in to [GoDaddy.com](https://godaddy.com)
   - Go to **My Products** → **DNS** (for aigismarketing.com)

2. **Check for redirect rules:**
   - Look for any **"Redirect"** or **"Forwarding"** rules
   - Delete any rules that redirect:
     - `www` → `aigismarketing.com`
     - `aigismarketing.com` → `www.aigismarketing.com`

3. **Verify DNS records:**
   - You should have:
     - **A Record** for `@` pointing to Vercel's IP
     - **CNAME Record** for `www` pointing to `cname.vercel-dns.com`
   - **DO NOT** have both pointing to different places

4. **Remove conflicting records:**
   - If you have multiple A or CNAME records for `www`, remove all except one
   - Keep only the CNAME pointing to Vercel

---

### Method 3: Use Only Non-WWW (Simplest)

If you don't need `www.aigismarketing.com`:

1. **In Vercel:**
   - Remove `www.aigismarketing.com` domain
   - Keep only `aigismarketing.com`

2. **In GoDaddy:**
   - Remove the CNAME record for `www`
   - Keep only the A record for `@`

3. **Users typing `www.aigismarketing.com` will get an error, but `aigismarketing.com` will work**

---

## Verify the Fix

After making changes:

1. **Wait 15-30 minutes** for DNS propagation
2. **Clear your browser cache** (Ctrl+Shift+Delete)
3. **Test both URLs:**
   - `https://aigismarketing.com` - Should work
   - `https://www.aigismarketing.com` - Should redirect to non-www (or work if you kept both)

4. **Check DNS propagation:**
   - Visit [dnschecker.org](https://dnschecker.org)
   - Enter `www.aigismarketing.com`
   - Check that CNAME points to Vercel

---

## Common Causes

1. **GoDaddy Forwarding Rule:**
   - GoDaddy has a "Forwarding" rule that redirects www → non-www
   - This conflicts with Vercel's redirect
   - **Solution:** Remove the forwarding rule in GoDaddy

2. **Multiple DNS Records:**
   - Both A and CNAME records for `www`
   - **Solution:** Use only CNAME for `www`, A record for `@`

3. **Vercel Auto-Redirect:**
   - Vercel automatically redirects www → non-www
   - If GoDaddy also redirects, you get a loop
   - **Solution:** Let Vercel handle redirects, remove GoDaddy redirects

---

## Still Not Working?

1. **Check Vercel Domain Status:**
   - Go to Vercel → Your project → Settings → Domains
   - Both domains should show "Valid Configuration"
   - If not, wait longer or check DNS records

2. **Test with curl (to bypass browser cache):**
   ```bash
   curl -I https://www.aigismarketing.com
   ```
   - Should show `301` or `302` redirect (not a loop)

3. **Check GoDaddy Forwarding:**
   - GoDaddy → My Products → DNS
   - Look for "Forwarding" section
   - Remove any forwarding rules

4. **Contact Support:**
   - Vercel Support: [vercel.com/support](https://vercel.com/support)
   - They can check domain configuration

---

## Recommended Setup

**Best Practice:**
- Use `aigismarketing.com` as primary domain
- Redirect `www.aigismarketing.com` → `aigismarketing.com` (handled by Vercel)
- No redirect rules in GoDaddy
- Only DNS records (A and CNAME) in GoDaddy

This prevents redirect loops and ensures proper SSL certificates.






