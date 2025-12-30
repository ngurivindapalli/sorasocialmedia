import { useState, useEffect, useRef } from 'react'
import { Video, Play, Loader2, Send, Sparkles } from 'lucide-react'
import { api } from '../utils/api'
import SoraVideoPlayer from '../components/SoraVideoPlayer'
import VideoGenerationLoader from '../components/VideoGenerationLoader'
import design from '../../design.json'

function VeoVideo() {
  const [topic, setTopic] = useState('')
  const [duration, setDuration] = useState(8)
  const [maxExtensions, setMaxExtensions] = useState(0)
  const [llmProvider, setLlmProvider] = useState('openai')
  const [loading, setLoading] = useState(false)
  const [generatingVideo, setGeneratingVideo] = useState(false)
  const [videoResult, setVideoResult] = useState(null)
  const [error, setError] = useState(null)
  const [script, setScript] = useState(null)
  const messagesEndRef = useRef(null)

  // Design tokens
  const { colors, typography, spacing, layout } = design
  const maxContentWidth = layout.page.maxContentWidth
  const pagePaddingX = spacing.page.paddingXDesktop
  const sectionGap = spacing.page.sectionGap

  // Check if video is being generated
  useEffect(() => {
    if (videoResult && videoResult.status) {
      const isGenerating = videoResult.status === 'in_progress' || videoResult.status === 'queued'
      setGeneratingVideo(isGenerating)
    } else {
      setGeneratingVideo(false)
    }
  }, [videoResult])

  const handleGenerate = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic for your video')
      return
    }

    setLoading(true)
    setGeneratingVideo(true)
    setError(null)
    setVideoResult(null)
    setScript(null)

    try {
      // Use a very long timeout since video generation can take 2-5 minutes with extensions
      const response = await api.post('/api/veo3/generate-with-context', {
        topic: topic.trim(),
        duration: duration,
        max_extensions: maxExtensions,
        resolution: '1280x720',
        llm_provider: llmProvider,
        wait_for_completion: true
      }, {
        timeout: 600000 // 10 minutes timeout for video generation with extensions
      })

      setVideoResult(response.data)
      setScript(response.data?.script || null)
      
      if (response.data?.video_url) {
        console.log('Video generated successfully:', response.data.video_url)
        setGeneratingVideo(false)
      } else if (response.data?.status === 'in_progress' || response.data?.status === 'queued') {
        // Still generating, keep loading state
        setGeneratingVideo(true)
      } else {
        setGeneratingVideo(false)
      }
    } catch (err) {
      console.error('Error generating video:', err)
      // Only show error if it's not a timeout (timeout means it's still processing)
      if (err.code !== 'ECONNABORTED' && !err.message?.includes('timeout')) {
        setError(err.response?.data?.detail || err.message || 'Failed to generate video. Please try again.')
      } else {
        // Timeout - video might still be generating, show a message
        setError('Video generation is taking longer than expected. It may still be processing in the background. Please check back in a few minutes.')
      }
      setGeneratingVideo(false)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (!loading) {
        handleGenerate()
      }
    }
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
      {generatingVideo && <VideoGenerationLoader message="Generating your video with Veo 3..." />}
      
      <div 
        className="rounded-2xl overflow-hidden"
        style={{
          backgroundColor: colors.background.card,
          border: `1px solid ${colors.borders.subtle}`,
          borderRadius: '24px',
          boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
        }}
      >
        {/* Header */}
        <div 
          style={{
            borderBottom: `1px solid ${colors.borders.subtle}`,
            padding: spacing.scale['3xl']
          }}
        >
          <div className="flex items-center gap-3">
            <div 
              className="rounded-lg flex items-center justify-center"
              style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(to bottom right, #8b5cf6, #ec4899)'
              }}
            >
              <Video className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 style={{ 
                fontSize: typography.sizes.xl, 
                fontWeight: typography.weights.semibold,
                color: colors.text.primary
              }}>
                Veo Video Generation
              </h2>
              <p style={{ 
                color: colors.text.muted, 
                fontSize: typography.sizes.sm
              }}>
                Generate AI videos using your brand context from Mem0
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: spacing.scale['3xl'] }}>
          {/* Topic Input */}
          <div style={{ marginBottom: spacing.scale.xl }}>
            <label style={{ 
              display: 'block',
              fontSize: typography.sizes.sm, 
              fontWeight: typography.weights.medium,
              color: colors.text.primary,
              marginBottom: spacing.scale.sm
            }}>
              Video Topic
            </label>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter a topic for your video (e.g., 'Introduction to AI Marketing')"
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
              The script will be generated based on your brand context stored in Mem0
            </p>
          </div>

          {/* Settings Grid */}
          <div className="grid md:grid-cols-3 gap-6" style={{ marginBottom: spacing.scale.xl }}>
            {/* Duration */}
            <div>
              <label style={{ 
                display: 'block',
                fontSize: typography.sizes.sm, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm
              }}>
                Initial Duration (seconds)
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value))}
                className="w-full px-4 py-3 rounded-lg focus:outline-none"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  color: colors.text.primary,
                  fontSize: typography.sizes.md
                }}
                disabled={loading}
              >
                <option value={4}>4 seconds</option>
                <option value={6}>6 seconds</option>
                <option value={8}>8 seconds</option>
              </select>
            </div>

            {/* Extensions */}
            <div>
              <label style={{ 
                display: 'block',
                fontSize: typography.sizes.sm, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm
              }}>
                Extensions (7s each)
              </label>
              <select
                value={maxExtensions}
                onChange={(e) => setMaxExtensions(parseInt(e.target.value))}
                className="w-full px-4 py-3 rounded-lg focus:outline-none"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  color: colors.text.primary,
                  fontSize: typography.sizes.md
                }}
                disabled={loading}
              >
                <option value={0}>No extensions</option>
                <option value={1}>1 extension (+7s)</option>
                <option value={2}>2 extensions (+14s)</option>
                <option value={3}>3 extensions (+21s)</option>
                <option value={5}>5 extensions (+35s)</option>
                <option value={10}>10 extensions (+70s)</option>
              </select>
              <p style={{ 
                fontSize: typography.sizes.xs, 
                color: colors.text.lightMuted,
                marginTop: spacing.scale.xs
              }}>
                Final duration: {duration + (maxExtensions * 7)}s
              </p>
            </div>

            {/* LLM Provider */}
            <div>
              <label style={{ 
                display: 'block',
                fontSize: typography.sizes.sm, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm
              }}>
                Script Generator
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
                <option value="openai">OpenAI GPT-4</option>
                <option value="claude">Claude (Anthropic)</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {error && !generatingVideo && (
            <div 
              style={{
                padding: spacing.scale.md,
                marginBottom: spacing.scale.xl,
                backgroundColor: '#fee2e2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                color: '#991b1b',
                fontSize: typography.sizes.sm
              }}
            >
              {error}
            </div>
          )}

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={loading || generatingVideo || !topic.trim()}
            className="w-full py-3 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            style={{
              backgroundColor: (loading || generatingVideo || !topic.trim()) ? colors.borders.subtle : undefined,
              background: (loading || generatingVideo || !topic.trim()) ? colors.borders.subtle : 'linear-gradient(to right, #8b5cf6, #ec4899)',
              color: 'white',
              fontSize: typography.sizes.md,
              fontWeight: typography.weights.semibold
            }}
          >
            {(loading || generatingVideo) ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                {generatingVideo ? 'Generating Video...' : 'Starting Generation...'}
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate Video
              </>
            )}
          </button>

          {/* Generated Script */}
          {script && (
            <div style={{ marginTop: spacing.scale.xl }}>
              <h3 style={{ 
                fontSize: typography.sizes.lg, 
                fontWeight: typography.weights.semibold,
                color: colors.text.primary,
                marginBottom: spacing.scale.md
              }}>
                Generated Script
              </h3>
              <div 
                style={{
                  padding: spacing.scale.lg,
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  borderRadius: '12px',
                  color: colors.text.primary,
                  fontSize: typography.sizes.sm,
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.6'
                }}
              >
                {script}
              </div>
            </div>
          )}

          {/* Video Result */}
          {videoResult && videoResult.video_url && (
            <div style={{ marginTop: spacing.scale.xl }}>
              <h3 style={{ 
                fontSize: typography.sizes.lg, 
                fontWeight: typography.weights.semibold,
                color: colors.text.primary,
                marginBottom: spacing.scale.md
              }}>
                Generated Video
              </h3>
              <div style={{
                borderRadius: '12px',
                overflow: 'hidden',
                border: `1px solid ${colors.borders.subtle}`
              }}>
                <SoraVideoPlayer 
                  videoJob={{
                    job_id: videoResult.job_id || '',
                    status: videoResult.status || 'completed',
                    video_url: videoResult.video_url,
                    model: videoResult.model || 'veo-3',
                    progress: 100
                  }}
                />
              </div>
              {videoResult.final_duration && (
                <p style={{ 
                  fontSize: typography.sizes.sm, 
                  color: colors.text.muted,
                  marginTop: spacing.scale.sm
                }}>
                  Final duration: {videoResult.final_duration} seconds
                  {videoResult.extensions_completed > 0 && ` (${videoResult.extensions_completed} extensions applied)`}
                </p>
              )}
            </div>
          )}

          {/* Video Status (if still generating) */}
          {videoResult && !videoResult.video_url && videoResult.status && (
            <div style={{ marginTop: spacing.scale.xl }}>
              <div 
                style={{
                  padding: spacing.scale.lg,
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  borderRadius: '12px'
                }}
              >
                <div className="flex items-center gap-3">
                  <Loader2 className="w-5 h-5 animate-spin" style={{ color: colors.text.primary }} />
                  <div>
                    <p style={{ 
                      fontSize: typography.sizes.md, 
                      fontWeight: typography.weights.medium,
                      color: colors.text.primary
                    }}>
                      Video generation in progress...
                    </p>
                    <p style={{ 
                      fontSize: typography.sizes.sm, 
                      color: colors.text.muted,
                      marginTop: spacing.scale.xs
                    }}>
                      Status: {videoResult.status || 'processing'} | Job ID: {videoResult.job_id ? videoResult.job_id.substring(0, 50) + '...' : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default VeoVideo

