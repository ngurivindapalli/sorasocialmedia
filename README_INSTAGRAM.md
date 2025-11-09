# Instagram to Sora Script Generator 🎬✨

Full-stack AI application that analyzes Instagram videos and generates Sora AI video prompts using OpenAI's Build Hours features.

## 🚀 Features

### Core Functionality
- **Instagram Video Scraping**: Automatically fetches top videos from public Instagram accounts
- **Whisper Transcription**: Converts video audio to text using OpenAI Whisper API
- **Sora Script Generation**: Creates detailed AI video generation prompts

### OpenAI Build Hours Features
- ✅ **Structured Outputs**: Guaranteed consistent JSON schemas for Sora prompts
- ✅ **Vision API**: GPT-4 Vision analyzes thumbnails for visual context
- ⚠️ **Batch API**: Process multiple videos at 50% cost savings (ready but not active)
- ⚠️ **Fine-Tuning**: Infrastructure ready for custom model training

### Advanced Modes
- **Single User Mode**: Analyze top 3 videos from one creator
- **Multi-User Fusion**: Combine 2-5 creators' styles into one unified Sora prompt

## 🛠 Tech Stack
- **Backend**: Python 3.12, FastAPI, Uvicorn
- **Frontend**: React 18 + Vite, Tailwind CSS
- **APIs**: Instagram (instaloader), OpenAI (Whisper, GPT-4o, Vision)
- **Model**: gpt-4o-2024-08-06 (Structured Outputs compatible)

## 📦 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenAI API key

### Backend Setup
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Frontend Setup
```bash
cd frontend
npm install
```

## 🚀 Running the Application

### Start Backend (Port 8000)
```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
python main.py
```

### Start Frontend (Port 3000)
```bash
cd frontend
npm run dev
```

Visit: `http://localhost:3000`

## 📖 Usage

### Single User Mode
1. Enter an Instagram username
2. Set number of videos (default: 3, max: 10)
3. Click "Generate Sora Scripts"
4. View transcriptions and AI-generated Sora prompts with structured outputs

### Multi-User Fusion Mode
1. Switch to "Multi-User Fusion" tab
2. Add 2-5 Instagram usernames
3. Choose videos per user (default: 2)
4. Select fusion style:
   - **Fusion**: Blend all styles into one cohesive concept
   - **Sequential**: Create a story flowing through each creator's style
5. Get a combined Sora script blending the best elements

## 🔑 Environment Variables

Create `backend/.env`:
```bash
OPENAI_API_KEY=sk-proj-your_key_here
```

## 📁 Project Structure
```
/backend
  - main.py              # FastAPI application with all endpoints
  - services/
    - instagram_api.py   # Instagram scraping with instaloader
    - openai_service.py  # OpenAI integrations (Whisper, GPT-4, Vision)
  - models/
    - schemas.py         # Pydantic models with strict validation
  - requirements.txt
  - .env.example

/frontend
  - src/
    - App.jsx            # Main React component with mode switching
    - components/        # Reusable UI components
  - package.json
```

## 🎓 OpenAI Build Hours Features Explained

### 1. Structured Outputs ✅
Forces GPT-4 to return JSON matching exact Pydantic schemas. No more parsing errors!

**Implementation:**
```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "sora_script",
        "strict": True,
        "schema": StructuredSoraScript.model_json_schema()
    }
}
```

**Key Fix:** All Pydantic models need `model_config = {"extra": "forbid"}` for strict validation.

**Schema Structure:**
- `core_concept`: Main video concept
- `visual_style`: Colors, lighting, mood, references
- `camera_work`: Shot types, movements, angles
- `timing`: Duration, pacing, key moments
- `full_prompt`: Complete Sora-ready prompt

### 2. Vision API ✅
Analyzes video thumbnails for visual context before generating scripts.

**Implementation:**
```python
# Downloads thumbnail as base64 (Instagram CDN auth workaround)
analysis = await openai_service.analyze_thumbnail_with_vision(thumbnail_url)
```

**Provides:**
- Dominant colors
- Composition analysis
- Visual elements
- Style assessment

### 3. Batch API ⚠️ (Ready)
Process multiple videos at 50% cost savings with 24-hour turnaround.

**Endpoints Created:**
- `POST /api/batch/create` - Submit batch job
- `GET /api/batch/status/{id}` - Check progress
- `GET /api/batch/results/{id}` - Get results

### 4. Fine-Tuning ⚠️ (Ready)
Infrastructure for training custom models on your data.

**Endpoints Created:**
- `POST /api/finetune/create` - Create training job
- `GET /api/finetune/list` - List jobs
- `GET /api/finetune/status/{id}` - Check status

## 🔒 Security
- Never commit `.env` files
- API keys stored in environment variables only
- `.gitignore` configured to exclude sensitive files
- GitHub push protection enabled

## 🐛 Common Issues

**Instagram Rate Limiting:**
- Returns videos found before rate limit
- Uses browser-like headers and delays to avoid blocking

**Low Quality Transcription:**
- System detects gibberish/repetitive transcriptions
- Falls back to caption and metrics only

**Vision API Errors:**
- Downloads thumbnails as base64 to bypass Instagram CDN auth
- Gracefully skips Vision analysis if it fails

## 📊 API Endpoints

### `POST /api/analyze`
Single user analysis with top N videos

### `POST /api/analyze/multi`
Multi-user fusion mode combining multiple creators

### `GET /api/health`
Check API status and configured features

### Batch & Fine-Tuning Endpoints
See code for full list of available endpoints

## 🎯 Use Cases
- Content creators studying viral Instagram videos
- Marketing teams analyzing competitor content
- AI video production planning
- Social media strategy research
- Creator style analysis and fusion

## 📝 License
MIT

## 🤝 Contributing
Pull requests welcome! Ensure all API keys use environment variables.

---

Built with OpenAI Build Hours technologies: Structured Outputs + Vision API
