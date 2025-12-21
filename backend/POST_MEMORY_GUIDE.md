# Post Memory System with Hyperspell

## Overview

The marketing post system now uses Hyperspell memory to:
1. **Remember every post** created for each user
2. **Track post performance** (views, likes, engagement)
3. **Learn from successful posts** to improve future content
4. **Automatically create intro posts** for new users

## How It Works

### First Post (Intro Post)

When a user creates their **first marketing post**, the system automatically:
- Detects it's the first post by checking Hyperspell memory
- Retrieves company context from uploaded documents
- Generates an **introductory post** about the company instead of the requested topic
- Creates a welcoming post that introduces the company, mission, and values
- Sets the foundation for the brand voice

**Example:**
- User requests: "New product launch"
- System detects: First post
- System generates: "Welcome! We're [Company Name], and we're excited to share our story..."

### Post Generation with Memory

For all posts (including first post), the system:

1. **Retrieves Context:**
   - Company information from uploaded documents
   - Previous posts and their performance data
   - High-performing post patterns
   - Low-performing post patterns

2. **Generates Content:**
   - Uses company context to personalize the caption
   - Learns from high-performing posts (topics, styles, hashtags)
   - Avoids approaches that didn't work well
   - Creates content that aligns with successful patterns

3. **Saves to Memory:**
   - Saves complete post data to Hyperspell
   - Includes: topic, caption, hashtags, image prompt, timestamp
   - Marks first post for future reference
   - Stores performance metrics (when available)

### Performance Tracking

After a post is published, you can update its performance metrics:

**Endpoint:** `POST /api/marketing-post/update-performance`

**Parameters:**
- `post_id`: The post identifier
- `views`: Number of views
- `likes`: Number of likes
- `comments`: Number of comments
- `shares`: Number of shares

**Example:**
```bash
curl -X POST "http://localhost:8000/api/marketing-post/update-performance" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "post_id=abc123" \
  -F "views=1500" \
  -F "likes=120" \
  -F "comments=15" \
  -F "shares=8"
```

The system will:
- Calculate engagement rate automatically
- Save performance data to Hyperspell
- Use this data to inform future post generation

### Post Suggestions

The suggestions endpoint (`GET /api/marketing-post/suggestions`) now:
- Uses post performance data to suggest topics
- Prioritizes topics similar to high-performing posts
- Avoids topics similar to low-performing posts
- Learns from successful hashtags and styles

## Data Structure

Each post is saved to Hyperspell with this structure:

```json
{
  "type": "marketing_post",
  "user_id": "user@example.com",
  "topic": "Post topic",
  "caption": "Post caption text",
  "hashtags": ["tag1", "tag2"],
  "image_prompt": "Image generation prompt",
  "created_at": "2024-01-15T10:30:00",
  "post_id": "platform_post_id",
  "post_url": "https://instagram.com/p/...",
  "is_first_post": false,
  "performance": {
    "views": 1500,
    "likes": 120,
    "comments": 15,
    "shares": 8,
    "engagement_rate": 0.095
  },
  "caption_style": "engaging",
  "aspect_ratio": "1:1"
}
```

## Performance Analysis

The system automatically analyzes post performance:

**High-Performing Posts:**
- Engagement rate > 5% OR
- Views > 1000 AND likes > 50

**Low-Performing Posts:**
- Engagement rate < 1% OR
- Views < 100 AND likes < 5

Future posts will:
- Mimic successful topics, styles, and hashtags
- Avoid approaches from low-performing posts
- Build on what works for each specific user

## API Endpoints

### Create Post
`POST /api/marketing-post/create`

**Features:**
- Automatically detects first post
- Uses company context for personalization
- Learns from previous post performance
- Saves post to Hyperspell memory

**Response includes:**
- `is_first_post`: Boolean indicating if this was the first post
- All standard post data (image, caption, hashtags)

### Update Performance
`POST /api/marketing-post/update-performance`

**Purpose:**
- Track post engagement metrics
- Enable learning from performance data
- Improve future post suggestions

### Get Suggestions
`GET /api/marketing-post/suggestions`

**Features:**
- Uses post performance data
- Suggests topics based on what worked
- Personalized to user's brand and context

## Implementation Details

### Files

- `backend/utils/post_memory_helper.py`: Core helper functions
  - `save_post_to_memory()`: Save posts to Hyperspell
  - `get_post_history_from_memory()`: Retrieve post history
  - `is_first_post()`: Check if first post
  - `get_post_performance_context()`: Get performance insights

- `backend/main.py`: API endpoints
  - `/api/marketing-post/create`: Enhanced with memory
  - `/api/marketing-post/update-performance`: New endpoint
  - `/api/marketing-post/suggestions`: Enhanced with performance data

### Hyperspell Collections

- `user_posts`: Stores all marketing posts
- `post_performance`: Stores performance updates

## Usage Flow

1. **User creates first post:**
   - System detects first post
   - Generates intro post about company
   - Saves to Hyperspell

2. **User creates subsequent posts:**
   - System retrieves previous posts and performance
   - Generates content using successful patterns
   - Saves new post to Hyperspell

3. **User updates performance:**
   - Posts engagement metrics
   - System saves performance data
   - Future posts learn from this data

4. **User requests suggestions:**
   - System analyzes all posts and performance
   - Suggests topics based on what worked
   - Prioritizes high-performing patterns

## Benefits

1. **Personalized Content:** Each user's posts improve over time
2. **Data-Driven:** Decisions based on actual performance data
3. **Automatic Learning:** System learns what works for each user
4. **Consistent Brand Voice:** First post sets the foundation
5. **Continuous Improvement:** Each post builds on previous success

## Requirements

- Hyperspell service must be configured
- User must be authenticated
- Company context should be uploaded to Hyperspell for best results



