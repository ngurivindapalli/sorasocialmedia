# Google OAuth App Verification Guide

## 🎯 Goal

Verify your Google OAuth app so it can be used by all users (not just test users) for Google Drive integration.

## 📋 Current Status

Your app is likely in **"Testing"** mode, which means:
- ✅ Only test users can access it
- ❌ Other users will see "Access blocked: app is in testing mode"
- ✅ This works for development, but limits production use

## 🚀 Step-by-Step: Verify Your App

### Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com/
2. Select your project: **aimarketing-480803** (or your project)
3. Navigate to: **APIs & Services** → **OAuth consent screen**

### Step 2: Review Your OAuth Consent Screen

Make sure everything is filled out correctly:

**App Information:**
- ✅ App name: `Aigis Marketing` (or your app name)
- ✅ User support email: Your email
- ✅ App logo: (Optional but recommended)
- ✅ Application home page: `https://sorasocialmedia-1.onrender.com`
- ✅ Privacy policy URL: (Required for verification)
- ✅ Terms of service URL: (Required for verification)

**Scopes:**
- ✅ `https://www.googleapis.com/auth/drive.readonly`
- ✅ `https://www.googleapis.com/auth/drive.metadata.readonly`

**Authorized domains:**
- ✅ `onrender.com`
- ✅ `sorasocialmedia-1.onrender.com`

### Step 3: Add Privacy Policy and Terms of Service

**IMPORTANT:** Google requires these for verification:

1. **Create Privacy Policy:**
   - You already have: `https://your-frontend.vercel.app/privacy-policy`
   - Or create a simple one-page privacy policy
   - Must be publicly accessible

2. **Create Terms of Service:**
   - You already have: `https://your-frontend.vercel.app/terms-of-service`
   - Or create a simple one-page terms of service
   - Must be publicly accessible

3. **Add to OAuth Consent Screen:**
   - Go to **OAuth consent screen**
   - Add Privacy Policy URL
   - Add Terms of Service URL
   - Click **Save**

### Step 4: Submit for Verification

1. Go to **OAuth consent screen**
2. Review all sections (should all be green checkmarks)
3. Click **PUBLISH APP** button (top right)
4. You'll see a warning - click **CONFIRM**

### Step 5: Verification Process

**For Non-Sensitive Scopes (Your Case):**
- ✅ `drive.readonly` and `drive.metadata.readonly` are **non-sensitive**
- ✅ Verification is usually **automatic** (instant to 24 hours)
- ✅ No additional review needed

**For Sensitive Scopes:**
- If you add sensitive scopes later (like `drive.file` for write access), you'll need:
  - Security assessment
  - Video demonstration
  - Can take 1-2 weeks

### Step 6: After Verification

Once verified:
- ✅ All users can access your app
- ✅ No need to add test users
- ✅ OAuth consent screen will show "Published" status

## 🔍 Check Verification Status

1. Go to **OAuth consent screen**
2. Look at the top - should show:
   - **Status:** "Published" (green) ✅
   - **Publishing status:** "In production"

## ⚠️ Important Notes

### Testing Mode vs Published

**Testing Mode:**
- Only test users can access
- Good for development
- No verification needed

**Published (Verified):**
- All users can access
- Required for production
- Automatic for non-sensitive scopes

### Your Current Scopes Are Safe

The scopes you're using:
- `drive.readonly` - Read-only access to files
- `drive.metadata.readonly` - Read file metadata only

These are **non-sensitive** and should verify automatically.

## 🐛 Troubleshooting

### "App verification required"

**If you see this:**
1. Make sure Privacy Policy and Terms of Service URLs are added
2. Make sure all required fields are filled
3. Click **PUBLISH APP** again

### "Verification in progress"

**If verification is pending:**
- Usually completes within 24 hours for non-sensitive scopes
- Check back tomorrow
- No action needed

### "Verification failed"

**If verification fails:**
1. Check Privacy Policy URL is accessible
2. Check Terms of Service URL is accessible
3. Make sure app name and description are clear
4. Review Google's feedback (if provided)

## 📝 Quick Checklist

Before submitting for verification:

- [ ] App name is clear and descriptive
- [ ] User support email is set
- [ ] Privacy Policy URL is added and accessible
- [ ] Terms of Service URL is added and accessible
- [ ] Application home page URL is set
- [ ] Authorized domains are added (`onrender.com`)
- [ ] Scopes are added (Drive readonly scopes)
- [ ] OAuth credentials are created
- [ ] Redirect URI is configured correctly

## 🚀 After Verification

Once verified:

1. **Remove Test Users (Optional):**
   - You can remove test users since all users can now access
   - Or keep them - doesn't matter

2. **Update Environment Variables:**
   - No changes needed - same credentials work

3. **Test with New User:**
   - Try connecting Google Drive with a different Google account
   - Should work without being a test user

## 📚 Additional Resources

- [Google OAuth Verification Guide](https://support.google.com/cloud/answer/9110914)
- [OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
- [Google Drive API Scopes](https://developers.google.com/drive/api/guides/api-specific-auth)

## 🎯 Summary

**For your use case (Drive readonly access):**
1. Add Privacy Policy and Terms of Service URLs
2. Click **PUBLISH APP**
3. Verification should be automatic (24 hours max)
4. All users can then access Google Drive integration

**No complex verification process needed** - your scopes are non-sensitive! 🎉

