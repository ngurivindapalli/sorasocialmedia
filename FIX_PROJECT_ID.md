# 🔧 Fix Wrong Project ID (igvideogen → aimarketing-480803)

## Problem

The code is using the wrong Google Cloud project ID:
- **Currently using:** `igvideogen` ❌
- **Should be using:** `aimarketing-480803` ✅

This causes a **403 Forbidden** error because the service account doesn't have access to the `igvideogen` project.

---

## ✅ Solution: Set Environment Variable

### For Local Development (.env file)

Add or update this in your `backend/.env` file:

```env
GOOGLE_CLOUD_PROJECT_ID=aimarketing-480803
```

**OR**

```env
VEO3_PROJECT_ID=aimarketing-480803
```

The code checks both variables (in that order).

---

### For Render.com (Backend)

1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. Add or update:

   **Variable Name:**
   ```
   GOOGLE_CLOUD_PROJECT_ID
   ```

   **Value:**
   ```
   aimarketing-480803
   ```

4. Click **Save Changes**
5. **Redeploy** your service (or it will auto-redeploy)

---

## 🔍 How to Verify

After setting the environment variable, check your backend logs. You should see:

```
[ImageGen] OK Imagen initialized via Vertex AI
[ImageGen]   Project ID: aimarketing-480803  ← Should show this, not igvideogen
[ImageGen]   Location: us-central1
[ImageGen]   Default Model: imagen-4.0-generate-001
```

---

## ⚠️ Important Notes

1. **Service Account JSON**: Make sure your service account JSON file also has `"project_id": "aimarketing-480803"` in it. If it has the old project ID, you'll need to:
   - Create a new service account in the `aimarketing-480803` project, OR
   - Update the existing service account to have access to `aimarketing-480803`

2. **Both Services Use Same Project**: Both Imagen and Veo 3 use the same project ID, so setting `GOOGLE_CLOUD_PROJECT_ID` will fix both.

3. **Restart Required**: After changing environment variables, restart your backend server.

---

## 🧪 Quick Test

After updating, try generating an image again. The error should change from:
- ❌ `projects/igvideogen/...` 
- ✅ `projects/aimarketing-480803/...`

---

## 📝 Environment Variable Priority

The code checks in this order:
1. `GOOGLE_CLOUD_PROJECT_ID` (preferred)
2. `VEO3_PROJECT_ID` (fallback)

So set `GOOGLE_CLOUD_PROJECT_ID` for consistency.

