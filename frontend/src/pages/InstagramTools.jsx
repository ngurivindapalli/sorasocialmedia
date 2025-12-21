import { useState, useEffect } from 'react'
import { Video, Play, Loader2 } from 'lucide-react'
import axios from 'axios'
import SoraVideoPlayer from '../components/SoraVideoPlayer'
import VideoGenerationLoader from '../components/VideoGenerationLoader'
import { TextShimmer } from '../components/ui/text-shimmer'
import DocumentUpload from '../components/DocumentUpload'
import design from '../../design.json'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function InstagramTools() {
  const [mode, setMode] = useState('single')
  const [username, setUsername] = useState('')
  const [videoLimit, setVideoLimit] = useState(3)
  const [videoSeconds, setVideoSeconds] = useState(8)
  const [multiUsernames, setMultiUsernames] = useState(['', ''])
  const [videosPerUser, setVideosPerUser] = useState(2)
  const [combineStyle, setCombineStyle] = useState('fusion')
  const [llmProvider, setLlmProvider] = useState('openai')
  const [videoModel, setVideoModel] = useState('sora-2') // 'sora-2' or 'veo-3'
  const [loading, setLoading] = useState(false)
  const [generatingVideo, setGeneratingVideo] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  
  // Informational video state
  const [infoTopic, setInfoTopic] = useState('')
  const [companyContext, setCompanyContext] = useState('')
  const [keyPoints, setKeyPoints] = useState([''])
  const [numImages, setNumImages] = useState(3)
  const [infoVideoResult, setInfoVideoResult] = useState(null)
  const [infoVideoJobStatus, setInfoVideoJobStatus] = useState(null) // Track video job status
  
  // Document upload state
  const [documents, setDocuments] = useState([])

  // Design tokens
  const { colors, typography, spacing, layout } = design
  const maxContentWidth = layout.page.maxContentWidth
  const pagePaddingX = spacing.page.paddingXDesktop
  const sectionGap = spacing.page.sectionGap

  // Check if any videos are being generated
  useEffect(() => {
    if (results) {
      console.log('[Instagram] Results updated:', results)
      let hasGeneratingVideo = false
      
      if (results.type === 'single' && results.data?.analyzed_videos) {
        console.log('[Instagram] Checking single mode videos:', results.data.analyzed_videos)
        hasGeneratingVideo = results.data.analyzed_videos.some(
          video => video.sora_video_job && 
          (video.sora_video_job.status === 'queued' || video.sora_video_job.status === 'in_progress')
        )
      } else if (results.type === 'multi' && results.data?.combined_sora_video_job) {
        const job = results.data.combined_sora_video_job
        hasGeneratingVideo = job.status === 'queued' || job.status === 'in_progress'
      }
      
      console.log('[Instagram] Generating video state:', hasGeneratingVideo)
      setGeneratingVideo(hasGeneratingVideo)
    } else {
      setGeneratingVideo(false)
    }
  }, [results])

  // Adjust video duration when model changes to ensure it's within valid range
  useEffect(() => {
    if (videoModel === 'veo-3') {
      // Veo 3 supports 4-60 seconds
      if (videoSeconds < 4) {
        setVideoSeconds(4)
      } else if (videoSeconds > 60) {
        setVideoSeconds(60)
      }
    } else {
      // Sora 2 supports 5-16 seconds
      if (videoSeconds < 5) {
        setVideoSeconds(5)
      } else if (videoSeconds > 16) {
        setVideoSeconds(16)
      }
    }
  }, [videoModel, videoSeconds])

  const handleAnalyze = async () => {
    if (mode === 'informational') {
      if (!username.trim()) {
        setError('Please enter an Instagram username to learn from')
        return
      }
      if (!videoSeconds || videoSeconds < 4 || videoSeconds > 60) {
        setError('Please enter a video duration between 4-60 seconds for Veo 3')
        return
      }
    } else if (mode === 'single') {
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
    setInfoVideoResult(null)
    setGeneratingVideo(false) // Reset generating video state

    try {
      if (mode === 'informational') {
        console.log('[Instagram] Calling informational video API with:', { 
          username: username.trim().replace('@', ''),
          target_duration: videoSeconds
        })
        console.log('[Instagram] API URL:', `${API_URL}/api/video/informational`)
        
        const requestPayload = {
          username: username.trim().replace('@', ''),
          target_duration: videoSeconds,
          document_ids: documents.map(doc => doc.id)
        }
        console.log('[Instagram] Request payload:', requestPayload)
        
        const response = await axios.post(`${API_URL}/api/video/informational`, requestPayload, {
          timeout: 600000 // 10 minute timeout for video processing (images + video)
        })
        
        console.log('[Instagram] Informational video API Response received:', response.status)
        console.log('[Instagram] Response data:', response.data)
        
        setInfoVideoResult(response.data)
      } else if (mode === 'single') {
        console.log('[Instagram] Calling API with:', { username: username.trim().replace('@', ''), video_limit: videoLimit, video_seconds: videoSeconds })
        console.log('[Instagram] API URL:', `${API_URL}/api/analyze`)
        
        const requestPayload = {
          username: username.trim().replace('@', ''),
          video_limit: videoLimit,
          video_seconds: videoSeconds,
          llm_provider: llmProvider,
          video_model: videoModel,
          document_ids: documents.map(doc => doc.id)
        }
        console.log('[Instagram] Request payload:', requestPayload)
        console.log('[Instagram] Selected video model:', videoModel)
        
        const response = await axios.post(`${API_URL}/api/analyze`, requestPayload, {
          timeout: 300000 // 5 minute timeout for video processing
        })
        
        console.log('[Instagram] API Response received:', response.status)
        console.log('[Instagram] API Response data:', response.data)
        console.log('[Instagram] Response structure:', {
          hasData: !!response.data,
          keys: response.data ? Object.keys(response.data) : [],
          hasScrapedVideos: !!response.data?.scraped_videos,
          hasAnalyzedVideos: !!response.data?.analyzed_videos,
          scrapedCount: response.data?.scraped_videos?.length,
          analyzedCount: response.data?.analyzed_videos?.length
        })
        
        setResults({ type: 'single', data: response.data })
      } else {
        const validUsernames = multiUsernames.filter(u => u.trim()).map(u => u.replace('@', ''))
        console.log('[Instagram] Calling multi-user API with:', { usernames: validUsernames, videos_per_user: videosPerUser, combine_style: combineStyle, video_seconds: videoSeconds })
        const response = await axios.post(`${API_URL}/api/analyze/multi`, {
          usernames: validUsernames,
          videos_per_user: videosPerUser,
          combine_style: combineStyle,
          video_seconds: videoSeconds,
          video_model: videoModel === 'sora-2' ? 'sora-2-pro' : videoModel, // Use pro for multi-user
          document_ids: documents.map(doc => doc.id)
        })
        console.log('[Instagram] Multi-user API Response:', response.data)
        setResults({ type: 'multi', data: response.data })
      }
    } catch (err) {
      console.error('[Instagram] API Error:', err)
      console.error('[Instagram] Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      })
      if (err.response) {
        // Server responded with error
        setError(err.response?.data?.detail || err.response?.data?.message || `Server error: ${err.response.status}`)
      } else if (err.request) {
        // Request made but no response
        setError('Unable to connect to server. Please check if the backend is running.')
      } else {
        // Something else happened
        setError(err.message || 'Failed to analyze videos. Please try again.')
      }
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
    <div 
      className="min-h-screen" 
      style={{ 
        backgroundColor: colors.background.section,
        fontFamily: typography.fontFamilies.body,
        paddingTop: spacing.scale['3xl'],
        paddingBottom: sectionGap,
        maxWidth: `${maxContentWidth}px`,
        margin: '0 auto',
        paddingLeft: `${pagePaddingX}px`,
        paddingRight: `${pagePaddingX}px`
      }}
    >
      
      {/* Sora Feature Notice */}
      <div 
        className="rounded-2xl mb-8"
        style={{
          backgroundColor: colors.background.card,
          border: `1px solid ${colors.borders.subtle}`,
          borderRadius: '24px',
          padding: spacing.scale['3xl'],
          boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
        }}
      >
        <p style={{ 
          fontSize: typography.sizes.sm, 
          color: colors.text.muted,
          lineHeight: typography.lineHeights.normal,
          fontFamily: typography.fontFamilies.body
        }}>
          Powered by OpenAI Sora - Generate professional videos from Instagram content analysis. 
          Videos are created automatically and available for download as MP4 files.
        </p>
      </div>

      {/* Input Section */}
      <div 
        className="rounded-2xl mb-8"
        style={{
          backgroundColor: colors.background.card,
          border: `1px solid ${colors.borders.subtle}`,
          borderRadius: '24px',
          padding: spacing.scale['3xl'],
          boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
        }}
      >
        <h2 style={{ 
          fontSize: typography.sizes.sectionTitle, 
          fontWeight: typography.weights.semibold,
          color: colors.text.primary,
          marginBottom: spacing.scale['5xl'],
          fontFamily: typography.fontFamilies.heading
        }}>
          Analyze Instagram Videos
        </h2>

        {/* Mode Toggle */}
        <div className="flex gap-2 mb-8">
          <button
            onClick={() => setMode('single')}
            className="flex-1 py-3 px-6 rounded-lg text-sm font-medium transition-all"
            style={{
              backgroundColor: mode === 'single' ? layout.navbar.primaryCta.background : 'transparent',
              color: mode === 'single' ? layout.navbar.primaryCta.textColor : colors.text.muted,
              border: mode === 'single' ? 'none' : `1px solid ${colors.borders.subtle}`,
              fontSize: typography.sizes.sm,
              fontWeight: typography.weights.medium,
              fontFamily: typography.fontFamilies.body
            }}
            disabled={loading}
            onMouseEnter={(e) => {
              if (mode !== 'single') {
                e.currentTarget.style.color = colors.text.primary
              }
            }}
            onMouseLeave={(e) => {
              if (mode !== 'single') {
                e.currentTarget.style.color = colors.text.muted
              }
            }}
          >
            Single User
          </button>
          <button
            onClick={() => setMode('multi')}
            className="flex-1 py-3 px-6 rounded-lg text-sm font-medium transition-all"
            style={{
              backgroundColor: mode === 'multi' ? layout.navbar.primaryCta.background : 'transparent',
              color: mode === 'multi' ? layout.navbar.primaryCta.textColor : colors.text.muted,
              border: mode === 'multi' ? 'none' : `1px solid ${colors.borders.subtle}`,
              fontSize: typography.sizes.sm,
              fontWeight: typography.weights.medium,
              fontFamily: typography.fontFamilies.body
            }}
            disabled={loading}
            onMouseEnter={(e) => {
              if (mode !== 'multi') {
                e.currentTarget.style.color = colors.text.primary
              }
            }}
            onMouseLeave={(e) => {
              if (mode !== 'multi') {
                e.currentTarget.style.color = colors.text.muted
              }
            }}
          >
            Multi-User Fusion
          </button>
          <button
            onClick={() => setMode('informational')}
            className="flex-1 py-3 px-6 rounded-lg text-sm font-medium transition-all"
            style={{
              backgroundColor: mode === 'informational' ? layout.navbar.primaryCta.background : 'transparent',
              color: mode === 'informational' ? layout.navbar.primaryCta.textColor : colors.text.muted,
              border: mode === 'informational' ? 'none' : `1px solid ${colors.borders.subtle}`,
              fontSize: typography.sizes.sm,
              fontWeight: typography.weights.medium,
              fontFamily: typography.fontFamilies.body
            }}
            disabled={loading}
            onMouseEnter={(e) => {
              if (mode !== 'informational') {
                e.currentTarget.style.color = colors.text.primary
              }
            }}
            onMouseLeave={(e) => {
              if (mode !== 'informational') {
                e.currentTarget.style.color = colors.text.muted
              }
            }}
          >
            Informational Videos
          </button>
        </div>

        {/* Document Upload Section */}
        <div className="mb-8">
          <label style={{ 
            display: 'block',
            fontSize: typography.sizes.sm, 
            fontWeight: typography.weights.medium,
            color: colors.text.primary,
            marginBottom: spacing.scale.sm,
            fontFamily: typography.fontFamilies.body
          }}>
            Upload Documents (Optional)
          </label>
          <p style={{ 
            fontSize: typography.sizes.xs, 
            color: colors.text.muted,
            marginBottom: spacing.scale.md,
            fontFamily: typography.fontFamilies.body
          }}>
            Upload PDF, DOCX, or TXT files to provide additional context for AI content generation
          </p>
          <DocumentUpload 
            onDocumentsChange={setDocuments}
            existingDocuments={documents}
          />
        </div>

        {mode === 'single' ? (
          <div className="space-y-6 mb-8">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm,
                  fontFamily: typography.fontFamilies.body
                }}>
                  Instagram Username
                </label>
                <input
                  type="text"
                  placeholder="@username or username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md,
                    fontFamily: typography.fontFamilies.body
                  }}
                  disabled={loading}
                />
                <p style={{ 
                  fontSize: typography.sizes.xs, 
                  color: colors.text.lightMuted,
                  marginTop: spacing.scale.xs,
                  fontFamily: typography.fontFamilies.body
                }}>
                  Public accounts only
                </p>
              </div>

              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm,
                  fontFamily: typography.fontFamilies.body
                }}>
                  Number of Videos
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={videoLimit}
                  onChange={(e) => setVideoLimit(parseInt(e.target.value))}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md,
                    fontFamily: typography.fontFamilies.body
                  }}
                  disabled={loading}
                />
                <p style={{ 
                  fontSize: typography.sizes.xs, 
                  color: colors.text.lightMuted,
                  marginTop: spacing.scale.xs,
                  fontFamily: typography.fontFamilies.body
                }}>
                  Analyzes top 3 videos by default
                </p>
              </div>
            </div>

            <div>
              <label style={{ 
                display: 'block',
                fontSize: typography.sizes.sm, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm
              }}>
                Generated Video Duration (seconds)
              </label>
              <input
                type="number"
                min={videoModel === 'veo-3' ? 4 : 5}
                max={videoModel === 'veo-3' ? 60 : 16}
                value={videoSeconds}
                onChange={(e) => {
                  const val = parseInt(e.target.value)
                  if (videoModel === 'veo-3') {
                    if (val >= 4 && val <= 60) {
                      setVideoSeconds(val)
                    }
                  } else {
                    if (val >= 5 && val <= 16) {
                      setVideoSeconds(val)
                    }
                  }
                }}
                className="w-full px-4 py-3 rounded-lg focus:outline-none"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  color: colors.text.primary,
                  fontSize: typography.sizes.md
                }}
                disabled={loading}
              />
              <p style={{ 
                fontSize: typography.sizes.xs, 
                color: colors.text.lightMuted,
                marginTop: spacing.scale.xs
              }}>
                {videoModel === 'veo-3' 
                  ? 'How long each AI-generated video should be (4-60 seconds for Veo 3)'
                  : 'How long each AI-generated video should be (5-16 seconds for Sora 2)'}
              </p>
              {videoModel === 'veo-3' && (
                <p style={{ 
                  fontSize: typography.sizes.xs, 
                  color: '#f59e0b',
                  marginTop: spacing.scale.xs,
                  fontWeight: typography.weights.medium
                }}>
                  ⚠️ Note: Veo 3 generation may take 2-5 minutes for longer videos (30+ seconds)
                </p>
              )}
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm
                }}>
                  LLM Provider for Script Generation
                </label>
                <select
                  value={llmProvider}
                  onChange={(e) => setLlmProvider(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md
                  }}
                  disabled={loading}
                >
                  <option value="openai">OpenAI (GPT-4)</option>
                  <option value="claude">Claude (Anthropic)</option>
                </select>
                <p style={{ 
                  fontSize: typography.sizes.xs, 
                  color: colors.text.lightMuted,
                  marginTop: spacing.scale.xs
                }}>
                  Choose which AI model to use for generating video scripts
                </p>
              </div>

              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm
                }}>
                  Video Generation Model
                </label>
                <select
                  value={videoModel}
                  onChange={(e) => setVideoModel(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md
                  }}
                  disabled={loading}
                >
                  <option value="sora-2">Sora 2 (OpenAI)</option>
                  <option value="veo-3">Veo 3 (Google)</option>
                </select>
                <p style={{ 
                  fontSize: typography.sizes.xs, 
                  color: colors.text.lightMuted,
                  marginTop: spacing.scale.xs
                }}>
                  Choose which model to use for generating videos
                </p>
              </div>
            </div>
          </div>
        ) : mode === 'multi' ? (
          <div className="space-y-6 mb-8">
            <div>
              <label style={{ 
                display: 'block',
                fontSize: typography.sizes.sm, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm
              }}>
                Instagram Usernames (2-5 users)
              </label>
              {multiUsernames.map((user, index) => (
                <div key={index} className="flex gap-2 mb-2">
                  <input
                    type="text"
                    placeholder={`@username ${index + 1}`}
                    value={user}
                    onChange={(e) => updateUsername(index, e.target.value)}
                    className="flex-1 px-4 py-3 rounded-lg focus:outline-none"
                    style={{
                      backgroundColor: colors.background.section,
                      border: `1px solid ${colors.borders.subtle}`,
                      color: colors.text.primary,
                      fontSize: typography.sizes.md
                    }}
                    disabled={loading}
                  />
                  {multiUsernames.length > 2 && (
                    <button
                      onClick={() => removeUsername(index)}
                      className="px-4 py-3 rounded-lg transition-colors"
                      style={{
                        backgroundColor: '#fee2e2',
                        border: '1px solid #fca5a5',
                        color: '#dc2626',
                        fontSize: typography.sizes.sm
                      }}
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
                  className="mt-2 px-4 py-2 rounded-lg transition-colors text-sm"
                  style={{
                    backgroundColor: 'transparent',
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.muted,
                    fontSize: typography.sizes.sm
                  }}
                  disabled={loading}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = colors.text.primary
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = colors.text.muted
                  }}
                >
                  Add Another User
                </button>
              )}
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm,
                  fontFamily: typography.fontFamilies.body
                }}>
                  Videos Per User
                </label>
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={videosPerUser}
                  onChange={(e) => setVideosPerUser(parseInt(e.target.value))}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md,
                    fontFamily: typography.fontFamilies.body
                  }}
                  disabled={loading}
                />
              </div>

              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm,
                  fontFamily: typography.fontFamilies.body
                }}>
                  Combine Style
                </label>
                <select
                  value={combineStyle}
                  onChange={(e) => setCombineStyle(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md,
                    fontFamily: typography.fontFamilies.body
                  }}
                  disabled={loading}
                >
                  <option value="fusion">Fusion (Blend Styles)</option>
                  <option value="sequence">Sequential (Story Flow)</option>
                </select>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm
                }}>
                  Generated Video Duration (seconds)
                </label>
                <input
                  type="number"
                  min={videoModel === 'veo-3' ? 4 : 5}
                  max={videoModel === 'veo-3' ? 60 : 16}
                  value={videoSeconds}
                  onChange={(e) => {
                    const val = parseInt(e.target.value)
                    if (videoModel === 'veo-3') {
                      if (val >= 4 && val <= 60) {
                        setVideoSeconds(val)
                      }
                    } else {
                      if (val >= 5 && val <= 16) {
                        setVideoSeconds(val)
                      }
                    }
                  }}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md
                  }}
                  disabled={loading}
                />
                <p style={{ 
                  fontSize: typography.sizes.xs, 
                  color: colors.text.lightMuted,
                  marginTop: spacing.scale.xs
                }}>
                  {videoModel === 'veo-3' 
                    ? 'How long the combined fusion video should be (4-60 seconds for Veo 3)'
                    : 'How long the combined fusion video should be (5-16 seconds for Sora 2 Pro)'}
                </p>
                {videoModel === 'veo-3' && (
                  <p style={{ 
                    fontSize: typography.sizes.xs, 
                    color: '#f59e0b',
                    marginTop: spacing.scale.xs,
                    fontWeight: typography.weights.medium
                  }}>
                    ⚠️ Note: Veo 3 generation may take 2-5 minutes for longer videos (30+ seconds)
                  </p>
                )}
              </div>

              <div>
                <label style={{ 
                  display: 'block',
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm
                }}>
                  Video Generation Model
                </label>
                <select
                  value={videoModel}
                  onChange={(e) => setVideoModel(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg focus:outline-none"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`,
                    color: colors.text.primary,
                    fontSize: typography.sizes.md
                  }}
                  disabled={loading}
                >
                  <option value="sora-2">Sora 2 Pro (OpenAI)</option>
                  <option value="veo-3">Veo 3 (Google)</option>
                </select>
                <p style={{ 
                  fontSize: typography.sizes.xs, 
                  color: colors.text.lightMuted,
                  marginTop: spacing.scale.xs
                }}>
                  Choose which model to use for generating the combined video
                </p>
              </div>
            </div>

            <div 
              className="rounded-lg p-4"
              style={{
                backgroundColor: '#eff6ff',
                border: '1px solid #bfdbfe'
              }}
            >
              <p style={{ 
                fontSize: typography.sizes.sm, 
                color: '#1e40af'
              }}>
                Multi-User Mode: Analyzes top videos from multiple creators and creates a combined Sora script that fuses their best elements together.
              </p>
            </div>
          </div>
        ) : mode === 'informational' ? (
          <div className="space-y-6 mb-8">
            <div>
              <label style={{ 
                display: 'block',
                fontSize: typography.sizes.sm, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm
              }}>
                Instagram Username *
              </label>
              <input
                type="text"
                placeholder="Enter Instagram username to learn from (e.g., welcome.ai)"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-lg focus:outline-none"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  color: colors.text.primary,
                  fontSize: typography.sizes.md
                }}
                disabled={loading}
              />
              <p style={{ 
                fontSize: typography.sizes.xs, 
                color: colors.text.lightMuted,
                marginTop: spacing.scale.xs
              }}>
                AI will analyze this profile to understand your brand, style, and content themes
              </p>
            </div>

            <div>
              <label style={{ 
                display: 'block',
                fontSize: typography.sizes.sm, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm
              }}>
                Video Duration *
              </label>
              <input
                type="number"
                min="4"
                max="60"
                value={videoSeconds}
                onChange={(e) => {
                  const val = parseInt(e.target.value) || 8
                  if (val >= 4 && val <= 60) {
                    setVideoSeconds(val)
                  }
                }}
                className="w-full px-4 py-3 rounded-lg focus:outline-none"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  color: colors.text.primary,
                  fontSize: typography.sizes.md
                }}
                disabled={loading}
              />
              <p style={{ 
                fontSize: typography.sizes.xs, 
                color: colors.text.lightMuted,
                marginTop: spacing.scale.xs
              }}>
                How long should the video be? (4-60 seconds for Veo 3)
              </p>
              <p style={{ 
                fontSize: typography.sizes.xs, 
                color: '#f59e0b',
                marginTop: spacing.scale.xs,
                fontWeight: typography.weights.medium
              }}>
                ⚠️ Note: Informational videos use Veo 3. Generation may take 2-5 minutes for longer videos (30+ seconds)
              </p>
            </div>

            <div 
              className="rounded-lg p-4"
              style={{
                backgroundColor: '#eff6ff',
                border: '1px solid #bfdbfe'
              }}
            >
              <p style={{ 
                fontSize: typography.sizes.sm, 
                color: '#1e40af'
              }}>
                ✨ <strong>Auto-Mode:</strong> AI will scrape the Instagram profile, analyze the content style and brand identity, then automatically generate images and video using Veo 3 that matches your page's aesthetic.
              </p>
            </div>

            <div 
              className="rounded-lg p-4"
              style={{
                backgroundColor: '#f0fdf4',
                border: '1px solid #86efac'
              }}
            >
              <p style={{ 
                fontSize: typography.sizes.sm, 
                color: '#166534'
              }}>
                📹 Informational Video Mode: Creates educational Instagram-style videos with AI-generated images from Nano Banana, incorporating your company context and key points.
              </p>
            </div>
          </div>
        ) : null}

        <button
          onClick={handleAnalyze}
          disabled={loading}
          className="w-full font-medium py-4 px-8 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          style={{
            backgroundColor: layout.navbar.primaryCta.background,
            color: layout.navbar.primaryCta.textColor,
            fontSize: layout.navbar.primaryCta.fontSize,
            fontWeight: typography.weights[layout.navbar.primaryCta.fontWeight],
            borderRadius: `${layout.navbar.primaryCta.borderRadius}px`,
            fontFamily: typography.fontFamilies.body
          }}
          onMouseEnter={(e) => {
            if (!loading) {
              e.currentTarget.style.backgroundColor = colors.accent.primaryHover
            }
          }}
          onMouseLeave={(e) => {
            if (!loading) {
              e.currentTarget.style.backgroundColor = layout.navbar.primaryCta.background
            }
          }}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <TextShimmer
                className="text-sm font-medium"
                duration={1.5}
                style={{
                  '--base-color': '#9ca3af',
                  '--base-gradient-color': '#ffffff'
                }}
              >
                {mode === 'informational' 
                  ? 'Generating images and video...' 
                  : mode === 'multi' 
                    ? 'Analyzing multiple users...' 
                    : 'Analyzing videos...'}
              </TextShimmer>
            </>
          ) : (
            <>
              <Video className="w-5 h-5" />
              {mode === 'informational' 
                ? 'Create Informational Video' 
                : mode === 'multi' 
                  ? 'Analyze Multiple Users' 
                  : 'Analyze Videos'}
            </>
          )}
        </button>

        {error && (
          <div 
            className="mt-4 p-4 rounded-lg"
            style={{
              backgroundColor: '#fee2e2',
              border: '1px solid #fca5a5',
              color: '#dc2626'
            }}
          >
            {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {results && results.type === 'single' && (
        <div className="space-y-8">
          {/* Debug Info - Remove after testing */}
          {console.log('[Instagram] Rendering results:', {
            hasResults: !!results,
            type: results?.type,
            hasData: !!results?.data,
            hasScrapedVideos: !!results?.data?.scraped_videos,
            hasAnalyzedVideos: !!results?.data?.analyzed_videos,
            scrapedCount: results?.data?.scraped_videos?.length,
            analyzedCount: results?.data?.analyzed_videos?.length
          })}
          
          {/* AI-Learned Context Section */}
          {results.data?.page_context && (
            <div 
              className="rounded-2xl"
              style={{
                backgroundColor: colors.background.card,
                border: `1px solid ${colors.borders.subtle}`,
                borderRadius: '24px',
                padding: spacing.scale['3xl'],
                boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
              }}
            >
              <div className="flex items-center gap-3 mb-4">
                <h3 style={{ 
                  fontSize: typography.sizes.xl, 
                  fontWeight: typography.weights.semibold,
                  color: colors.text.primary,
                }}>
                  AI-Learned Context
                </h3>
              </div>
              <p style={{ 
                fontSize: typography.sizes.sm,
                color: colors.text.muted,
                marginBottom: spacing.scale.md,
                lineHeight: typography.lineHeights.relaxed
              }}>
                Here's what the AI learned about this page/profile to inform script generation:
              </p>
              <div 
                className="rounded-lg p-4"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  whiteSpace: 'pre-wrap',
                  lineHeight: typography.lineHeights.relaxed
                }}
              >
                <p style={{ 
                  fontSize: typography.sizes.sm,
                  color: colors.text.primary,
                  margin: 0
                }}>
                  {results.data.page_context}
                </p>
              </div>
            </div>
          )}
          
          {/* Scraped Videos */}
          {results.data?.scraped_videos && results.data.scraped_videos.length > 0 ? (
          <div 
            className="rounded-2xl"
            style={{
              backgroundColor: colors.background.card,
              border: `1px solid ${colors.borders.subtle}`,
              borderRadius: '24px',
              padding: spacing.scale['3xl'],
              boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
            }}
          >
            <h3 style={{ 
              fontSize: typography.sizes.xl, 
              fontWeight: typography.weights.semibold,
              color: colors.text.primary,
              marginBottom: spacing.scale['3xl']
            }}>
              Found Videos from @{results.data.username}
            </h3>
            <div className="grid gap-3">
              {results.data.scraped_videos.map((video, index) => (
                <div 
                  key={video.id} 
                  className="rounded-lg p-4 transition-colors"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`
                  }}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span style={{ 
                      fontSize: typography.sizes.sm, 
                      fontWeight: typography.weights.medium,
                      color: colors.text.muted
                    }}>
                      Video {index + 1}
                    </span>
                    <a 
                      href={video.post_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ 
                        fontSize: typography.sizes.xs, 
                        color: colors.text.lightMuted,
                        textDecoration: 'none'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.color = colors.text.primary
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.color = colors.text.lightMuted
                      }}
                    >
                      View on Instagram
                    </a>
                  </div>
                  <p style={{ 
                    color: colors.text.primary, 
                    fontSize: typography.sizes.sm,
                    marginBottom: spacing.scale.sm,
                    lineHeight: typography.lineHeights.normal
                  }}>
                    {video.text}
                  </p>
                  <div className="flex gap-4" style={{ fontSize: typography.sizes.xs, color: colors.text.lightMuted }}>
                    <span>{video.views.toLocaleString()} views</span>
                    <span>{video.likes.toLocaleString()} likes</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
          ) : (
            <div 
              className="rounded-2xl p-8 text-center"
              style={{
                backgroundColor: colors.background.card,
                border: `1px solid ${colors.borders.subtle}`,
                borderRadius: '24px',
                padding: spacing.scale['3xl']
              }}
            >
              <p style={{ color: colors.text.muted }}>
                No videos found. Please check the username and try again.
              </p>
            </div>
          )}

          {/* Loading State for Video Generation */}
          {generatingVideo && (
            <div className="mb-8">
              <VideoGenerationLoader message="Generating your video..." inline={true} />
            </div>
          )}

          {/* Loading State - Show while processing if no analyzed videos yet */}
          {loading && (!results.data?.analyzed_videos || results.data.analyzed_videos.length === 0) && (
            <div className="mb-8">
              <VideoGenerationLoader message="Generating scripts..." inline={true} />
            </div>
          )}

          {/* Analyzed Results */}
          {results.data?.analyzed_videos && results.data.analyzed_videos.length > 0 ? (
            results.data.analyzed_videos.map((result, index) => (
            <div 
              key={result.video_id} 
              className="rounded-2xl"
              style={{
                backgroundColor: colors.background.card,
                border: `1px solid ${colors.borders.subtle}`,
                borderRadius: '24px',
                padding: spacing.scale['3xl'],
                boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
              }}
            >
              <h3 style={{ 
                fontSize: typography.sizes.sectionTitle, 
                fontWeight: typography.weights.semibold,
                color: colors.text.primary,
                marginBottom: spacing.scale['5xl']
              }}>
                Video {index + 1} Analysis
              </h3>

              {/* Vision API Analysis */}
              {result.thumbnail_analysis && (
                <div className="mb-6">
                  <h4 style={{ 
                    fontSize: typography.sizes.sm, 
                    fontWeight: typography.weights.medium,
                    color: colors.text.muted,
                    marginBottom: spacing.scale.md
                  }}>
                    Visual Analysis
                    <span style={{ 
                      marginLeft: spacing.scale.sm,
                      fontSize: typography.sizes.xs,
                      backgroundColor: '#dbeafe',
                      color: '#1e40af',
                      padding: `${spacing.scale.xs}px ${spacing.scale.sm}px`,
                      borderRadius: '4px'
                    }}>
                      Vision API
                    </span>
                  </h4>
                  <div 
                    className="rounded-lg p-4"
                    style={{
                      backgroundColor: colors.background.section,
                      border: `1px solid ${colors.borders.subtle}`
                    }}
                  >
                    <div className="grid md:grid-cols-2 gap-3" style={{ fontSize: typography.sizes.sm }}>
                      <div>
                        <span style={{ color: colors.text.lightMuted }}>Colors:</span>
                        <span style={{ color: colors.text.primary, marginLeft: spacing.scale.sm }}>
                          {result.thumbnail_analysis.dominant_colors.join(', ')}
                        </span>
                      </div>
                      <div>
                        <span style={{ color: colors.text.lightMuted }}>Composition:</span>
                        <span style={{ color: colors.text.primary, marginLeft: spacing.scale.sm }}>
                          {result.thumbnail_analysis.composition}
                        </span>
                      </div>
                      <div className="md:col-span-2">
                        <span style={{ color: colors.text.lightMuted }}>Elements:</span>
                        <span style={{ color: colors.text.primary, marginLeft: spacing.scale.sm }}>
                          {result.thumbnail_analysis.visual_elements.join(', ')}
                        </span>
                      </div>
                      <div className="md:col-span-2">
                        <span style={{ color: colors.text.lightMuted }}>Style:</span>
                        <span style={{ color: colors.text.primary, marginLeft: spacing.scale.sm }}>
                          {result.thumbnail_analysis.style_assessment}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Transcription */}
              <div className="mb-6">
                <h4 style={{ 
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.muted,
                  marginBottom: spacing.scale.md
                }}>
                  Transcription
                </h4>
                <div 
                  className="rounded-lg p-4"
                  style={{
                    backgroundColor: colors.background.section,
                    border: `1px solid ${colors.borders.subtle}`
                  }}
                >
                  <p style={{ 
                    color: colors.text.primary, 
                    fontSize: typography.sizes.sm,
                    lineHeight: typography.lineHeights.relaxed,
                    whiteSpace: 'pre-wrap'
                  }}>
                    {result.transcription}
                  </p>
                </div>
              </div>

              {/* Sora Script */}
              <div className="mb-6">
                <h4 style={{ 
                  fontSize: typography.sizes.sm, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.muted,
                  marginBottom: spacing.scale.md
                }}>
                  Sora AI Script
                  {result.structured_sora_script && (
                    <span style={{ 
                      marginLeft: spacing.scale.sm,
                      fontSize: typography.sizes.xs,
                      backgroundColor: '#f3e8ff',
                      color: '#7c3aed',
                      padding: `${spacing.scale.xs}px ${spacing.scale.sm}px`,
                      borderRadius: '4px'
                    }}>
                      Structured Outputs
                    </span>
                  )}
                </h4>
                
                {result.structured_sora_script ? (
                  <div className="space-y-3">
                    <div 
                      className="rounded-lg p-4"
                      style={{
                        backgroundColor: colors.background.section,
                        border: `1px solid ${colors.borders.subtle}`
                      }}
                    >
                      <h5 style={{ 
                        fontSize: typography.sizes.xs, 
                        fontWeight: typography.weights.medium,
                        color: colors.text.lightMuted,
                        marginBottom: spacing.scale.sm
                      }}>
                        Core Concept
                      </h5>
                      <p style={{ 
                        color: colors.text.primary, 
                        fontSize: typography.sizes.sm
                      }}>
                        {result.structured_sora_script.core_concept}
                      </p>
                    </div>
                    
                    <div 
                      className="rounded-lg p-4"
                      style={{
                        backgroundColor: '#fdf2f8',
                        border: '1px solid #fbcfe8'
                      }}
                    >
                      <h5 style={{ 
                        fontSize: typography.sizes.sm, 
                        fontWeight: typography.weights.bold,
                        color: '#be185d',
                        marginBottom: spacing.scale.sm
                      }}>
                        Visual Style
                      </h5>
                      <div className="space-y-2" style={{ fontSize: typography.sizes.sm }}>
                        <div>
                          <span style={{ color: colors.text.muted }}>Colors: </span>
                          <span style={{ color: colors.text.primary }}>
                            {result.structured_sora_script.visual_style.primary_colors.join(', ')}
                          </span>
                        </div>
                        <div>
                          <span style={{ color: colors.text.muted }}>Lighting: </span>
                          <span style={{ color: colors.text.primary }}>
                            {result.structured_sora_script.visual_style.lighting}
                          </span>
                        </div>
                        <div>
                          <span style={{ color: colors.text.muted }}>Mood: </span>
                          <span style={{ color: colors.text.primary }}>
                            {result.structured_sora_script.visual_style.mood}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div 
                      className="rounded-lg p-4"
                      style={{
                        backgroundColor: '#eef2ff',
                        border: '1px solid #c7d2fe'
                      }}
                    >
                      <h5 style={{ 
                        fontSize: typography.sizes.sm, 
                        fontWeight: typography.weights.bold,
                        color: '#4338ca',
                        marginBottom: spacing.scale.sm
                      }}>
                        Camera Work
                      </h5>
                      <div className="grid grid-cols-3 gap-2" style={{ fontSize: typography.sizes.xs, color: colors.text.primary }}>
                        <div>
                          <span style={{ color: colors.text.muted }}>Shots: </span>
                          {result.structured_sora_script.camera_work.shot_types.join(', ')}
                        </div>
                        <div>
                          <span style={{ color: colors.text.muted }}>Movements: </span>
                          {result.structured_sora_script.camera_work.camera_movements.join(', ')}
                        </div>
                        <div>
                          <span style={{ color: colors.text.muted }}>Angles: </span>
                          {result.structured_sora_script.camera_work.angles.join(', ')}
                        </div>
                      </div>
                    </div>
                    
                    <div 
                      className="rounded-lg p-6"
                      style={{
                        backgroundColor: '#f0fdf4',
                        border: '1px solid #bbf7d0'
                      }}
                    >
                      <h5 style={{ 
                        fontSize: typography.sizes.sm, 
                        fontWeight: typography.weights.bold,
                        color: '#166534',
                        marginBottom: spacing.scale.sm
                      }}>
                        Complete Sora Prompt
                      </h5>
                      <p style={{ 
                        color: colors.text.primary, 
                        fontSize: typography.sizes.sm,
                        lineHeight: typography.lineHeights.relaxed,
                        whiteSpace: 'pre-wrap'
                      }}>
                        {result.structured_sora_script.full_prompt}
                      </p>
                    </div>
                  </div>
                ) : (
                  <div 
                    className="rounded-lg p-6"
                    style={{
                      backgroundColor: colors.background.section,
                      border: `1px solid ${colors.borders.subtle}`
                    }}
                  >
                    <p style={{ 
                      color: colors.text.primary, 
                      fontSize: typography.sizes.sm,
                      lineHeight: typography.lineHeights.relaxed,
                      whiteSpace: 'pre-wrap'
                    }}>
                      {result.sora_script}
                    </p>
                  </div>
                )}
              </div>

              {/* Sora Generated Video */}
              {result.sora_video_job && (
                <SoraVideoPlayer 
                  videoJob={result.sora_video_job}
                  onStatusChange={(status) => {
                    setResults(prev => {
                      if (!prev || prev.type !== 'single') return prev
                      const updated = { ...prev }
                      updated.data.analyzed_videos = updated.data.analyzed_videos.map(v => {
                        if (v.video_id === result.video_id && v.sora_video_job) {
                          return {
                            ...v,
                            sora_video_job: { ...v.sora_video_job, status }
                          }
                        }
                        return v
                      })
                      return updated
                    })
                  }}
                />
              )}
            </div>
          ))
          ) : !loading ? (
            <div 
              className="rounded-2xl p-8 text-center"
              style={{
                backgroundColor: colors.background.card,
                border: `1px solid ${colors.borders.subtle}`,
                borderRadius: '24px',
                padding: spacing.scale['3xl']
              }}
            >
              <p style={{ color: colors.text.muted }}>
                No analyzed videos found. Please try again or check if the username is correct.
              </p>
            </div>
          ) : null}
        </div>
      )}

      {/* Informational Video Results */}
      {infoVideoResult && (
        <div className="space-y-6">
          <div 
            className="rounded-2xl"
            style={{
              backgroundColor: colors.background.card,
              border: `1px solid ${colors.borders.subtle}`,
              borderRadius: '24px',
              padding: spacing.scale['3xl'],
              boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
            }}
          >
            <h3 style={{ 
              fontSize: typography.sizes.sectionTitle, 
              fontWeight: typography.weights.bold,
              color: colors.text.primary,
              marginBottom: spacing.scale.lg
            }}>
              📹 Informational Video: {infoVideoResult.topic}
            </h3>

            {/* Generated Images */}
            {infoVideoResult.generated_images && infoVideoResult.generated_images.length > 0 && (
              <div className="mb-6">
                <h4 style={{ 
                  fontSize: typography.sizes.lg, 
                  fontWeight: typography.weights.semibold,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.md
                }}>
                  🎨 Generated Images (Nano Banana)
                </h4>
                <div className="grid md:grid-cols-3 gap-4">
                  {infoVideoResult.generated_images.map((img, idx) => (
                    <div key={idx} className="rounded-lg overflow-hidden" style={{
                      border: `1px solid ${colors.borders.subtle}`,
                      backgroundColor: colors.background.section
                    }}>
                      {img.image_url && (
                        <img 
                          src={img.image_url} 
                          alt={`Generated image ${idx + 1}`}
                          className="w-full h-auto"
                          style={{ display: 'block' }}
                        />
                      )}
                      <div className="p-3">
                        <p style={{ 
                          fontSize: typography.sizes.xs, 
                          color: colors.text.muted 
                        }}>
                          {infoVideoResult.image_prompts[idx] || `Image ${idx + 1}`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Video Script */}
            {infoVideoResult.video_script && (
              <div className="mb-6">
                <h4 style={{ 
                  fontSize: typography.sizes.lg, 
                  fontWeight: typography.weights.semibold,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.md
                }}>
                  📝 Video Script
                </h4>
                <div className="rounded-lg p-4" style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`
                }}>
                  <p style={{ 
                    color: colors.text.primary, 
                    fontSize: typography.sizes.sm,
                    lineHeight: typography.lineHeights.relaxed,
                    whiteSpace: 'pre-wrap'
                  }}>
                    {infoVideoResult.video_script}
                  </p>
                </div>
              </div>
            )}

            {/* Generated Video */}
            {infoVideoResult.video_job_id && (
              <div className="mb-6">
                <h4 style={{ 
                  fontSize: typography.sizes.lg, 
                  fontWeight: typography.weights.semibold,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.md
                }}>
                  🎬 Generated Video ({infoVideoResult.video_model})
                </h4>
                <SoraVideoPlayer 
                  videoJob={{
                    job_id: infoVideoResult.video_job_id,
                    status: infoVideoJobStatus?.status || 'in_progress',
                    progress: infoVideoJobStatus?.progress || 0,
                    video_url: infoVideoJobStatus?.video_url || null,
                    model: infoVideoResult.video_model,
                    created_at: Date.now()
                  }}
                  onStatusChange={(status, progress, videoUrl) => {
                    setGeneratingVideo(status === 'in_progress' || status === 'queued')
                    // Preserve the video job status
                    setInfoVideoJobStatus({
                      status,
                      progress: progress || 0,
                      video_url: videoUrl || null
                    })
                  }}
                />
              </div>
            )}

            {/* Composition Data */}
            {infoVideoResult.composition_data && (
              <div className="mt-6 p-4 rounded-lg" style={{
                backgroundColor: '#f0f9ff',
                border: '1px solid #bae6fd'
              }}>
                <h5 style={{ 
                  fontSize: typography.sizes.md, 
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  marginBottom: spacing.scale.sm
                }}>
                  Video Structure
                </h5>
                {infoVideoResult.composition_data.narrative_structure && (
                  <p style={{ 
                    fontSize: typography.sizes.sm, 
                    color: colors.text.muted,
                    marginBottom: spacing.scale.sm
                  }}>
                    <strong>Narrative:</strong> {infoVideoResult.composition_data.narrative_structure}
                  </p>
                )}
                {infoVideoResult.composition_data.text_overlays && infoVideoResult.composition_data.text_overlays.length > 0 && (
                  <div>
                    <strong style={{ fontSize: typography.sizes.sm, color: colors.text.primary }}>Text Overlays:</strong>
                    <ul style={{ marginTop: spacing.scale.xs, paddingLeft: spacing.scale.lg }}>
                      {infoVideoResult.composition_data.text_overlays.map((overlay, idx) => (
                        <li key={idx} style={{ fontSize: typography.sizes.sm, color: colors.text.muted, marginBottom: spacing.scale.xs }}>
                          {overlay}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Multi-User Results */}
      {results && !generatingVideo && results.type === 'multi' && (
        <div className="space-y-6">
          {/* Combined Script Header */}
          <div 
            className="rounded-lg p-6"
            style={{
              background: 'linear-gradient(to right, #f3e8ff, #fce7f3)',
              border: '2px solid #d8b4fe'
            }}
          >
            <h3 style={{ 
              fontSize: typography.sizes.sectionTitle, 
              fontWeight: typography.weights.bold,
              color: colors.text.primary,
              marginBottom: spacing.scale.sm
            }}>
              Combined Sora Script - Multi-Creator Fusion
            </h3>
            <p style={{ color: colors.text.primary, fontSize: typography.sizes.md }}>
              Analyzed {results.data.total_videos_analyzed} videos from: {results.data.usernames.map(u => '@' + u).join(', ')}
            </p>
            <p style={{ 
              fontSize: typography.sizes.sm, 
              color: colors.text.muted,
              marginTop: spacing.scale.sm
            }}>
              {results.data.fusion_notes}
            </p>
          </div>

          {/* Combined Structured Script */}
          {results.data.combined_structured_script ? (
            <div 
              className="rounded-2xl p-10"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
              }}
            >
              <h4 style={{ 
                fontSize: typography.sizes.sectionTitle, 
                fontWeight: typography.weights.bold,
                color: colors.text.primary,
                marginBottom: spacing.scale['3xl']
              }}>
                Structured Combined Script
              </h4>
              <div className="space-y-4">
                <div 
                  className="rounded-lg p-4"
                  style={{
                    backgroundColor: '#faf5ff',
                    border: '1px solid #e9d5ff'
                  }}
                >
                  <h5 style={{ 
                    fontSize: typography.sizes.sm, 
                    fontWeight: typography.weights.bold,
                    color: '#7c3aed',
                    marginBottom: spacing.scale.sm
                  }}>
                    Core Concept
                  </h5>
                  <p style={{ 
                    color: colors.text.primary, 
                    fontSize: typography.sizes.sm
                  }}>
                    {results.data.combined_structured_script.core_concept}
                  </p>
                </div>
                
                <div 
                  className="rounded-lg p-4"
                  style={{
                    backgroundColor: '#fdf2f8',
                    border: '1px solid #fbcfe8'
                  }}
                >
                  <h5 style={{ 
                    fontSize: typography.sizes.sm, 
                    fontWeight: typography.weights.bold,
                    color: '#be185d',
                    marginBottom: spacing.scale.sm
                  }}>
                    Visual Style
                  </h5>
                  <div className="space-y-2" style={{ fontSize: typography.sizes.sm }}>
                    <div>
                      <span style={{ color: colors.text.muted }}>Colors: </span>
                      <span style={{ color: colors.text.primary }}>
                        {results.data.combined_structured_script.visual_style.primary_colors.join(', ')}
                      </span>
                    </div>
                    <div>
                      <span style={{ color: colors.text.muted }}>Lighting: </span>
                      <span style={{ color: colors.text.primary }}>
                        {results.data.combined_structured_script.visual_style.lighting}
                      </span>
                    </div>
                    <div>
                      <span style={{ color: colors.text.muted }}>Mood: </span>
                      <span style={{ color: colors.text.primary }}>
                        {results.data.combined_structured_script.visual_style.mood}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div 
                  className="rounded-lg p-4"
                  style={{
                    backgroundColor: '#eef2ff',
                    border: '1px solid #c7d2fe'
                  }}
                >
                  <h5 style={{ 
                    fontSize: typography.sizes.sm, 
                    fontWeight: typography.weights.bold,
                    color: '#4338ca',
                    marginBottom: spacing.scale.sm
                  }}>
                    Camera Work
                  </h5>
                  <div className="grid grid-cols-3 gap-2" style={{ fontSize: typography.sizes.xs, color: colors.text.primary }}>
                    <div>
                      <span style={{ color: colors.text.muted }}>Shots: </span>
                      {results.data.combined_structured_script.camera_work.shot_types.join(', ')}
                    </div>
                    <div>
                      <span style={{ color: colors.text.muted }}>Movements: </span>
                      {results.data.combined_structured_script.camera_work.camera_movements.join(', ')}
                    </div>
                    <div>
                      <span style={{ color: colors.text.muted }}>Angles: </span>
                      {results.data.combined_structured_script.camera_work.angles.join(', ')}
                    </div>
                  </div>
                </div>
                
                <div 
                  className="rounded-lg p-6"
                  style={{
                    backgroundColor: '#f0fdf4',
                    border: '1px solid #bbf7d0'
                  }}
                >
                  <h5 style={{ 
                    fontSize: typography.sizes.sm, 
                    fontWeight: typography.weights.bold,
                    color: '#166534',
                    marginBottom: spacing.scale.sm
                  }}>
                    Complete Combined Prompt
                  </h5>
                  <p style={{ 
                    color: colors.text.primary, 
                    fontSize: typography.sizes.sm,
                    lineHeight: typography.lineHeights.relaxed,
                    whiteSpace: 'pre-wrap'
                  }}>
                    {results.data.combined_structured_script.full_prompt}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div 
              className="rounded-2xl p-10"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
              }}
            >
              <h4 style={{ 
                fontSize: typography.sizes.sectionTitle, 
                fontWeight: typography.weights.bold,
                color: colors.text.primary,
                marginBottom: spacing.scale['3xl']
              }}>
                Combined Sora Script
              </h4>
              <div 
                className="rounded-xl p-8"
                style={{
                  background: 'linear-gradient(to right, #f9fafb, #f3f4f6)',
                  border: `1px solid ${colors.borders.subtle}`
                }}
              >
                <p style={{ 
                  color: colors.text.primary, 
                  fontSize: typography.sizes.sm,
                  lineHeight: typography.lineHeights.relaxed,
                  whiteSpace: 'pre-wrap'
                }}>
                  {results.data.combined_sora_script}
                </p>
              </div>
            </div>
          )}

          {/* Combined Sora Video */}
          {results.data.combined_sora_video_job && (
            <div 
              className="rounded-2xl p-10"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
              }}
            >
              <SoraVideoPlayer 
                videoJob={results.data.combined_sora_video_job}
                onStatusChange={(status) => {
                  setResults(prev => {
                    if (!prev || prev.type !== 'multi') return prev
                    return {
                      ...prev,
                      data: {
                        ...prev.data,
                        combined_sora_video_job: {
                          ...prev.data.combined_sora_video_job,
                          status
                        }
                      }
                    }
                  })
                }}
              />
            </div>
          )}

          {/* Individual Videos Summary */}
          <div 
            className="rounded-2xl p-8"
            style={{
              backgroundColor: colors.background.section,
              border: `1px solid ${colors.borders.subtle}`,
              boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
            }}
          >
            <h4 style={{ 
              fontSize: typography.sizes.sectionTitle, 
              fontWeight: typography.weights.bold,
              color: colors.text.primary,
              marginBottom: spacing.scale['3xl']
            }}>
              Individual Videos Analyzed
            </h4>
            <div className="grid gap-4">
              {results.data.individual_results.map((result, index) => (
                <div 
                  key={result.video_id} 
                  className="rounded-xl p-5 transition-shadow"
                  style={{
                    background: 'linear-gradient(to right, #f9fafb, #f3f4f6)',
                    border: `1px solid ${colors.borders.subtle}`
                  }}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span style={{ 
                      fontSize: typography.sizes.sm, 
                      fontWeight: typography.weights.medium,
                      color: '#2563eb'
                    }}>
                      Video {index + 1}
                    </span>
                    <a 
                      href={result.post_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{ 
                        fontSize: typography.sizes.xs, 
                        color: '#2563eb',
                        textDecoration: 'none'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.textDecoration = 'underline'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.textDecoration = 'none'
                      }}
                    >
                      View on Instagram →
                    </a>
                  </div>
                  <p style={{ 
                    color: colors.text.primary, 
                    fontSize: typography.sizes.sm,
                    marginBottom: spacing.scale.sm
                  }}>
                    {result.original_text.substring(0, 100)}...
                  </p>
                  <div className="flex gap-4" style={{ fontSize: typography.sizes.xs, color: colors.text.muted }}>
                    <span>{result.views.toLocaleString()} views</span>
                    <span>{result.likes.toLocaleString()} likes</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InstagramTools
