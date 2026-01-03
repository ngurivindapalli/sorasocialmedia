# Hyperspell Testing Guide 🧪✨

This guide will help you test the Hyperspell integration in your application.

## Prerequisites

✅ Backend server running on `http://localhost:8000`  
✅ Frontend server running on `http://localhost:3001`  
✅ Hyperspell API key configured in `backend/.env`  
✅ Hyperspell SDK installed in backend venv  

## Quick Start

1. **Open the application**: Navigate to `http://localhost:3001`
2. **Go to Settings**: Click on "Settings" in the navigation
3. **Find Hyperspell Section**: Scroll down to "Hyperspell Memory & Context"

## Testing Steps

### 1. Check Status ✅

**What to test**: Verify Hyperspell service is available

**Steps**:
1. Go to Settings page
2. Look at the "Hyperspell Memory & Context" section
3. Check the status indicator

**Expected Result**:
- ✅ Green checkmark with "Status: Available"
- Message: "Hyperspell is available"

**If not working**:
- Check backend logs for Hyperspell initialization
- Verify `HYPERSPELL_API_KEY` is in `backend/.env`
- Restart backend server

---

### 2. Connect User Accounts 🔗

**What to test**: Get Hyperspell Connect URL for users to link accounts

**Steps**:
1. Make sure you're logged in (create account if needed)
2. Click "Get Connect URL" button
3. Copy the URL that appears
4. Open URL in a new tab

**Expected Result**:
- URL appears in a blue box
- URL format: `https://connect.hyperspell.com?token=...`
- Opening URL shows Hyperspell Connect interface

**Note**: You need to be authenticated to get the connect URL. If you see an error, make sure you're logged in.

---

### 3. Query Memories 🔍

**What to test**: Search user's memory layer for relevant context

**Steps**:
1. Enter a query in the search box (e.g., "What is the project deadline?")
2. Click "Search" button
3. View results

**Expected Result**:
- Results appear in a formatted JSON box
- Results include relevant memories from connected accounts
- If no accounts connected, you may get empty results

**Test Queries**:
- "What are my upcoming deadlines?"
- "What is my brand voice?"
- "What projects am I working on?"
- "What are my content preferences?"

---

### 4. Upload Document 📄

**What to test**: Upload a document to enhance memory layer

**Steps**:
1. Click "Choose File" button
2. Select a PDF, DOCX, or TXT file
3. Wait for upload to complete

**Expected Result**:
- Success message with resource ID
- File is added to memory layer
- Can query for information from uploaded document

**Test Files**:
- Brand guidelines PDF
- Company document
- Meeting notes
- Any text-based document

---

## Testing with Claude Integration

### Test Memory-Enhanced Script Generation

**What to test**: Generate video scripts using Claude with Hyperspell memory

**Steps**:
1. Go to Instagram Tools or LinkedIn Tools
2. Enter a username or topic
3. Select `llm_provider: "claude"` (if available in UI)
4. Generate a script

**Expected Result**:
- Script is personalized based on user's memories
- Brand voice matches user's preferences
- Content themes align with user's documented style

**Check Backend Logs**:
Look for these messages:
```
[Claude+Hyperspell] Enhanced prompt with memory context (XXX chars)
[Claude] Generating Sora script with Claude...
```

---

## API Endpoint Testing

You can also test directly via API:

### Check Status
```bash
curl http://localhost:8000/api/hyperspell/status
```

**Expected Response**:
```json
{
  "available": true,
  "message": "Hyperspell is available"
}
```

### Get Connect URL (requires auth)
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/hyperspell/connect-url
```

### Query Memories (requires auth)
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the project deadline?", "max_results": 5}' \
  http://localhost:8000/api/hyperspell/query
```

### Upload Document (requires auth)
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  http://localhost:8000/api/hyperspell/upload
```

---

## Troubleshooting

### Status Shows "Not Available"

**Possible Causes**:
1. Hyperspell SDK not installed in venv
2. API key not in `.env` file
3. Server not restarted after adding key

**Solutions**:
```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install hyperspell
# Verify key in .env
# Restart server
```

### Connect URL Returns 401

**Cause**: Not authenticated

**Solution**: 
- Log in to the application first
- Or use API with valid Bearer token

### Query Returns Empty Results

**Possible Causes**:
1. No accounts connected yet
2. Accounts not fully indexed
3. Query too specific

**Solutions**:
- Connect accounts via Connect URL first
- Wait a few minutes for indexing
- Try more general queries

### Upload Fails

**Possible Causes**:
1. File too large
2. Unsupported format
3. Not authenticated

**Solutions**:
- Use PDF, DOCX, or TXT files
- Check file size limits
- Ensure you're logged in

---

## Expected Behavior

### When Everything Works

1. **Status**: ✅ Available
2. **Connect URL**: Generates successfully
3. **Query**: Returns relevant memories
4. **Upload**: Documents upload successfully
5. **Claude Integration**: Scripts are personalized

### Console Logs to Look For

**Backend**:
```
[DEBUG] Hyperspell API key found: hs2-301-uTW8oEzG7v...
[Hyperspell] ✓ Hyperspell service initialized
[Claude] Claude API initialized ✓ with Hyperspell memory
```

**Frontend** (Browser Console):
```
[API] Request: GET /api/hyperspell/status
[API] Response: 200 /api/hyperspell/status
```

---

## Next Steps

After testing:

1. **Connect Real Accounts**: Use Connect URL to link Gmail, Calendar, etc.
2. **Upload Brand Documents**: Add your brand guidelines
3. **Test Claude Generation**: Generate scripts with memory enhancement
4. **Monitor Performance**: Check how memory improves script quality

---

## Support

If you encounter issues:

1. Check backend logs in PowerShell window
2. Check browser console for frontend errors
3. Verify all environment variables are set
4. Ensure both servers are running

**Happy Testing!** 🚀



















