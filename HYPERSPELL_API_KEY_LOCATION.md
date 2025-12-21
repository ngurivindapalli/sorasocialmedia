# 🔑 Where is the Hyperspell API Key?

## 📍 How Hyperspell is Accessed

Hyperspell is accessed through the **`HyperspellService`** class located at:
- **File:** `backend/services/hyperspell_service.py`
- **Initialized in:** `backend/main.py` (line 196)

The service reads the API key from the environment variable: **`HYPERSPELL_API_KEY`**

---

## 🔍 Where to Set the API Key

### For Local Development

**Location:** `backend/.env` file

Add this line:
```env
HYPERSPELL_API_KEY=your-hyperspell-api-key-here
```

**Example:**
```env
HYPERSPELL_API_KEY=hyp_abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

---

### For Production (Render.com)

**Location:** Render.com Dashboard → Your Service → Environment Tab

1. Go to your Render service dashboard
2. Navigate to **Environment** tab
3. Add new environment variable:

   **Variable Name:**
   ```
   HYPERSPELL_API_KEY
   ```

   **Value:**
   ```
   your-hyperspell-api-key-here
   ```

4. Click **Save Changes**
5. **Redeploy** your service (or it will auto-redeploy)

---

## ✅ How to Verify It's Set

### Check Backend Logs

When the backend starts, you should see one of these messages:

**✅ If API key is set:**
```
[DEBUG] Hyperspell API key found: hyp_abc123def456...xyz
[Hyperspell] OK Hyperspell service initialized
[Hyperspell] OK Each user's memories will be stored in their own Hyperspell account
```

**❌ If API key is NOT set:**
```
[DEBUG] HYPERSPELL_API_KEY not found. Hyperspell memory features will be disabled.
[Hyperspell] API key not provided. Set HYPERSPELL_API_KEY environment variable.
```

### Check API Status

Visit: `https://your-backend.onrender.com/api/hyperspell/status`

Should return:
```json
{
  "available": true,
  "message": "Hyperspell is available"
}
```

---

## 📝 Code Reference

**Where it's read:**
- `backend/main.py` line 137: `HYPERSPELL_API_KEY = os.getenv('HYPERSPELL_API_KEY')`
- `backend/services/hyperspell_service.py` line 33: `self.api_key = api_key or os.getenv('HYPERSPELL_API_KEY')`

**Where it's used:**
- `backend/services/hyperspell_service.py` - All Hyperspell operations use this API key
- Each user's memories are stored in their own Hyperspell account using their email as `user_id`

---

## 🔗 How to Get Your Hyperspell API Key

1. Go to your Hyperspell dashboard
2. Navigate to **API Keys** or **Settings** section
3. Copy your API key (usually starts with `hyp_`)
4. Add it to your `.env` file or Render environment variables

---

## ⚠️ Important Notes

1. **Never commit the API key to git** ✅ (already in `.gitignore`)
2. **For Render:** Set it in the Environment tab, not in code
3. **For local:** Set it in `backend/.env` file
4. **Format:** The key usually starts with `hyp_` but can vary

---

## 🆘 Troubleshooting

### "Hyperspell service is not available"

**Check:**
1. Is `HYPERSPELL_API_KEY` set in your environment?
2. Check backend logs for the initialization message
3. Verify the API key is correct (no extra spaces, correct format)
4. For Render: Make sure you saved the environment variable and redeployed

### "No memories found"

**This is different from API key issues:**
- API key is working (service is available)
- But no memories are found for the user
- This could mean:
  - No documents/competitors have been added yet
  - User email format mismatch (should be fixed now with normalization)
  - Memories haven't been indexed yet

---

## 📋 Quick Checklist

- [ ] API key obtained from Hyperspell dashboard
- [ ] For local: Added to `backend/.env` file
- [ ] For Render: Added to Environment variables
- [ ] Backend restarted/redeployed
- [ ] Check logs to verify initialization
- [ ] Test by adding a document/competitor in Settings

