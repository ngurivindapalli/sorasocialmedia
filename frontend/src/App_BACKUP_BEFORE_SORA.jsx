import { useState } from 'react'
import { Video, Play, FileText, Loader2 } from 'lucide-react'
import axios from 'axios'
import './App.css'

function App() {
  const [mode, setMode] = useState('single') // 'single' or 'multi'
  const [username, setUsername] = useState('')
  const [videoLimit, setVideoLimit] = useState(3)
  const [multiUsernames, setMultiUsernames] = useState(['', ''])
  const [videosPerUser, setVideosPerUser] = useState(2)
  const [combineStyle, setCombineStyle] = useState('fusion')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (mode === 'single') {
      if (!username.trim()) {
        setError('Please enter an Instagram username')
        return
      }
    } else {
      const validUsernames = multiUsernames.filter(u => u.trim())
      if (validUsernames.length < 2) {
        setError('Please enter at least 2 Instagram usernames')
        return
      }
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      if (mode === 'single') {
        const response = await axios.post('http://localhost:8000/api/analyze', {
          username: username.trim().replace('@', ''),
          video_limit: videoLimit
        })
        setResults({ type: 'single', data: response.data })
      } else {
        const validUsernames = multiUsernames.filter(u => u.trim()).map(u => u.replace('@', ''))
        const response = await axios.post('http://localhost:8000/api/analyze/multi', {
          usernames: validUsernames,
          videos_per_user: videosPerUser,
          combine_style: combineStyle
        })
        setResults({ type: 'multi', data: response.data })
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze videos. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const addUsername = () => {
    if (multiUsernames.length < 5) {
      setMultiUsernames([...multiUsernames, ''])
    }
  }

  const removeUsername = (index) => {
    if (multiUsernames.length > 2) {
      setMultiUsernames(multiUsernames.filter((_, i) => i !== index))
    }
  }

  const updateUsername = (index, value) => {
    const updated = [...multiUsernames]
    updated[index] = value
    setMultiUsernames(updated)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Instagram → Sora Script</h1>
            <p className="text-gray-600 text-sm mt-1">Scrape Instagram videos, transcribe, and generate Sora AI prompts</p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Input Section */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Analyze Instagram Videos</h2>

          {/* Mode Toggle */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setMode('single')}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-colors ${
                mode === 'single' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              disabled={loading}
            >
              Single User
            </button>
            <button
              onClick={() => setMode('multi')}
              className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-colors ${
                mode === 'multi' 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
              disabled={loading}
            >
              Multi-User Fusion
            </button>
          </div>

          {mode === 'single' ? (
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instagram Username
                </label>
                <input
                  type="text"
                  placeholder="@username or username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-1">Public accounts only</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Videos
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={videoLimit}
                  onChange={(e) => setVideoLimit(parseInt(e.target.value))}
                  className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                />
                <p className="text-xs text-gray-500 mt-1">Analyzes top 3 videos by default</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Instagram Usernames (2-5 users)
                </label>
                {multiUsernames.map((user, index) => (
                  <div key={index} className="flex gap-2 mb-2">
                    <input
                      type="text"
                      placeholder={`@username ${index + 1}`}
                      value={user}
                      onChange={(e) => updateUsername(index, e.target.value)}
                      className="flex-1 px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={loading}
                    />
                    {multiUsernames.length > 2 && (
                      <button
                        onClick={() => removeUsername(index)}
                        className="px-4 py-3 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors"
                        disabled={loading}
                      >
                        Remove
                      </button>
                    )}
                  </div>
                ))}
                {multiUsernames.length < 5 && (
                  <button
                    onClick={addUsername}
                    className="mt-2 px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                    disabled={loading}
                  >
                    + Add Another User
                  </button>
                )}
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Videos Per User
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="5"
                    value={videosPerUser}
                    onChange={(e) => setVideosPerUser(parseInt(e.target.value))}
                    className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={loading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Combine Style
                  </label>
                  <select
                    value={combineStyle}
                    onChange={(e) => setCombineStyle(e.target.value)}
                    className="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={loading}
                  >
                    <option value="fusion">Fusion (Blend Styles)</option>
                    <option value="sequence">Sequential (Story Flow)</option>
                  </select>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-blue-700">
                  <strong>Multi-User Mode:</strong> Analyzes top videos from multiple creators and creates a combined Sora script that fuses their best elements together.
                </p>
              </div>
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}
        </div>

        {/* Results Section */}
        {results && results.type === 'single' && (
          <div className="space-y-6">
            {/* Scraped Videos */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-4">
                📹 Found Videos from @{results.data.username}
              </h3>
              <div className="grid gap-4">
                {results.data.scraped_videos.map((video, index) => (
                  <div key={video.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium text-blue-600">Video {index + 1}</span>
                      <a 
                        href={video.post_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        View on Instagram →
                      </a>
                    </div>
                    <p className="text-gray-700 text-sm mb-2">{video.text}</p>
                    <div className="flex gap-4 text-xs text-gray-600">
                      <span>👁️ {video.views.toLocaleString()} views</span>
                      <span>❤️ {video.likes.toLocaleString()} likes</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Analyzed Results */}
            {results.data.analyzed_videos.map((result, index) => (
              <div key={result.video_id} className="bg-white rounded-lg shadow-md p-8 border border-gray-200">
                <div className="flex items-center gap-2 mb-6">
                  <FileText className="w-6 h-6 text-blue-600" />
                  <h3 className="text-2xl font-bold text-gray-900">Video {index + 1} Analysis</h3>
                </div>

                {/* Vision API Analysis (if available) */}
                {result.thumbnail_analysis && (
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <span>👁️</span> Visual Analysis
                      <span className="ml-2 text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
                        Vision API
                      </span>
                    </h4>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="grid md:grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-blue-700 font-semibold">Colors: </span>
                          <span className="text-gray-700">{result.thumbnail_analysis.dominant_colors.join(', ')}</span>
                        </div>
                        <div>
                          <span className="text-blue-700 font-semibold">Composition: </span>
                          <span className="text-gray-700">{result.thumbnail_analysis.composition}</span>
                        </div>
                        <div className="md:col-span-2">
                          <span className="text-blue-700 font-semibold">Elements: </span>
                          <span className="text-gray-700">{result.thumbnail_analysis.visual_elements.join(', ')}</span>
                        </div>
                        <div className="md:col-span-2">
                          <span className="text-blue-700 font-semibold">Style: </span>
                          <span className="text-gray-700">{result.thumbnail_analysis.style_assessment}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Transcription */}
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <span>📝</span> Transcription
                  </h4>
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-wrap">
                      {result.transcription}
                    </p>
                  </div>
                </div>

                {/* Sora Script */}
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <span>🎬</span> Sora AI Script
                    {result.structured_sora_script && (
                      <span className="ml-2 text-xs bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
                        Structured Outputs
                      </span>
                    )}
                  </h4>
                  
                  {/* Show structured version if available, otherwise show regular */}
                  {result.structured_sora_script ? (
                    <div className="space-y-4">
                      {/* Core Concept */}
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                        <h5 className="text-sm font-bold text-purple-700 mb-2">🎯 Core Concept</h5>
                        <p className="text-gray-700 text-sm">{result.structured_sora_script.core_concept}</p>
                      </div>
                      
                      {/* Visual Style */}
                      <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                        <h5 className="text-sm font-bold text-pink-700 mb-2">🎨 Visual Style</h5>
                        <div className="space-y-2 text-sm">
                          <div>
                            <span className="text-gray-600">Colors: </span>
                            <span className="text-gray-800">{result.structured_sora_script.visual_style.primary_colors.join(', ')}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Lighting: </span>
                            <span className="text-gray-800">{result.structured_sora_script.visual_style.lighting}</span>
                          </div>
                          <div>
                            <span className="text-gray-600">Mood: </span>
                            <span className="text-gray-800">{result.structured_sora_script.visual_style.mood}</span>
                          </div>
                        </div>
                      </div>
                      
                      {/* Camera Work */}
                      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                        <h5 className="text-sm font-bold text-indigo-700 mb-2">🎥 Camera Work</h5>
                        <div className="grid grid-cols-3 gap-2 text-xs text-gray-700">
                          <div>
                            <span className="text-gray-600">Shots: </span>
                            {result.structured_sora_script.camera_work.shot_types.join(', ')}
                          </div>
                          <div>
                            <span className="text-gray-600">Movements: </span>
                            {result.structured_sora_script.camera_work.camera_movements.join(', ')}
                          </div>
                          <div>
                            <span className="text-gray-600">Angles: </span>
                            {result.structured_sora_script.camera_work.angles.join(', ')}
                          </div>
                        </div>
                      </div>
                      
                      {/* Full Prompt */}
                      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                        <h5 className="text-sm font-bold text-green-700 mb-2">✨ Complete Sora Prompt</h5>
                        <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                          {result.structured_sora_script.full_prompt}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                      <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                        {result.sora_script}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Multi-User Results */}
        {results && results.type === 'multi' && (
          <div className="space-y-6">
            {/* Combined Script Header */}
            <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg shadow-md p-6 border-2 border-purple-300">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                🎬 Combined Sora Script - Multi-Creator Fusion
              </h3>
              <p className="text-gray-700">
                Analyzed {results.data.total_videos_analyzed} videos from: {results.data.usernames.map(u => '@' + u).join(', ')}
              </p>
              <p className="text-sm text-gray-600 mt-2">{results.data.fusion_notes}</p>
            </div>

            {/* Combined Structured Script */}
            {results.data.combined_structured_script ? (
              <div className="bg-white rounded-lg shadow-md p-8 border border-gray-200">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">
                  ✨ Structured Combined Script
                </h4>
                <div className="space-y-4">
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <h5 className="text-sm font-bold text-purple-700 mb-2">🎯 Core Concept</h5>
                    <p className="text-gray-700 text-sm">{results.data.combined_structured_script.core_concept}</p>
                  </div>
                  
                  <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                    <h5 className="text-sm font-bold text-pink-700 mb-2">🎨 Visual Style</h5>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="text-gray-600">Colors: </span>
                        <span className="text-gray-800">{results.data.combined_structured_script.visual_style.primary_colors.join(', ')}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Lighting: </span>
                        <span className="text-gray-800">{results.data.combined_structured_script.visual_style.lighting}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Mood: </span>
                        <span className="text-gray-800">{results.data.combined_structured_script.visual_style.mood}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
                    <h5 className="text-sm font-bold text-indigo-700 mb-2">🎥 Camera Work</h5>
                    <div className="grid grid-cols-3 gap-2 text-xs text-gray-700">
                      <div>
                        <span className="text-gray-600">Shots: </span>
                        {results.data.combined_structured_script.camera_work.shot_types.join(', ')}
                      </div>
                      <div>
                        <span className="text-gray-600">Movements: </span>
                        {results.data.combined_structured_script.camera_work.camera_movements.join(', ')}
                      </div>
                      <div>
                        <span className="text-gray-600">Angles: </span>
                        {results.data.combined_structured_script.camera_work.angles.join(', ')}
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <h5 className="text-sm font-bold text-green-700 mb-2">✨ Complete Combined Prompt</h5>
                    <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                      {results.data.combined_structured_script.full_prompt}
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-8 border border-gray-200">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">
                  🎬 Combined Sora Script
                </h4>
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <p className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                    {results.data.combined_sora_script}
                  </p>
                </div>
              </div>
            )}

            {/* Individual Videos Summary */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">
                📊 Individual Videos Analyzed
              </h4>
              <div className="grid gap-4">
                {results.data.individual_results.map((result, index) => (
                  <div key={result.video_id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-sm font-medium text-blue-600">Video {index + 1}</span>
                      <a 
                        href={result.post_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        View on Instagram →
                      </a>
                    </div>
                    <p className="text-gray-700 text-sm mb-2">{result.original_text.substring(0, 100)}...</p>
                    <div className="flex gap-4 text-xs text-gray-600">
                      <span>👁️ {result.views.toLocaleString()} views</span>
                      <span>❤️ {result.likes.toLocaleString()} likes</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
