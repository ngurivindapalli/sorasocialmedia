# How Hyperspell is Used in This Application 🧠

## Overview

Hyperspell is integrated as a **memory and context layer** that enhances AI script generation with persistent user context. It provides personalized, context-aware video scripts by remembering user preferences, brand information, and past interactions.

---

## Architecture

```
┌─────────────────┐
│   Frontend      │
│  (React/Vite)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Backend API   │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────────┐
│ Hyperspell │ │ OpenAI/Claude   │
│  Service   │ │   Service        │
└─────┬─────┘ └────────┬─────────┘
      │                │
      │                │
      ▼                ▼
┌─────────────────────────────┐
│   Script Generation         │
│  (Enhanced with Memory)     │
└─────────────────────────────┘
```

---

## Integration Points

### 1. **Service Initialization** (`backend/main.py`)

```python
# Initialize Hyperspell service
hyperspell_service = HyperspellService()

# Pass to UserContextService
user_context_service = UserContextService(hyperspell_service=hyperspell_service)

# Pass to OpenAIService (for Claude integration)
openai_service = OpenAIService(
    api_key=OPENAI_API_KEY,
    anthropic_key=ANTHROPIC_API_KEY,
    hyperspell_service=hyperspell_service  # ← Hyperspell integration
)
```

**Location**: `backend/main.py` lines 163-175

---

### 2. **Video Script Generation** (`backend/main.py` - `/api/video/from-documents`)

When generating video scripts from documents, Hyperspell is queried to enhance the prompt:

```python
# Step 3.5: Get Hyperspell memory context for enhanced personalization
hyperspell_memory_context = ""

if user_id and hyperspell_service.is_available():
    try:
        # Create a query from the document content
        memory_query = f"video script about {request.topic or 'content creation'}"
        
        # Query Hyperspell for relevant memories
        hyperspell_memory_context = await hyperspell_service.get_context_summary(
            user_id, 
            memory_query
        )
        
        # Enhance page_context with Hyperspell memory
        page_context = f"""{hyperspell_memory_context}
        
        {page_context}"""
    except Exception as hyperspell_error:
        # Non-critical - continue without Hyperspell if it fails
        print(f"[API] ⚠️ Hyperspell memory query skipped: {hyperspell_error}")
```

**Location**: `backend/main.py` lines 251-278

**What it does**:
- Queries Hyperspell for relevant user memories based on the video topic
- Injects retrieved context into the AI prompt
- Enhances script personalization with user's past preferences and brand information

---

### 3. **OpenAI Service Integration** (`backend/services/openai_service.py`)

The `OpenAIService` uses Hyperspell when generating Sora scripts:

#### For Claude API:

```python
async def generate_sora_script(self, transcription, video_metadata, user_id=None, ...):
    # Enhance prompt with Hyperspell memory if available
    if self.hyperspell_service and self.hyperspell_service.is_available():
        # Extract query from transcription or metadata
        memory_query = transcription[:200] if transcription else video_metadata.get('text', '')[:200]
        
        if memory_query:
            # Get Hyperspell context
            hyperspell_context = await self._get_hyperspell_context(user_id, memory_query)
            
            if hyperspell_context:
                # Inject into prompt
                enhanced_prompt = f"""{hyperspell_context}
                
                {original_prompt}"""
                
                # Use enhanced prompt for Claude
                response = await self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    messages=[{"role": "user", "content": enhanced_prompt}],
                    system="You are an expert video production director. Use any provided memory context to personalize the prompt."
                )
```

**Location**: `backend/services/openai_service.py` lines 287-306

#### For OpenAI GPT-4:

```python
async def generate_structured_sora_script(self, transcription, video_metadata, user_id=None, ...):
    # Enhance page_context with Hyperspell memory if available
    if user_id and self.hyperspell_service and self.hyperspell_service.is_available():
        try:
            memory_query = f"{transcription[:200]} {video_metadata.get('text', '')[:100]}".strip()
            if memory_query:
                hyperspell_context = await self._get_hyperspell_context(user_id, memory_query)
                if hyperspell_context:
                    # Inject into page_context
                    page_context = f"{hyperspell_context}\n\n{page_context}"
        except Exception as e:
            print(f"[OpenAI+Hyperspell] Error: {e}")
```

**Location**: `backend/services/openai_service.py` lines 339-350

---

### 4. **User Context Service** (`backend/services/user_context_service.py`)

The `UserContextService` can optionally query Hyperspell when building user context summaries:

```python
async def get_context_summary_for_ai(self, user_id: str, query: Optional[str] = None) -> str:
    # ... build context from user preferences, history, etc. ...
    
    # Optionally enhance with Hyperspell if query provided
    if query and self.hyperspell_service and self.hyperspell_service.is_available():
        try:
            hyperspell_context = await self.hyperspell_service.get_context_summary(user_id, query)
            if hyperspell_context:
                context_summary += f"\n\n{hyperspell_context}"
        except Exception as e:
            print(f"[UserContext+Hyperspell] Error: {e}")
    
    return context_summary
```

**Location**: `backend/services/user_context_service.py`

---

## API Endpoints

### 1. **GET `/api/hyperspell/status`**

Check if Hyperspell is configured and available.

**Response**:
```json
{
  "available": true,
  "message": "Hyperspell is configured and ready"
}
```

**Location**: `backend/main.py` lines 3500+

---

### 2. **GET `/api/hyperspell/connect-url`**

Get a URL for users to connect their accounts (Gmail, Calendar, Documents, etc.) to Hyperspell.

**Response**:
```json
{
  "connect_url": "https://connect.hyperspell.com?token=...",
  "message": "Use this URL to connect your accounts to Hyperspell"
}
```

**Location**: `backend/main.py` lines 3415-3443

---

### 3. **POST `/api/hyperspell/query`**

Query Hyperspell memories for a specific user.

**Request**:
```json
{
  "query": "video script about AI consulting"
}
```

**Response**:
```json
{
  "query": "video script about AI consulting",
  "results": [...],
  "user_id": "...",
  "queried_at": "2024-..."
}
```

**Location**: `backend/main.py` lines 3446-3470

---

### 4. **POST `/api/hyperspell/upload`**

Upload a document to Hyperspell memory layer.

**Request**: Multipart form with `file` field

**Response**:
```json
{
  "resource_id": "...",
  "filename": "document.pdf",
  "uploaded_at": "2024-...",
  "user_id": "..."
}
```

**Location**: `backend/main.py` lines 3473-3500

---

## How It Works in Practice

### Example Flow:

1. **User generates a video script** from documents about "AI Consulting"

2. **Backend queries Hyperspell**:
   ```
   Query: "video script about AI consulting"
   ```

3. **Hyperspell returns relevant memories**:
   - Past video scripts the user approved
   - Brand guidelines from uploaded documents
   - User's preferred tone and style
   - Previous successful topics

4. **Context is injected into AI prompt**:
   ```
   HYPERSPELL MEMORY CONTEXT:
   1. User prefers professional, educational tone...
   2. Brand colors: Blue (#0066CC), White...
   3. Previous successful scripts used hook format...
   
   [Original prompt continues...]
   ```

5. **AI generates personalized script** using:
   - The original prompt (document content, topic, etc.)
   - Hyperspell memory context (user preferences, brand info)
   - User context service data (behavioral patterns, history)

6. **Result**: A highly personalized, context-aware video script that matches the user's brand and preferences

---

## Benefits

✅ **Persistent Memory**: Remembers user preferences across sessions  
✅ **Brand Consistency**: Uses uploaded brand guidelines and documents  
✅ **Personalization**: Adapts scripts to user's style and past successful content  
✅ **Context-Aware**: Understands user's business, industry, and goals  
✅ **Non-Intrusive**: Fails gracefully if Hyperspell is unavailable  

---

## Configuration

### Environment Variable

```bash
HYPERSPELL_API_KEY=hs2-301-uTW8oEzG7vqI7qTTQRWzry6UCzJyfQN8
```

**Location**: `backend/.env`

### Service Availability Check

The service checks if Hyperspell is available before using it:

```python
if hyperspell_service.is_available():
    # Use Hyperspell
else:
    # Continue without Hyperspell (graceful fallback)
```

---

## Current Status

✅ **Integrated**: Hyperspell is fully integrated into script generation  
✅ **Active**: Service is initialized and available  
✅ **Used in**: 
   - Document-based video generation (`/api/video/from-documents`)
   - Script generation with OpenAI GPT-4
   - Script generation with Claude
   - User context building

---

## Future Enhancements

Potential improvements:
- Auto-upload generated scripts to Hyperspell for future reference
- Query Hyperspell for similar past content when generating new videos
- Use Hyperspell to learn from user's editing patterns
- Store video performance data in Hyperspell for better recommendations

---

## Summary

Hyperspell acts as a **memory layer** that:
1. **Stores** user preferences, brand info, and past content
2. **Retrieves** relevant context when generating new scripts
3. **Enhances** AI prompts with personalized information
4. **Improves** script quality by making them context-aware

The integration is **non-blocking** - if Hyperspell is unavailable, the app continues to work normally, just without the memory enhancement.




















