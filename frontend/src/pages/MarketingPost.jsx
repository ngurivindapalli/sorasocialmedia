import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Image, Download, Copy, FileText, Loader2, CheckCircle2, XCircle, Hash, LogIn, UserPlus, LogOut, Lightbulb, X, Info, Instagram, Linkedin, ExternalLink } from 'lucide-react'
import { api, API_URL } from '../utils/api'
import { authUtils } from '../utils/auth'
import LoadingOverlay from '../components/LoadingOverlay'

function MarketingPost() {
  const navigate = useNavigate()
  const [topic, setTopic] = useState('')
  const [platform, setPlatform] = useState('linkedin') // Default to LinkedIn
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [copied, setCopied] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [postingToLinkedIn, setPostingToLinkedIn] = useState(false)
  const [postSuccess, setPostSuccess] = useState(null)
  
  // Get current user from localStorage
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('videohook_current_user') || 'null')
    } catch {
      return null
    }
  })
  const isLoggedIn = !!currentUser

  // Refresh user state when component mounts or when returning from login/signup
  useEffect(() => {
    const user = authUtils.getCurrentUser()
    setCurrentUser(user)
  }, [])

  // Listen for storage changes (when user logs in from another tab/window)
  useEffect(() => {
    const handleStorageChange = () => {
      const user = authUtils.getCurrentUser()
      setCurrentUser(user)
    }
    
    window.addEventListener('storage', handleStorageChange)
    return () => window.removeEventListener('storage', handleStorageChange)
  }, [])

  const handleLogout = () => {
    authUtils.logout()
    setCurrentUser(null)
    setResult(null) // Clear results when logging out
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    setCopied(false)

    try {
      // Image generation can take 15-30 seconds, so use longer timeout
      const response = await api.post('/api/marketing-post/create', {
        topic,
        caption_style: 'engaging', // Default style
        aspect_ratio: '1:1', // Default square format
        include_hashtags: true, // Always include hashtags
        platform: platform, // Instagram or LinkedIn
        post_to_instagram: false, // Manual posting for now
      }, {
        timeout: 60000 // 60 second timeout for image generation
      })

      setResult(response.data)
      console.log('Marketing post generated:', response.data)
    } catch (err) {
      console.error('Error generating marketing post:', err)
      
      // Extract error message properly - handle Pydantic validation errors
      let errorMessage = 'Failed to generate marketing post'
      
      if (err.response?.data) {
        const errorData = err.response.data
        
        // Handle Pydantic validation errors (array of errors)
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
        }
        // Handle string error messages
        else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        }
        // Handle object error messages
        else if (errorData.detail && typeof errorData.detail === 'object') {
          errorMessage = errorData.detail.msg || errorData.detail.message || JSON.stringify(errorData.detail)
        }
        // Fallback to message field
        else if (errorData.message) {
          errorMessage = errorData.message
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleGetSuggestions = async () => {
    setLoadingSuggestions(true)
    setError(null)
    try {
      const response = await api.get('/api/marketing-post/suggestions', {
        params: { count: 5 },
        timeout: 60000 // 60 second timeout for suggestions (Hyperspell queries can take time)
      })
      setSuggestions(response.data.suggestions || [])
      setShowSuggestions(true)
    } catch (err) {
      console.error('Error getting suggestions:', err)
      let errorMessage = 'Failed to get suggestions'
      
      if (err.response) {
        // Server responded with error
        if (err.response.status === 404) {
          errorMessage = 'Suggestions endpoint not found. Please make sure the backend server is running and has been restarted.'
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail
        } else if (err.response.data?.message) {
          errorMessage = err.response.data.message
        } else {
          errorMessage = `Server error: ${err.response.status} ${err.response.statusText}`
        }
      } else if (err.request) {
        // Request made but no response
        errorMessage = 'No response from server. Please make sure the backend server is running on http://localhost:8000'
      } else {
        // Error setting up request
        errorMessage = err.message || 'Failed to get suggestions'
      }
      
      setError(errorMessage)
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const handleSelectSuggestion = (suggestion) => {
    setTopic(suggestion.topic)
    setShowSuggestions(false)
  }

  const handleCopyCaption = () => {
    if (result?.full_caption) {
      navigator.clipboard.writeText(result.full_caption)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleDownloadImage = async () => {
    if (result?.image_base64) {
      // Convert base64 to blob and download
      const byteCharacters = atob(result.image_base64)
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const blob = new Blob([byteArray], { type: 'image/png' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `marketing-post-${Date.now()}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } else if (result?.image_url) {
      // Download from URL - handle both static files and API URLs
      const imageUrl = result.image_url.startsWith('/static-posts/') 
        ? result.image_url  // Static file, use as-is
        : result.image_url.startsWith('http')
          ? result.image_url  // Full URL
          : `${API_URL}${result.image_url}`  // API endpoint
      
      try {
        // Fetch the image and create a blob for download
        const response = await fetch(imageUrl)
        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `marketing-post-${Date.now()}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Error downloading image:', error)
        // Fallback: try direct link
        const link = document.createElement('a')
        link.href = imageUrl
        link.download = `marketing-post-${Date.now()}.png`
        link.target = '_blank'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    }
  }

  const handlePostToLinkedIn = async () => {
    if (!result?.image_base64 && !result?.image_url) {
      setError('No image available to post. Please generate content first.')
      return
    }

    setPostingToLinkedIn(true)
    setError(null)
    setPostSuccess(null)

    try {
      const postData = {
        caption: result.full_caption || result.caption || '',
        image_base64: result.image_base64 || null,
        image_url: result.image_url || null
      }

      const response = await api.post('/api/post/linkedin/company', postData, {
        timeout: 60000 // 60 second timeout
      })
      
      if (response.data.success) {
        setPostSuccess(response.data.post_url || 'Posted to AIGIS company page successfully!')
      } else {
        setError(response.data.error || 'Failed to post to LinkedIn company page')
      }
    } catch (err) {
      console.error('Error posting to LinkedIn:', err)
      setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Failed to post to LinkedIn company page.')
    } finally {
      setPostingToLinkedIn(false)
    }
  }

  return (
    <div className="min-h-screen bg-white p-6 relative">
      {/* Loading Overlay for Image Generation */}
      <LoadingOverlay 
        isLoading={loading} 
        type="image" 
        message="Creating your marketing post..."
        subMessage="Our AI is generating a custom image and crafting the perfect caption. This typically takes 15-30 seconds."
        fullScreen={true}
      />
      
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-[#1e293b]" />
              <h1 className="text-4xl font-bold text-[#111827]">Marketing Post Generator</h1>
            </div>
            
            {/* Auth Buttons */}
            <div className="flex items-center gap-3">
              {isLoggedIn ? (
                <>
                  <div className="flex items-center gap-2 px-4 py-2 bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg">
                    <span className="text-sm font-medium text-[#111827]">
                      {currentUser?.username || 'User'}
                    </span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-all"
                    style={{ boxShadow: '0 0 0 rgba(255, 255, 255, 0)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = '0 0 10px rgba(255, 255, 255, 0.1)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = '0 0 0 rgba(255, 255, 255, 0)'
                    }}
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm font-medium">Logout</span>
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => navigate(`/login?from=${encodeURIComponent('/dashboard')}`)}
                    className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-[#f5f5f5] text-[#111827] border border-[#e5e7eb] rounded-lg transition-all"
                    style={{ boxShadow: '0 0 0 rgba(255, 255, 255, 0)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = '0 0 15px rgba(255, 255, 255, 0.3)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = '0 0 0 rgba(255, 255, 255, 0)'
                    }}
                  >
                    <LogIn className="w-4 h-4" />
                    <span className="text-sm font-medium">Login</span>
                  </button>
                  <button
                    onClick={() => navigate(`/signup?from=${encodeURIComponent('/dashboard')}`)}
                    className="flex items-center gap-2 px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-all"
                    style={{ boxShadow: '0 0 0 rgba(255, 255, 255, 0)' }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.boxShadow = '0 0 15px rgba(255, 255, 255, 0.2)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = '0 0 0 rgba(255, 255, 255, 0)'
                    }}
                  >
                    <UserPlus className="w-4 h-4" />
                    <span className="text-sm font-medium">Sign Up</span>
                  </button>
                </>
              )}
            </div>
          </div>
          <p className="text-[#4b5563] text-lg">
            Generate professional marketing content with AI-powered image creation
          </p>
        </div>

        {/* Info Banner */}
        {!isLoggedIn && (
          <div className="mb-6 bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg p-4 flex items-start gap-3">
            <Info className="w-5 h-5 text-[#1e293b] flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-[#1e293b]">Brand Personalization Available</p>
              <p className="text-xs text-[#4b5563] mt-1">
                Sign up to enable personalized content generation based on your brand guidelines and context.
              </p>
            </div>
          </div>
        )}

        {isLoggedIn && (
          <div className="mb-6 bg-[#1e293b] border border-[#1e293b] rounded-lg p-4 flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-white flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-white">Brand Personalization Active</p>
              <p className="text-xs text-white/70 mt-1">
                Content is automatically personalized based on your brand context and uploaded documents.
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Simple Form */}
          <div className="bg-white border border-[#e5e7eb] rounded-xl p-6 shadow-sm">
            <form onSubmit={handleGenerate} className="space-y-6">
              {/* Topic - Only Required Field */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-semibold text-[#111827]">
                    What do you want to post about? *
                  </label>
                  <button
                    type="button"
                    onClick={handleGetSuggestions}
                    disabled={loadingSuggestions}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    style={{ boxShadow: '0 0 0 rgba(255, 255, 255, 0)' }}
                    onMouseEnter={(e) => {
                      if (!loadingSuggestions) {
                        e.currentTarget.style.boxShadow = '0 0 10px rgba(255, 255, 255, 0.1)'
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.boxShadow = '0 0 0 rgba(255, 255, 255, 0)'
                    }}
                  >
                    {loadingSuggestions ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Loading...
                      </>
                    ) : (
                      <>
                        <Lightbulb className="w-4 h-4" />
                        Give me suggestions
                      </>
                    )}
                  </button>
                </div>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g., AI-powered productivity tools, Sustainable fashion, Tech startup launch"
                  className="w-full px-4 py-3 bg-white border border-[#e5e7eb] rounded-lg focus:ring-2 focus:ring-[#1e293b] focus:border-[#1e293b] text-lg text-[#111827] placeholder-[#9ca3af]"
                  required
                />
                <p className="mt-2 text-sm text-[#4b5563]">
                  {isLoggedIn 
                    ? "Content will be automatically personalized based on your brand context and uploaded documents."
                    : "Use the suggestions feature to explore topic ideas, or sign up to enable brand personalization for your posts."}
                </p>
              </div>

              {/* Suggestions Display */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Lightbulb className="w-5 h-5 text-[#1e293b]" />
                      <h3 className="text-sm font-semibold text-[#111827]">AI Suggestions</h3>
                    </div>
                    <button
                      type="button"
                      onClick={() => setShowSuggestions(false)}
                      className="text-[#4b5563] hover:text-[#111827] transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="space-y-2">
                    {suggestions.map((suggestion, idx) => (
                      <div
                        key={idx}
                        className="bg-white border border-[#e5e7eb] rounded-lg p-3 hover:border-[#1e293b] transition-all cursor-pointer group"
                        onClick={() => handleSelectSuggestion(suggestion)}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="text-sm font-medium text-[#111827] group-hover:text-[#1e293b] transition-colors">
                                {suggestion.topic}
                              </p>
                              {suggestion.score && (
                                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                                  suggestion.score >= 80 ? 'bg-green-500 text-white' :
                                  suggestion.score >= 60 ? 'bg-yellow-500 text-black' :
                                  'bg-gray-500 text-white'
                                }`}>
                                  {suggestion.score}/100
                                </span>
                              )}
                            </div>
                            {suggestion.context && (
                              <p className="text-xs text-[#4b5563] mt-1">
                                {suggestion.context}
                              </p>
                            )}
                            {suggestion.reasoning && (
                              <p className="text-xs text-[#6b7280] mt-1 italic">
                                {suggestion.reasoning}
                              </p>
                            )}
                            {suggestion.source && (
                              <p className="text-xs text-[#9ca3af] mt-1">
                                Source: {suggestion.source === 'linkedin_scored' ? 'High-scoring LinkedIn post' : 'AI Generated'}
                              </p>
                            )}
                          </div>
                          <FileText className="w-4 h-4 text-[#1e293b] opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 mt-0.5" />
                        </div>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-[#6b7280] mt-3 text-center">
                    Click a suggestion to use it, or enter your own topic above
                  </p>
                </div>
              )}

              {/* Platform Selection */}
              <div>
                <label className="block text-sm font-semibold text-[#111827] mb-2">
                  Platform
                </label>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setPlatform('instagram')}
                    className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                      platform === 'instagram'
                        ? 'bg-[#1e293b] text-white border-[#1e293b]'
                        : 'bg-white text-[#4b5563] border-[#e5e7eb] hover:border-[#1e293b]'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2">
                      <Instagram className="w-5 h-5" />
                      <span className="font-medium">Instagram</span>
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => setPlatform('linkedin')}
                    className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all ${
                      platform === 'linkedin'
                        ? 'bg-[#1e293b] text-white border-[#1e293b]'
                        : 'bg-white text-[#4b5563] border-[#e5e7eb] hover:border-[#1e293b]'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-2">
                      <Linkedin className="w-5 h-5" />
                      <span className="font-medium">LinkedIn</span>
                    </div>
                  </button>
                </div>
                <p className="mt-2 text-xs text-[#4b5563]">
                  {platform === 'instagram' 
                    ? 'Instagram uses 10-20 hashtags for maximum reach'
                    : 'LinkedIn uses 3-5 professional hashtags'}
                </p>
              </div>

              {/* Generate Button */}
              <button
                type="submit"
                disabled={loading || !topic.trim()}
                className="w-full bg-[#1e293b] hover:bg-[#334155] text-white font-semibold py-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    Generate Marketing Post
                  </>
                )}
              </button>
            </form>

            {/* Error Display */}
            {error && (
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-red-600">Error</p>
                  <p className="text-sm text-red-700">{typeof error === 'string' ? error : JSON.stringify(error)}</p>
                </div>
              </div>
            )}
          </div>

          {/* Right Column: Results */}
          <div className="bg-white border border-[#e5e7eb] rounded-xl p-6 shadow-sm">
            {result ? (
              <div className="space-y-6">
                {/* Success Message */}
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="font-semibold">Post Generated Successfully!</span>
                </div>

                {/* Generated Image */}
                <div className="relative">
                  <div className="bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg overflow-hidden aspect-square flex items-center justify-center">
                    {result.image_url || result.image_base64 ? (
                      <img
                        src={
                          result.image_base64 
                            ? `data:image/png;base64,${result.image_base64}`
                            : result.image_url?.startsWith('http') 
                              ? result.image_url 
                              : result.image_url?.startsWith('/static-posts/')
                                ? result.image_url  // Static files served from frontend, no API_URL needed
                                : `${API_URL}${result.image_url}`
                        }
                        alt="Generated marketing post"
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Image className="w-16 h-16 text-gray-400" />
                    )}
                  </div>
                  <div className="mt-3 space-y-2">
                    <button
                      onClick={handleDownloadImage}
                      className="w-full bg-[#1e293b] hover:bg-[#334155] text-white py-2 rounded-lg transition-all flex items-center justify-center gap-2"
                    >
                      <Download className="w-4 h-4" />
                      Download Image
                    </button>
                    
                    {/* Post to LinkedIn Company Page */}
                    {platform === 'linkedin' && (result.image_url || result.image_base64) && (
                      <button
                        onClick={handlePostToLinkedIn}
                        disabled={postingToLinkedIn}
                        className="w-full bg-[#0077b5] hover:bg-[#005885] text-white py-2 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {postingToLinkedIn ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Posting to LinkedIn...
                          </>
                        ) : (
                          <>
                            <Linkedin className="w-4 h-4" />
                            Post to AIGIS Company Page
                          </>
                        )}
                      </button>
                    )}
                    
                    {/* Post Success Message */}
                    {postSuccess && (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
                        <p className="font-medium flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4" />
                          Posted to LinkedIn successfully!
                        </p>
                        {postSuccess.startsWith('http') && (
                          <a 
                            href={postSuccess} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-green-800 underline hover:no-underline mt-1 flex items-center gap-1"
                          >
                            <ExternalLink className="w-3 h-3" />
                            View Post on LinkedIn
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Image Prompt Used */}
                {result.image_prompt && (
                  <div className="bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg p-4">
                    <p className="text-xs font-semibold text-[#4b5563] mb-1">Image Prompt Used:</p>
                    <p className="text-sm text-[#111827]">{result.image_prompt}</p>
                  </div>
                )}

                {/* Caption */}
                <div className="bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-sm font-semibold text-[#111827]">Marketing Caption</p>
                    <button
                      onClick={handleCopyCaption}
                      className="text-xs text-[#1e293b] hover:text-[#334155] flex items-center gap-1 transition-colors"
                    >
                      {copied ? (
                        <>
                          <CheckCircle2 className="w-3 h-3" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-sm text-[#111827] whitespace-pre-wrap leading-relaxed">
                    {result.full_caption || result.caption}
                  </p>
                </div>

                {/* Hashtags (if included) */}
                {result.hashtags && result.hashtags.length > 0 && (
                  <div className="bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg p-4">
                    <p className="text-xs font-semibold text-[#4b5563] mb-2">Hashtags:</p>
                    <div className="flex flex-wrap gap-2">
                      {result.hashtags.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-[#1e293b] text-white rounded text-xs font-medium"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Post Info */}
                {result.post_url && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-sm font-semibold text-green-600 mb-1">
                      Posted to {platform === 'linkedin' ? 'LinkedIn' : 'Instagram'}
                    </p>
                    <a
                      href={result.post_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-green-700 hover:underline flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      View Post →
                    </a>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full min-h-[400px] text-[#9ca3af]">
                <Image className="w-16 h-16 mb-4 opacity-50" />
                <p className="text-sm">Your generated marketing post will appear here</p>
              </div>
            )}
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-8 bg-[#f5f5f5] border border-[#e5e7eb] rounded-xl p-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-4">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-[#1e293b] rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">1</span>
              </div>
              <div>
                <p className="font-semibold text-[#111827]">Enter Your Topic</p>
                <p className="text-sm text-[#4b5563]">Describe what your marketing post is about</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-[#1e293b] rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">2</span>
              </div>
              <div>
                <p className="font-semibold text-[#111827]">AI Generates Content</p>
                <p className="text-sm text-[#4b5563]">Google Imagen creates the image, AI writes the caption</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-[#1e293b] rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-white font-bold">3</span>
              </div>
              <div>
                <p className="font-semibold text-[#111827]">Download & Post</p>
                <p className="text-sm text-[#4b5563]">Download the image and post to your social media</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MarketingPost

