# 🎥 Sora Video Generation - Usage Guide

## Quick Start

Your API key **now has access** to OpenAI's Sora video generation! Here's how to use it:

### 1. Start the Application

```bash
# Both servers should be running
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

### 2. Generate Videos

#### Single User Mode (≤3 videos):
1. Enter an Instagram username (e.g., `@welcome.ai`)
2. Set "Number of Videos" to 3 or fewer
3. Click "Generate Sora Scripts"
4. **Each analyzed video will get its own AI-generated video!**

#### Multi-User Mode (Fusion Video):
1. Switch to "Multi-User Fusion" tab
2. Enter 2-5 Instagram usernames
3. Choose "Fusion" or "Sequential" style
4. Click "Generate Sora Scripts"
5. **One combined fusion video will be generated from all styles**

### 3. Video Generation Process

The system automatically:
1. ✅ Scrapes Instagram videos
2. ✅ Transcribes audio with Whisper
3. ✅ Analyzes thumbnails with GPT-4 Vision
4. ✅ Generates structured Sora scripts
5. ✨ **Creates AI videos with Sora**
6. 📥 Provides download option (MP4)

### 4. What to Expect

**Generation Time:**
- `sora-2` (single videos): ~30-90 seconds
- `sora-2-pro` (fusion video): ~2-5 minutes

**Video Output:**
- Resolution: 1280x720 (720p)
- Duration: 8-10 seconds per video
- Format: MP4
- Quality: Production-ready

### 5. Monitoring Progress

The UI shows real-time status:
- 🟡 **Queued**: Video job is waiting
- 🔵 **In Progress**: AI is generating (shows progress %)
- 🟢 **Completed**: Video ready to play/download
- 🔴 **Failed**: Generation error (check API credits)

## Sora Models Used

### sora-2 (Fast Generation)
- **Used for:** Single video analysis (≤3 videos)
- **Speed:** Fast (~30-90 seconds)
- **Quality:** Good for social media
- **Cost:** Lower

### sora-2-pro (High Quality)
- **Used for:** Multi-user fusion videos
- **Speed:** Slower (~2-5 minutes)
- **Quality:** Production-grade
- **Cost:** Higher

## Example Workflow

```
1. User enters: @welcome.ai, 3 videos
   
2. System analyzes:
   - Video 1: "Generative AI Impact"
   - Video 2: "AI Guardrails"
   - Video 3: "AI Agent Capabilities"
   
3. Sora generates 3 videos:
   ✅ Video 1: 8-second clip about Gen AI (sora-2)
   ✅ Video 2: 8-second clip about safety (sora-2)
   ✅ Video 3: 8-second clip about agents (sora-2)
   
4. Each video appears with:
   - Video player (HTML5)
   - Download button
   - Job ID and model info
```

## API Costs

**Estimate** (check OpenAI pricing for exact costs):
- `sora-2`: ~$0.10-0.20 per 8-second video
- `sora-2-pro`: ~$0.30-0.50 per 8-second video

**Cost per analysis:**
- Single user (3 videos): ~$0.30-0.60
- Multi-user (2-5 users): ~$0.30-0.50 for fusion video

## Troubleshooting

### Videos Not Generating?

**Check your API credits:**
```bash
# Visit OpenAI Dashboard
https://platform.openai.com/usage
```

**Common issues:**
- ❌ Insufficient API credits → Add payment method
- ❌ Rate limit exceeded → Wait a few minutes
- ❌ API key invalid → Check .env file

### Videos Taking Too Long?

**Normal generation times:**
- sora-2: 30-90 seconds
- sora-2-pro: 2-5 minutes

**If longer than 10 minutes:**
- Check backend logs for errors
- Verify OpenAI API status
- Try again with fewer videos

## Advanced Features

### Content Restrictions

Sora enforces guardrails:
- ✅ Family-friendly content only (U18)
- ❌ No copyrighted characters/music
- ❌ No real people (including celebrities)
- ❌ No faces in input images

### Video Quality Tips

**For best results:**
1. Analyze high-engagement Instagram videos
2. Use clear, descriptive transcriptions
3. Let the Vision API capture visual style
4. Trust the Structured Outputs format

**The AI handles:**
- Camera angles and movements
- Color grading and lighting
- Scene composition
- Motion dynamics

## Next Steps

🎉 **You're ready to generate AI videos!**

1. Open http://localhost:3000
2. Enter an Instagram username
3. Watch the magic happen

The system will analyze real Instagram content and create brand-new AI-generated videos inspired by the original style, themes, and aesthetics.

---

**Questions?** Check the main README or backend logs for details.
