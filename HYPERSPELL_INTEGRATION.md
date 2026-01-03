# Hyperspell Memory Integration Guide

This document explains how Hyperspell memory integration works across all sections of the application.

## Overview

Hyperspell is integrated into **all content generation endpoints** to provide personalized, context-aware AI responses. All memories are stored in a single Hyperspell account (`sandbox:ngurivindapalli@gmail.com` by default).

## Backend Integration

### Reusable Helper Function

All endpoints use the reusable helper function `get_hyperspell_context()`:

```python
from utils.hyperspell_helper import get_hyperspell_context

# In any endpoint:
hyperspell_context = await get_hyperspell_context(
    hyperspell_service=hyperspell_service,
    query="your search query here",
    user_email=current_user.email if current_user else None
)

# Use the context in your prompts:
enhanced_prompt = f"""{hyperspell_context}

{original_prompt}"""
```

### Endpoints with Hyperspell Integration

1. **`/api/marketing-post/create`** - Marketing post generation
2. **`/api/analyze`** - Instagram video analysis
3. **`/api/video/informational`** - Informational video creation
4. **`/api/video/from-documents`** - Document-based video generation
5. **`/api/video/smart-composition`** - Smart video composition
6. **`/api/video/options`** - Video options generation

### How It Works

1. **Query Construction**: Build a query from user input, topic, or context
2. **Memory Search**: Hyperspell searches all stored memories
3. **Context Injection**: Retrieved context is injected into AI prompts
4. **Enhanced Output**: AI generates content using both user input and stored memories

## Frontend Integration

### React Hook: `useHyperspell`

Use the `useHyperspell` hook in any React component:

```javascript
import { useHyperspell } from '../hooks/useHyperspell'

function MyComponent() {
  const { getContext, addMemory, loading, error } = useHyperspell()
  
  // Get context for a query
  const context = await getContext("AI consulting services")
  
  // Add a new memory
  const success = await addMemory("Our company specializes in AI consulting", "company_info")
}
```

### Pages with Hyperspell

- **MarketingPost** - Uses Hyperspell for personalized post generation
- **HyperspellMemories** - Dedicated page for adding/managing memories
- All other pages can use the `useHyperspell` hook as needed

## Adding Hyperspell to New Endpoints

### Step 1: Import the Helper

```python
from utils.hyperspell_helper import get_hyperspell_context
```

### Step 2: Build Query and Get Context

```python
# Build query from user input/context
memory_query = f"{request.topic} {request.description or ''}".strip()

# Get Hyperspell context
hyperspell_context = await get_hyperspell_context(
    hyperspell_service=hyperspell_service,
    query=memory_query,
    user_email=current_user.email if current_user else None
)
```

### Step 3: Inject into Prompts

```python
# Enhance your prompt with Hyperspell context
if hyperspell_context:
    enhanced_prompt = f"""{hyperspell_context}

{original_prompt}"""
else:
    enhanced_prompt = original_prompt
```

## Configuration

### Environment Variables

- `HYPERSPELL_API_KEY` - Your Hyperspell API key (required)
- `HYPERSPELL_USER_ID` - User ID where all memories are stored (default: `sandbox:ngurivindapalli@gmail.com`)

### All Memories Go To One Account

All memories from all users are stored in the same Hyperspell account. This is configured in `backend/services/hyperspell_service.py`:

```python
self.user_id = user_id or os.getenv('HYPERSPELL_USER_ID', 'sandbox:ngurivindapalli@gmail.com')
```

## API Endpoints

### Add Memory
- **POST** `/api/hyperspell/add-memory`
- Body: `{ "text": "...", "collection": "optional" }`

### Query Memories
- **POST** `/api/hyperspell/query`
- Body: `{ "query": "...", "max_results": 5 }`

### Check Status
- **GET** `/api/hyperspell/status`

## Best Practices

1. **Build Good Queries**: Include relevant keywords from user input
2. **Use Collections**: Organize memories into collections for better retrieval
3. **Error Handling**: Hyperspell failures are non-critical - always continue without context if it fails
4. **Logging**: All Hyperspell operations are logged for debugging

## Example: Adding to a New Endpoint

```python
@app.post("/api/my-endpoint")
async def my_endpoint(
    request: MyRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    # Build query from request
    memory_query = f"{request.topic} {request.context or ''}".strip()
    
    # Get Hyperspell context (reusable helper)
    hyperspell_context = await get_hyperspell_context(
        hyperspell_service=hyperspell_service,
        query=memory_query,
        user_email=current_user.email if current_user else None
    )
    
    # Enhance your prompt
    prompt = f"""Generate content about: {request.topic}
    
{hyperspell_context if hyperspell_context else ''}

{request.additional_context}"""
    
    # Continue with your logic...
```














