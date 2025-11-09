# X Video Hook Generator 🎬✨

An AI-powered full-stack application that analyzes top-performing X (Twitter) videos and generates compelling social media and marketing hooks using OpenAI's GPT-4 with Structured Outputs and Whisper API.

## 🚀 Features

- **X API Integration**: Fetches top videos from X accounts sorted by views
- **AI Transcription**: Uses OpenAI Whisper to transcribe video content
- **Structured Hook Generation**: Leverages GPT-4 with Structured Outputs for consistent, high-quality hooks
- **Dual Hook Types**: Generates both social media hooks (engagement-focused) and marketing hooks (conversion-focused)
- **Modern UI**: Clean React frontend with Tailwind CSS
- **Real-time Analysis**: Fast async processing with FastAPI backend

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OpenAI API** - Whisper (transcription) + GPT-4 (hook generation with Structured Outputs)
- **X API v2** - Fetch videos and user data
- **Pydantic** - Data validation and schema management

### Frontend
- **React 18** - UI library
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- X API Bearer Token ([Get here](https://developer.twitter.com/))
- OpenAI API Key ([Get here](https://platform.openai.com/))

## 🔧 Installation

### 1. Clone and Setup Backend

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env
```

Edit `backend/.env` and add your API keys:
```
X_BEARER_TOKEN=your_actual_x_bearer_token
OPENAI_API_KEY=your_actual_openai_api_key
```

### 2. Setup Frontend

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Option 1: Start Everything with One Command (Recommended)

```powershell
# Using npm script
npm start
```

Or using VS Code:
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Task"
- Select "Start All Servers"

### Option 2: Start Manually

**Backend (Terminal 1):**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

**Frontend (Terminal 2):**
```powershell
cd frontend
npm run dev
```

Both servers will be available at:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## 📖 Usage

1. Open `http://localhost:3000` in your browser
2. Enter an X username (with or without @)
3. Select number of videos to analyze (1-10)
4. Click "Generate Hooks"
5. View generated hooks, transcriptions, and video metrics

## 🎯 API Endpoints

### `POST /api/analyze`
Analyze videos from X account and generate hooks

**Request:**
```json
{
  "username": "elonmusk",
  "video_limit": 5
}
```

**Response:**
```json
{
  "username": "elonmusk",
  "videos_analyzed": 5,
  "results": [
    {
      "video_id": "123...",
      "video_url": "https://...",
      "views": 1000000,
      "transcription": "...",
      "hooks": [
        {
          "type": "social_media",
          "text": "You won't believe what happens next...",
          "platform": "TikTok",
          "reasoning": "Creates curiosity gap..."
        }
      ]
    }
  ]
}
```

### `GET /api/health`
Check API health and configuration status

## 🔑 OpenAI Structured Outputs

This project uses OpenAI's Structured Outputs feature to ensure consistent, validated responses. The `HookGenerationSchema` defines:

- **social_media_hooks**: 2-3 engagement-focused hooks
- **marketing_hooks**: 2-3 conversion-focused hooks
- **key_themes**: Main video themes
- **target_audience**: Identified audience

Benefits:
- ✅ Guaranteed JSON structure
- ✅ Type safety
- ✅ No parsing errors
- ✅ Consistent output format

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── x_api.py           # X API integration
│   │   └── openai_service.py  # OpenAI integration
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main component
│   │   ├── components/
│   │   │   ├── VideoCard.jsx
│   │   │   └── HookDisplay.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 🎨 Features Breakdown

### Hook Types

**Social Media Hooks:**
- Short, punchy, curiosity-driven
- Optimized for engagement
- Platform-specific recommendations

**Marketing Hooks:**
- Value-focused, benefit-driven
- Suitable for ads and campaigns
- Conversion-oriented messaging

## 🔮 Future Enhancements

- [ ] Sora v2 script generation
- [ ] Real-time API integration for live analysis
- [ ] Batch processing for multiple accounts
- [ ] Export hooks to CSV/JSON
- [ ] A/B testing recommendations
- [ ] Analytics dashboard

## 🐛 Troubleshooting

**Issue: X API Rate Limit**
- Solution: Wait for rate limit reset or use higher-tier API access

**Issue: OpenAI API Error**
- Solution: Check API key and account credits

**Issue: No videos found**
- Solution: Ensure username has public videos with high view counts

## 📝 License

MIT License - feel free to use this project for your own purposes!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using OpenAI Dev Hours technologies
