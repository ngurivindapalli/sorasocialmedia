# Hyperspell + Claude Integration 🧠✨

This document describes the enhanced integration between Hyperspell memory layer and Claude (Anthropic) AI for context-aware video generation.

## Overview

The application now supports **Hyperspell memory integration with Claude API calls**, providing persistent memory and context awareness for better AI-generated content. When using Claude as the LLM provider, the system automatically enriches prompts with relevant user memories from Hyperspell.

## How It Works

### 1. Automatic Memory Enhancement

When generating Sora scripts with Claude (`llm_provider="claude"`), the system:

1. **Extracts Query**: Creates a memory query from the video transcription or metadata
2. **Queries Hyperspell**: Searches user's memory layer for relevant context
3. **Enhances Prompt**: Injects memory context into Claude's system prompt
4. **Generates Response**: Claude uses both the video data and user memories for personalized output

### 2. Integration Points

#### OpenAIService Enhancement

The `OpenAIService` class now accepts a `hyperspell_service` parameter:

```python
openai_service = OpenAIService(
    api_key=OPENAI_API_KEY,
    anthropic_key=ANTHROPIC_API_KEY,
    fine_tuned_model=fine_tuned_model,
    hyperspell_service=hyperspell_service  # Hyperspell integration
)
```

#### Claude API Calls

When using Claude for script generation:

```python
# Automatic Hyperspell enhancement happens internally
script = await openai_service.generate_sora_script(
    transcription=transcription,
    video_metadata=metadata,
    llm_provider="claude",  # Uses Claude with Hyperspell
    user_id="user_123"  # Optional: for user-specific memories
)
```

### 3. Memory Query Strategy

The system intelligently creates memory queries from:

- **Video Transcription**: First 200 characters of transcription
- **Video Caption**: If transcription unavailable
- **User Context**: User ID for personalized memories

## Benefits

✅ **Personalized Content**: Claude generates scripts based on user's past preferences and brand  
✅ **Context Awareness**: Remembers user's style, tone, and content themes  
✅ **Better Alignment**: Scripts align with user's documented brand guidelines  
✅ **Continuous Learning**: Improves with each interaction  

## Usage Examples

### Basic Usage

```python
# Generate script with Claude + Hyperspell
script = await openai_service.generate_sora_script(
    transcription="Welcome to our channel...",
    video_metadata={
        "views": 10000,
        "likes": 500,
        "text": "New product launch"
    },
    llm_provider="claude",
    user_id="user_123"  # For personalized memories
)
```

### With User Context

```python
# The system automatically queries Hyperspell for:
# - User's brand voice preferences
# - Previous successful content themes
# - Document-based brand guidelines
# - Calendar/deadline context
```

## Configuration

### Required Environment Variables

```bash
# Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Hyperspell API
HYPERSPELL_API_KEY=your_hyperspell_api_key
```

### Service Initialization

The services are automatically initialized in `main.py`:

```python
# Initialize Hyperspell
hyperspell_service = HyperspellService()

# Initialize OpenAI service with Hyperspell
openai_service = OpenAIService(
    api_key=OPENAI_API_KEY,
    anthropic_key=ANTHROPIC_API_KEY,
    hyperspell_service=hyperspell_service
)
```

## API Endpoints

### Generate Script with Claude + Hyperspell

**Endpoint**: `POST /api/analyze`

**Request**:
```json
{
  "username": "example_user",
  "video_limit": 3,
  "llm_provider": "claude"
}
```

**Response**: Enhanced script with Hyperspell context automatically included

### Check Integration Status

**Endpoint**: `GET /api/hyperspell/status`

**Response**:
```json
{
  "available": true,
  "message": "Hyperspell is available"
}
```

## How Memory Context is Used

### Example Memory Context Injection

When Hyperspell finds relevant memories, they're injected like this:

```
HYPERSPELL MEMORY CONTEXT:
1. Brand voice: Professional, friendly, approachable...
2. Content themes: Technology, innovation, user experience...
3. Previous successful topics: Product launches, tutorials...

[Original prompt continues...]
```

Claude then uses this context to:
- Match brand voice and tone
- Align with documented content themes
- Reference successful past content
- Incorporate brand guidelines

## Troubleshooting

### Claude Not Using Hyperspell

**Issue**: Claude responses don't seem personalized

**Solutions**:
1. Verify `HYPERSPELL_API_KEY` is set
2. Check that user has connected accounts via Hyperspell Connect
3. Ensure user_id is passed correctly
4. Check logs for `[Claude+Hyperspell]` messages

### No Memory Context Found

**Issue**: `[Claude+Hyperspell]` shows no context

**Solutions**:
1. User needs to connect accounts first
2. Wait for indexing to complete (few minutes)
3. Upload documents manually if needed
4. Try more specific queries

## Architecture

```
User Request
    ↓
OpenAIService.generate_sora_script()
    ↓
HyperspellService.query_memories()  ← Memory lookup
    ↓
Enhanced Prompt (with memory context)
    ↓
Claude API (claude-3-5-sonnet-20241022)
    ↓
Personalized Script Response
```

## Future Enhancements

- [ ] User-specific memory queries based on video topic
- [ ] Multi-turn conversation memory
- [ ] Automatic memory updates from generated content
- [ ] Memory-based A/B testing
- [ ] Cross-session memory persistence

## Related Documentation

- [Hyperspell Setup Guide](./HYPERSPELL_SETUP.md)
- [Claude API Documentation](https://docs.anthropic.com/)
- [Hyperspell Documentation](https://docs.hyperspell.com/)

---

**Status**: ✅ Active - Hyperspell + Claude integration is fully operational












