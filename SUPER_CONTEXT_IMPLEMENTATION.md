# Super Context Implementation Guide

## Overview

This document outlines the comprehensive user context system implemented to enhance script and video generation with personalized, context-aware AI outputs.

## Research-Based Methods Implemented

Based on industry research and best practices, we've implemented the following "super context" methods:

### 1. **User Preference Profiling**
- **Brand Voice**: Captures user's preferred communication style
- **Content Style**: Educational, entertaining, inspirational, etc.
- **Target Audience**: Specific demographic information
- **Video Preferences**: Preferred length, model (Sora vs Veo 3), platform
- **Visual Preferences**: Brand colors, tone preferences, content themes

### 2. **Behavioral Pattern Analysis**
- **Content Generation History**: Tracks all generated videos
- **Approval/Rejection Patterns**: Learns what users like/dislike
- **Editing Patterns**: Understands how users modify scripts
- **Platform Usage**: Identifies most-used platforms
- **Duration Preferences**: Calculates average preferred video length
- **Model Preferences**: Tracks preferred video generation model

### 3. **Brand Intelligence Extraction**
- **Social Profile Analysis**: Extracts brand elements from Instagram/LinkedIn profiles
- **Document Analysis**: Extracts themes, messaging, and brand guidelines from uploaded documents
- **Content Theme Identification**: Builds a library of successful content themes
- **Visual Style Learning**: Captures visual preferences from analyzed profiles
- **Messaging Pattern Recognition**: Identifies successful messaging frameworks

### 4. **Performance-Based Learning**
- **Successful Content Tracking**: Records topics and styles that get approved
- **Failed Content Analysis**: Identifies what doesn't work for the user
- **Engagement Pattern Analysis**: Tracks what generates engagement
- **A/B Testing Data**: Can incorporate performance metrics

### 5. **Multi-Modal Context Fusion**
- **Document Context**: PDFs, DOCX, TXT files
- **Social Media Context**: Instagram, LinkedIn profile analysis
- **User Behavior**: Historical generation patterns
- **Preference Data**: Explicitly set user preferences
- **Performance Data**: What has worked in the past

## Implementation Details

### Backend Services

#### `UserContextService` (`backend/services/user_context_service.py`)

**Key Methods:**
- `get_user_context(user_id)`: Retrieves comprehensive user profile
- `update_preferences(user_id, preferences)`: Updates user preferences
- `record_video_generation(user_id, data)`: Tracks video generation events
- `record_social_profile_analysis(user_id, platform, data)`: Records profile analysis
- `record_document_analysis(user_id, data)`: Records document insights
- `get_context_summary_for_ai(user_id)`: Generates AI-ready context summary
- `get_preferred_settings(user_id)`: Returns auto-fill settings

**Context Structure:**
```json
{
  "preferences": {
    "brand_voice": "...",
    "content_style": "...",
    "target_audience": "...",
    "preferred_video_length": 15,
    "video_model_preference": "veo-3",
    "platform_preferences": {},
    "content_themes": [],
    "brand_colors": [],
    "tone_preferences": []
  },
  "content_history": {
    "generated_videos": [],
    "approved_scripts": [],
    "rejected_scripts": [],
    "successful_topics": []
  },
  "behavioral_patterns": {
    "most_used_platforms": [],
    "average_video_duration": 15.5,
    "preferred_video_model": "veo-3"
  },
  "brand_insights": {
    "content_themes": [],
    "visual_style_preferences": [],
    "messaging_patterns": []
  }
}
```

### API Endpoints

1. **POST `/api/user/preferences`**: Update user preferences
2. **GET `/api/user/context`**: Get full user context
3. **GET `/api/user/preferred-settings`**: Get auto-fill settings

### Integration Points

#### Script Generation Enhancement

The `generate_linkedin_optimized_script` method now accepts `user_context` parameter:

```python
script_result = await openai_service.generate_linkedin_optimized_script(
    document_context=document_context,
    topic=request.topic,
    duration=duration_for_script,
    target_audience=request.target_audience,
    key_message=request.key_message,
    video_model=video_model_for_script,
    user_context=user_context_summary  # NEW: User context for personalization
)
```

#### Context Injection into AI Prompts

User context is injected into AI prompts at two levels:

1. **Document Analysis Phase**: 
   - Includes user preferences, brand voice, successful topics
   - Guides AI decisions on topic, audience, duration

2. **Script Generation Phase**:
   - Personalizes script to match user's brand voice
   - References successful content patterns
   - Aligns with behavioral preferences

### Automatic Context Collection

The system automatically collects context from:

1. **Video Generations**: Every video generation is recorded
2. **Script Approvals/Rejections**: Tracks what users approve/reject
3. **Script Edits**: Learns from user modifications
4. **Social Profile Analysis**: Extracts brand elements
5. **Document Uploads**: Analyzes and extracts themes

## Frontend Integration

### Context Storage

Uses `contextStorage` utility (`frontend/src/utils/contextStorage.js`):
- Stores context per user ID
- Persistent for authenticated users (localStorage)
- Session-based for guests (sessionStorage)

### User Preferences Component (To Be Created)

A settings/preferences component where users can:
- Set brand voice and content style
- Define target audience
- Choose default video preferences
- Upload brand guidelines
- Set visual style preferences

## Advanced Context Methods (Future Enhancements)

### 1. **Cross-Platform Context Fusion**
- Analyze multiple social profiles (Instagram + LinkedIn + TikTok)
- Build unified brand identity across platforms
- Identify platform-specific adaptations

### 2. **Temporal Context**
- Track content performance over time
- Seasonal content patterns
- Trending topic integration

### 3. **Audience Feedback Loop**
- Video engagement metrics
- Comment sentiment analysis
- Share/engagement patterns

### 4. **Competitive Intelligence**
- Analyze competitor content
- Identify differentiation opportunities
- Benchmark against industry standards

### 5. **Content Calendar Integration**
- Plan content themes in advance
- Avoid repetition
- Build narrative arcs

### 6. **A/B Testing Framework**
- Test different script styles
- Track performance metrics
- Optimize based on results

## Usage Examples

### Example 1: First-Time User
1. User uploads documents
2. System generates script (no context yet)
3. User approves/rejects script
4. System learns preferences
5. Next generation uses learned context

### Example 2: Returning User
1. User uploads new documents
2. System loads user context:
   - Brand voice: "Professional but friendly"
   - Successful topics: ["AI automation", "Productivity tips"]
   - Preferred duration: 20 seconds (Veo 3)
   - Content style: "Educational with storytelling"
3. AI generates script personalized to user's preferences
4. Script aligns with past successful content
5. User approves → Context updated

### Example 3: Multi-Platform User
1. User analyzes Instagram profile → Brand elements extracted
2. User analyzes LinkedIn profile → Professional voice identified
3. User uploads documents → Themes extracted
4. System fuses all contexts
5. Generates platform-appropriate content with unified brand voice

## Benefits

1. **Personalization**: Content matches user's brand and style
2. **Consistency**: Maintains brand voice across generations
3. **Efficiency**: Learns from past approvals/rejections
4. **Quality**: Better scripts through context-aware generation
5. **Scalability**: Context improves over time automatically

## Next Steps

1. Create frontend preferences UI component
2. Add authentication integration (get real user_id)
3. Implement cross-platform context fusion
4. Add performance metrics tracking
5. Build content calendar integration
6. Create context visualization dashboard

## Technical Notes

- Context stored in JSON files (can migrate to database)
- Context summary limited to ~2000 chars for AI prompts
- Automatic pattern analysis from behavioral data
- Privacy: User context is user-specific and isolated



















