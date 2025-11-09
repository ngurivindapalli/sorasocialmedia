import { useState } from 'react'
import { Video, Play, FileText, Loader2 } from 'lucide-react'
import axios from 'axios'
import './App.css'

function App() {
  const [username, setUsername] = useState('')
  const [videoLimit, setVideoLimit] = useState(1)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!username.trim()) {
      setError('Please enter an Instagram username')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await axios.post('http://localhost:8000/api/analyze', {
        username: username.trim().replace('@', ''),
        video_limit: videoLimit
      })
      
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze videos. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-pink-800 to-orange-700">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-2 rounded-lg">
              <Video className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">📷 Instagram → Sora Script</h1>
              <p className="text-gray-200 text-sm">Scrape Instagram videos, transcribe, and generate Sora AI prompts</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Input Section */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 mb-8 border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-6">Analyze Instagram Videos</h2>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-200 mb-2">
                Instagram Username
              </label>
              <input
                type="text"
                placeholder="@username or username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-500"
                disabled={loading}
              />
              <p className="text-xs text-gray-300 mt-1">Public accounts only</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-200 mb-2">
                Number of Videos
              </label>
              <input
                type="number"
                min="1"
                max="3"
                value={videoLimit}
                onChange={(e) => setVideoLimit(parseInt(e.target.value))}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500"
                disabled={loading}
              />
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-4 px-6 rounded-lg transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing Videos...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Generate Sora Scripts
              </>
            )}
          </button>

          {error && (
            <div className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {results && (
          <div className="space-y-6">
            {/* Scraped Videos */}
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">
                📹 Found Videos from @{results.username}
              </h3>
              <div className="grid gap-4">
                {results.scraped_videos.map((video, index) => (
                  <div key={video.id} className="bg-black/30 rounded-lg p-4 border border-white/10">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium text-pink-400">Video {index + 1}</span>
                      <a 
                        href={video.post_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-purple-300 hover:text-purple-200"
                      >
                        View on Instagram →
                      </a>
                    </div>
                    <p className="text-gray-200 text-sm mb-2">{video.text}</p>
                    <div className="flex gap-4 text-xs text-gray-300">
                      <span>👁️ {video.views.toLocaleString()} views</span>
                      <span>❤️ {video.likes.toLocaleString()} likes</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Analyzed Results */}
            {results.analyzed_videos.map((result, index) => (
              <div key={result.video_id} className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
                <div className="flex items-center gap-2 mb-6">
                  <FileText className="w-6 h-6 text-green-400" />
                  <h3 className="text-2xl font-bold text-white">Video {index + 1} Analysis</h3>
                </div>

                {/* Transcription */}
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <span>📝</span> Transcription
                  </h4>
                  <div className="bg-black/30 rounded-lg p-4 border border-white/10">
                    <p className="text-gray-200 text-sm leading-relaxed whitespace-pre-wrap">
                      {result.transcription}
                    </p>
                  </div>
                </div>

                {/* Sora Script */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                    <span>🎬</span> Sora AI Script
                  </h4>
                  <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-lg p-6 border border-pink-500/30">
                    <p className="text-gray-100 text-sm leading-relaxed whitespace-pre-wrap">
                      {result.sora_script}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
