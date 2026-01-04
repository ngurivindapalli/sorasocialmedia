# Hyperspell Integration Guide 🧠✨

This guide explains how to set up and use Hyperspell in your video hook generator application for enhanced memory and context awareness.

## What is Hyperspell?

Hyperspell is the memory & context layer for AI agents. It provides:
- **Persistent Memory**: Continuously indexes user data to build a memory graph
- **Context Engineering**: Enriches AI agents with real-time context from user's data
- **Instant Answers**: Grounded answers from user's connected data sources
- **Privacy & Security**: SOC2 and GDPR compliant

## 🚀 Quick Start

### 1. Get Your Hyperspell API Key

1. Visit [Hyperspell Dashboard](https://app.hyperspell.com/)
2. Create an account or log in
3. Create a new application
4. Copy your API key from the dashboard

### 2. Set Environment Variable

Add to your `backend/.env` file:

```bash
HYPERSPELL_API_KEY=your_hyperspell_api_key_here
```

### 3. Install Dependencies

The Hyperspell SDK is already included in `requirements.txt`. Install it:

```bash
cd backend
pip install -r requirements.txt
```

### 4. Restart Your Backend

Restart your FastAPI server to load the Hyperspell service:

```bash
python main.py
```

You should see:
```
[Hyperspell] ✓ Hyperspell service initialized
```

## 📖 Usage

### For Users: Connect Your Accounts

1. **Get Connect URL**: Call `GET /api/hyperspell/connect-url` (requires authentication)
2. **Open URL**: Users open the URL in a new tab to connect their accounts
3. **Connect Accounts**: Users can connect Gmail, Calendar, Documents, and more
4. **Automatic Indexing**: Hyperspell automatically indexes connected data

### For Developers: Query Memories

Use Hyperspell to enhance AI responses with user context:

```python
# Query user's memories
response = await hyperspell_service.query_memories(
    user_id="user_123",
    query="What is the project deadline?",
    max_results=5
)
```

### Integration with User Context

The `UserContextService` automatically uses Hyperspell when available:

```python
# Enhanced context summary includes Hyperspell memories
context = await user_context_service.get_context_summary_for_ai(
    user_id="user_123",
    query="video generation preferences"
)
```

## 🔌 API Endpoints

### `GET /api/hyperspell/connect-url`
Get Hyperspell Connect URL for user to link accounts.

**Authentication**: Required

**Response**:
```json
{
  "connect_url": "https://connect.hyperspell.com?token=user_123",
  "message": "Use this URL to connect your accounts to Hyperspell",
  "instructions": "Open this URL in a new tab to connect your accounts..."
}
```

### `POST /api/hyperspell/query`
Query Hyperspell memory layer for relevant context.

**Authentication**: Required

**Request Body**:
```json
{
  "query": "What is the project deadline?",
  "max_results": 5
}
```

**Response**:
```json
{
  "query": "What is the project deadline?",
  "results": [...],
  "user_id": "user_123",
  "queried_at": "2025-01-15T10:30:00"
}
```

### `POST /api/hyperspell/upload`
Upload a document to Hyperspell memory layer.

**Authentication**: Required

**Request**: Multipart form data with `file` field

**Response**:
```json
{
  "success": true,
  "resource_id": "doc_123",
  "filename": "document.pdf",
  "message": "Document uploaded successfully to Hyperspell memory layer"
}
```

### `GET /api/hyperspell/status`
Check Hyperspell service status.

**Response**:
```json
{
  "available": true,
  "message": "Hyperspell is available"
}
```

## 🎯 How It Works

1. **User Connects Accounts**: Via Hyperspell Connect URL
2. **Automatic Indexing**: Hyperspell continuously indexes user's data
3. **Memory Graph**: Builds a knowledge graph of user's information
4. **Context Retrieval**: Query memories to get relevant context
5. **Enhanced AI**: Use context in AI prompts for better responses

## 🔒 Privacy & Security

- **SOC2 Certified**: Independent security audit
- **GDPR Compliant**: EU data protection standards
- **User Control**: Users can delete their data at any time
- **No Training**: Data is not used to train foundational AI models
- **No Sharing**: Data is not shared with third parties

## 💡 Use Cases

### 1. Personalized Video Generation
```python
# Get user's brand preferences from their documents
context = await hyperspell_service.query_memories(
    user_id=user_id,
    query="brand voice and style preferences"
)
# Use context in video generation prompts
```

### 2. Document-Based Context
```python
# Upload company documents
await hyperspell_service.upload_document(
    user_id=user_id,
    file_path="brand_guidelines.pdf"
)
# Query for brand information
memories = await hyperspell_service.query_memories(
    user_id=user_id,
    query="brand colors and messaging"
)
```

### 3. Calendar & Meeting Context
```python
# Query upcoming meetings or deadlines
context = await hyperspell_service.query_memories(
    user_id=user_id,
    query="upcoming deadlines and important dates"
)
```

## 🐛 Troubleshooting

### Hyperspell Not Available

**Issue**: `"Hyperspell service is not available"`

**Solutions**:
1. Check that `HYPERSPELL_API_KEY` is set in `.env`
2. Verify API key is correct
3. Restart backend server
4. Check logs for initialization errors

### Connection Issues

**Issue**: Cannot connect accounts via Hyperspell Connect

**Solutions**:
1. Ensure user is authenticated
2. Verify user_id is valid
3. Check Hyperspell dashboard for account status
4. Try generating a new connect URL

### Query Returns Empty

**Issue**: Memory queries return no results

**Solutions**:
1. Ensure user has connected accounts
2. Wait for indexing to complete (can take a few minutes)
3. Try uploading documents manually
4. Use more specific queries

## 📚 Resources

- [Hyperspell Documentation](https://docs.hyperspell.com/)
- [Hyperspell Dashboard](https://app.hyperspell.com/)
- [API Reference](https://docs.hyperspell.com/api-reference)

## 🎉 Benefits

✅ **Better Context**: AI understands user's specific situation  
✅ **Persistent Memory**: Remembers across sessions  
✅ **Privacy First**: User controls their data  
✅ **Easy Integration**: One-line SDK integration  
✅ **Continuous Learning**: Improves with every query  

---

**Need Help?** Contact Hyperspell support at hello@hyperspell.com




















