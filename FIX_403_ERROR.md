# 🔧 Fix 403 Forbidden Error - Imagen Generation

## Error Message
```
403 Forbidden for url 'https://us-central1-aiplatform.googleapis.com/v1/projects/igvideogen/locations/us-central1/publishers/google/models/imagen-4.0-ultra-generate-001:predict'
```

## 🔍 What This Means

A **403 Forbidden** error means your service account **doesn't have permission** to access Imagen, or the API is **not enabled**. This is different from 401 (authentication failed).

---

## ✅ Fix Checklist (Try in Order)

### 1. **Enable Vertex AI API** (Most Common Issue)

The Vertex AI API must be enabled in your Google Cloud project:

1. Go to: https://console.cloud.google.com/apis/library/aiplatform.googleapis.com
2. Select your project: **`igvideogen`**
3. Click **"Enable"**
4. Wait 1-2 minutes for it to activate
5. Try again

**Or via gcloud CLI:**
```bash
gcloud services enable aiplatform.googleapis.com --project=igvideogen
```

---

### 2. **Check Service Account Permissions**

Your service account needs the **Vertex AI User** role:

1. Go to: https://console.cloud.google.com/iam-admin/iam?project=igvideogen
2. Find your service account (the email from your JSON key)
3. Check if it has **`Vertex AI User`** role
4. If not, click **"Edit"** → **"Add Another Role"** → Select **`Vertex AI User`**
5. Click **"Save"**

**Or via gcloud CLI:**
```bash
gcloud projects add-iam-policy-binding igvideogen \
  --member="serviceAccount:YOUR-SERVICE-ACCOUNT-EMAIL@igvideogen.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

---

### 3. **Check if Imagen 4 Ultra Requires Access Request**

Imagen 4 Ultra might be in **limited preview** and require explicit access:

1. Go to: https://console.cloud.google.com/vertex-ai/models?project=igvideogen
2. Check if `imagen-4.0-ultra-generate-001` appears in the list
3. If not, you may need to:
   - Request access from Google Cloud support
   - Or use a different model (see step 4)

---

### 4. **Try a Different Imagen Model**

If Imagen 4 Ultra isn't available, try these models instead:

**Option A: Use Imagen 4 (Standard)**
```env
IMAGEN_MODEL_ID=imagen-4.0-generate-001
```

**Option B: Use Imagen 4 Fast**
```env
IMAGEN_MODEL_ID=imagen-4.0-fast-generate-001
```

**Option C: Use Imagen 3**
```env
IMAGEN_MODEL_ID=imagen-3.0-generate-001
```

The code will automatically try these fallback models if Ultra fails.

---

### 5. **Verify Project ID**

Make sure your project ID is correct:

1. Check your `.env` file:
   ```env
   GOOGLE_CLOUD_PROJECT_ID=igvideogen
   # OR
   VEO3_PROJECT_ID=igvideogen
   ```

2. Verify the project exists:
   - Go to: https://console.cloud.google.com/home/dashboard?project=igvideogen
   - Make sure you can access it

---

### 6. **Check Billing**

Vertex AI requires **billing to be enabled**:

1. Go to: https://console.cloud.google.com/billing?project=igvideogen
2. Make sure billing is enabled
3. If not, enable it and add a payment method

---

### 7. **Verify Service Account JSON**

Make sure your service account JSON is valid:

1. Check the `project_id` in your JSON matches `igvideogen`
2. Verify the JSON is not corrupted
3. Make sure you're using the correct service account

**To verify:**
```bash
# If using file path
cat path/to/your-service-account.json | jq .project_id

# Should output: "igvideogen"
```

---

## 🧪 Quick Test

Test if Vertex AI API is accessible:

```bash
# Using gcloud CLI
gcloud ai models list --region=us-central1 --project=igvideogen

# If this works, the API is enabled and accessible
```

---

## 🔄 After Making Changes

1. **Restart your backend server**
2. **Clear any cached tokens** (if using gcloud CLI: `gcloud auth application-default revoke`)
3. **Try generating an image again**

---

## 📝 Most Likely Solutions (In Order)

1. ✅ **Enable Vertex AI API** (90% of cases)
2. ✅ **Add Vertex AI User role** to service account
3. ✅ **Try Imagen 4 (standard) instead of Ultra**
4. ✅ **Check billing is enabled**

---

## 🆘 Still Not Working?

If none of the above works:

1. **Check the full error response** - Look at backend logs for more details
2. **Try using gcloud CLI auth** temporarily:
   ```env
   VEO3_USE_GCLOUD_AUTH=true
   ```
   Then run: `gcloud auth login`
3. **Check Google Cloud status**: https://status.cloud.google.com/
4. **Verify your service account email** has access to the project

---

## 💡 Pro Tip

The code automatically tries fallback models. If Imagen 4 Ultra fails, it will try:
- Imagen 4
- Imagen 4 Fast  
- Imagen 3
- Imagen 2

So even if Ultra isn't available, image generation should still work with a different model.

