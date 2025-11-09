import { useState } from 'react'
import { Video, Sparkles, TrendingUp, Loader2 } from 'lucide-react'
import axios from 'axios'
import './App.css'
import VideoCard from './components/VideoCard'
import HookDisplay from './components/HookDisplay'

function App() {
  const [username, setUsername] = useState('')
  const [videoLimit, setVideoLimit] = useState(5)
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!username.trim()) {
      setError('Please enter a username')
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
      setError(err.response?.data?.detail || 'Failed to analyze videos. Please check your credentials and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Header */}
      <header className="bg-black/30 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-2 rounded-lg">
              <Video className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white">X Video Hook Generator</h1>
              <p className="text-gray-400 text-sm">AI-powered hook generation from top X videos</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Input Section */}
        <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 mb-8 border border-white/20">
          <div className="flex items-center gap-2 mb-6">
            <Sparkles className="w-6 h-6 text-yellow-400" />
            <h2 className="text-2xl font-bold text-white">Analyze X Account</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                X Username
              </label>
              <input
                type="text"
                placeholder="@username or username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Number of Videos
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={videoLimit}
                onChange={(e) => setVideoLimit(parseInt(e.target.value))}
                className="w-full px-4 py-3 bg-white/5 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-lg transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing Videos...
              </>
            ) : (
              <>
                <TrendingUp className="w-5 h-5" />
                Generate Hooks
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
            <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-2">
                Analysis Complete for @{results.username}
              </h3>
              <p className="text-gray-300">
                Analyzed {results.videos_analyzed} video{results.videos_analyzed !== 1 ? 's' : ''}
              </p>
            </div>

            {results.results.map((video, index) => (
              <div key={video.video_id} className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
                <VideoCard video={video} index={index} />
                <HookDisplay hooks={video.hooks} />
                
                {/* Transcription */}
                <div className="mt-6">
                  <h4 className="text-lg font-semibold text-white mb-3">Transcription</h4>
                  <div className="bg-black/30 rounded-lg p-4 border border-white/10">
                    <p className="text-gray-300 text-sm leading-relaxed">
                      {video.transcription}
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
