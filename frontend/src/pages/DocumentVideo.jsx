import { useState, useEffect } from 'react'
import { FileText, Video, Loader2, Sparkles } from 'lucide-react'
import axios from 'axios'
import DocumentUpload from '../components/DocumentUpload'
import SoraVideoPlayer from '../components/SoraVideoPlayer'
import ScriptApprovalModal from '../components/ScriptApprovalModal'
import VideoOptionsSelector from '../components/VideoOptionsSelector'
import { contextStorage } from '../utils/contextStorage'
import { authUtils } from '../utils/auth'
import design from '../../design.json'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function DocumentVideo() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [generatingVideo, setGeneratingVideo] = useState(false)
  const [videoResult, setVideoResult] = useState(null)
  const [error, setError] = useState(null)
  const [showScriptApproval, setShowScriptApproval] = useState(false)
  const [showVideoOptions, setShowVideoOptions] = useState(false)
  const [videoOptions, setVideoOptions] = useState([])
  const [selectedOption, setSelectedOption] = useState(null)
  const [currentScript, setCurrentScript] = useState(null)
  const [pendingVideoGeneration, setPendingVideoGeneration] = useState(null)
  const [videoModel, setVideoModel] = useState('sora-2') // 'sora-2' or 'veo-3'

  // Design tokens
  const { colors, typography, spacing, layout } = design
  const maxContentWidth = layout.page.maxContentWidth
  const pagePaddingX = spacing.page.paddingXDesktop
  const sectionGap = spacing.page.sectionGap

  // Check if video is being generated
  const checkVideoStatus = () => {
    if (videoResult?.video_job) {
      const job = videoResult.video_job
      const isGenerating = job.status === 'queued' || job.status === 'in_progress'
      setGeneratingVideo(isGenerating)
    } else {
      setGeneratingVideo(false)
    }
  }

  useEffect(() => {
    checkVideoStatus()
  }, [videoResult])

  // Save context when documents change
  useEffect(() => {
    if (documents.length > 0) {
      const documentIds = documents.map(doc => doc.id)
      contextStorage.saveContext('document_ids', documentIds)
    }
  }, [documents])

  // Load saved context on mount
  useEffect(() => {
    const savedDocIds = contextStorage.getContext('document_ids')
    if (savedDocIds && Array.isArray(savedDocIds)) {
      // Optionally restore document IDs (if documents are still available)
      console.log('[DocumentVideo] Loaded saved context:', savedDocIds)
    }
  }, [])

  const handleGenerateVideo = async () => {
    // Validate inputs - only require documents, AI decides everything else
    if (documents.length === 0) {
      setError('Please upload at least one document to generate a video')
      return
    }

    setLoading(true)
    setError(null)
    setVideoResult(null)
    setShowScriptApproval(false)
    setShowVideoOptions(false)

    try {
      console.log('[DocumentVideo] AI is analyzing documents and deciding what videos to create...')
      
      // Save context
      const documentIds = documents.map(doc => doc.id)
      contextStorage.saveContext('document_ids', documentIds)
      
      // First, get video options (pass video model so options respect Veo 3 constraints)
      try {
        const optionsResponse = await axios.post(`${API_URL}/api/video/options`, {
          document_ids: documentIds,
          num_options: 3,
          video_model: videoModel // Pass selected video model
        }, {
          timeout: 120000 // 2 minute timeout
        })
        
        if (optionsResponse.data.options && optionsResponse.data.options.length > 0) {
          setVideoOptions(optionsResponse.data.options)
          setShowVideoOptions(true)
          setLoading(false)
          return // Wait for user to select an option
        }
      } catch (optionsError) {
        console.warn('[DocumentVideo] Could not generate options, proceeding with single script:', optionsError)
        // Continue with single script generation
      }

      // If no options or options failed, proceed with single script
      await generateVideoWithOption(null)
      
    } catch (err) {
      console.error('[DocumentVideo] Error:', err)
      handleError(err)
      setLoading(false)
    }
  }

  const handleOptionSelect = async (option) => {
    setSelectedOption(option)
    setShowVideoOptions(false)
    setLoading(true)
    
    // Save selected option to context
    contextStorage.saveContext('selected_video_option', option)
    
    // Generate video with selected option
    await generateVideoWithOption(option)
  }

  const generateVideoWithOption = async (option) => {
    try {
      const documentIds = documents.map(doc => doc.id)
      
      // Build request payload with selected option or let AI decide
      const requestPayload = {
        document_ids: documentIds,
        video_model: videoModel // Include selected video model
      }
      
      if (option) {
        requestPayload.topic = option.topic
        requestPayload.duration = option.duration
        requestPayload.target_audience = option.target_audience
        requestPayload.key_message = option.key_message
      }

      console.log('[DocumentVideo] Request payload:', requestPayload)
      console.log('[DocumentVideo] Selected video model:', videoModel)

      const response = await axios.post(`${API_URL}/api/video/from-documents`, requestPayload, {
        timeout: 600000 // 10 minute timeout
      })

      console.log('[DocumentVideo] Video generation response:', response.data)
      
      // Save full result to context
      contextStorage.saveContext('last_video_result', response.data)
      
      // Show script approval modal before proceeding
      setCurrentScript(response.data.script)
      setPendingVideoGeneration(response.data)
      setShowScriptApproval(true)
      setLoading(false)
      
    } catch (err) {
      console.error('[DocumentVideo] Error generating video:', err)
      handleError(err)
      setLoading(false)
    }
  }

  const handleScriptApproval = (approved, editedScript = null, videoModel = 'sora-2') => {
    if (approved) {
      // Use edited script if provided, otherwise use original
      const finalScript = editedScript || currentScript
      
      // Generate video with the selected model
      generateVideoFromScript(finalScript, videoModel)
    } else {
      // User rejected - they can edit and try again
      setShowScriptApproval(false)
      setPendingVideoGeneration(null)
    }
  }

  const generateVideoFromScript = async (script, videoModel) => {
    setLoading(true)
    setShowScriptApproval(false)
    setError(null)

    try {
      const documentIds = documents.map(doc => doc.id)
      
      // Call backend to generate video with approved script and selected model
      console.log('[DocumentVideo] Generating video with approved script')
      console.log('[DocumentVideo] Video model:', videoModel)
      console.log('[DocumentVideo] Script length:', script.length)
      
      const response = await axios.post(`${API_URL}/api/video/from-documents`, {
        document_ids: documentIds,
        script: script,
        video_model: videoModel,
        approved: true
      }, {
        timeout: videoModel === 'veo-3' ? 600000 : 300000 // Longer timeout for Veo 3
      })

      console.log('[DocumentVideo] Video generation response:', response.data)
      
      setVideoResult(response.data)
      
      // Set generatingVideo based on video job status
      if (response.data.video_job) {
        const jobStatus = response.data.video_job.status
        setGeneratingVideo(jobStatus === 'queued' || jobStatus === 'in_progress')
      } else {
        setGeneratingVideo(false)
      }
      
      // Save approved script to context
      contextStorage.saveContext('approved_script', script)
      contextStorage.saveContext('selected_video_model', videoModel)
      
    } catch (err) {
      console.error('[DocumentVideo] Error generating video:', err)
      handleError(err)
    } finally {
      setLoading(false)
    }
  }

  const handleScriptEdit = (editedScript) => {
    setCurrentScript(editedScript)
    // Save edited script to context
    contextStorage.saveContext('edited_script', editedScript)
  }

  const handleError = (err) => {
    console.error('[DocumentVideo] Error:', err)
    
    // Extract error message properly - handle both string and object responses
    let errorMessage = 'Failed to generate video. Please try again.'
    
    if (err.response?.data?.detail) {
      const detail = err.response.data.detail
      if (typeof detail === 'string') {
        errorMessage = detail
      } else if (Array.isArray(detail)) {
        // Handle Pydantic validation errors array
        errorMessage = detail.map((error) => {
          const loc = Array.isArray(error.loc) ? error.loc.slice(1).join('.') : 'field'
          return `${loc}: ${error.msg || 'Invalid value'}`
        }).join(', ')
      } else if (typeof detail === 'object' && detail !== null) {
        // Handle single validation error object
        const loc = Array.isArray(detail.loc) ? detail.loc.slice(1).join('.') : 'field'
        errorMessage = `${loc}: ${detail.msg || 'Invalid value'}`
      } else {
        // Fallback: convert to string
        errorMessage = String(detail)
      }
    } else if (err.message) {
      errorMessage = err.message
    }
    
    setError(errorMessage)
    setGeneratingVideo(false)
  }

  return (
    <>
      {/* Video Options Selector */}
      <VideoOptionsSelector
        options={videoOptions}
        onSelect={handleOptionSelect}
        isOpen={showVideoOptions}
      />

      {/* Script Approval Modal */}
      <ScriptApprovalModal
        script={currentScript || ''}
        onApprove={(selectedModel) => handleScriptApproval(true, null, selectedModel || videoModel)}
        onReject={() => handleScriptApproval(false)}
        onEdit={handleScriptEdit}
        isOpen={showScriptApproval}
        defaultVideoModel={videoModel}
      />

      {/* Full-screen loading overlay - only during initial script generation */}
      {loading && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-[#111] border border-gray-800 rounded-3xl p-12 max-w-md w-full mx-6">
            <div className="flex flex-col items-center text-center space-y-6">
              <div className="relative">
                <Loader2 className="w-16 h-16 text-white animate-spin" />
                <Video className="w-8 h-8 text-white/50 absolute inset-0 m-auto" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-white">Generating script...</h3>
                <p className="text-sm text-gray-400">This may take a few moments. Please don't close this window.</p>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden max-w-md">
                <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 animate-pulse" style={{ width: '70%' }} />
              </div>
              <div className="flex gap-4 text-xs text-gray-500">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  <span className="text-white">Creating script</span>
                </div>
                <div className="flex items-center gap-2">
                  <Video className="w-4 h-4" />
                  <span>Generating video</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
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
      {/* Header */}
      <div className="mb-8">
        <h1 style={{ 
          fontSize: typography.sizes.pageTitle, 
          fontWeight: typography.weights.bold,
          color: colors.text.primary,
          marginBottom: spacing.scale.md,
          fontFamily: typography.fontFamilies.heading
        }}>
          Create Marketing Video from Documents
        </h1>
        <p style={{ 
          fontSize: typography.sizes.md, 
          color: colors.text.muted,
          lineHeight: typography.lineHeights.relaxed,
          fontFamily: typography.fontFamilies.body
        }}>
          Upload your documents and let AI automatically analyze the content to create the best marketing and educational videos tailored to your brand and messaging.
        </p>
      </div>

      {/* Document Upload Section */}
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
        <div className="flex items-center gap-3 mb-4">
          <FileText className="w-6 h-6" style={{ color: colors.text.primary }} />
          <h2 style={{ 
            fontSize: typography.sizes.sectionTitle, 
            fontWeight: typography.weights.semibold,
            color: colors.text.primary,
            fontFamily: typography.fontFamilies.heading
          }}>
            Step 1: Upload Documents
          </h2>
        </div>
        <p style={{ 
          fontSize: typography.sizes.sm, 
          color: colors.text.muted,
          marginBottom: spacing.scale.md,
          fontFamily: typography.fontFamilies.body
        }}>
          Upload PDF, DOCX, or TXT files containing your brand content, marketing materials, product info, or any context you want to incorporate into the video.
        </p>
        <DocumentUpload 
          onDocumentsChange={setDocuments}
          existingDocuments={documents}
        />
      </div>

      {/* Video Model Selection - Show only when documents are uploaded */}
      {documents.length > 0 && (
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
          <div className="flex items-center gap-3 mb-4">
            <Video className="w-6 h-6" style={{ color: colors.text.primary }} />
            <h2 style={{ 
              fontSize: typography.sizes.sectionTitle, 
              fontWeight: typography.weights.semibold,
              color: colors.text.primary,
              fontFamily: typography.fontFamilies.heading
            }}>
              Step 2: Choose Video Generation Model
            </h2>
          </div>
          <p style={{ 
            fontSize: typography.sizes.sm, 
            color: colors.text.muted,
            marginBottom: spacing.scale.lg,
            fontFamily: typography.fontFamilies.body
          }}>
            Select your video generation model. This choice will determine the duration constraints for script generation.
          </p>
          
          <div className="grid md:grid-cols-2 gap-4">
            {/* Sora 2 Option */}
            <button
              onClick={() => setVideoModel('sora-2')}
              className="p-6 rounded-xl border-2 transition-all text-left"
              style={{
                borderColor: videoModel === 'sora-2' 
                  ? layout.navbar.primaryCta.background 
                  : colors.borders.subtle,
                backgroundColor: videoModel === 'sora-2' 
                  ? `${layout.navbar.primaryCta.background}10` 
                  : colors.background.section,
                cursor: 'pointer'
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 style={{ 
                  fontSize: typography.sizes.lg, 
                  fontWeight: typography.weights.semibold,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamilies.heading
                }}>
                  Sora 2 (OpenAI)
                </h3>
                {videoModel === 'sora-2' && (
                  <div className="w-5 h-5 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: layout.navbar.primaryCta.background }}>
                    <span style={{ color: layout.navbar.primaryCta.textColor, fontSize: '12px' }}>✓</span>
                  </div>
                )}
              </div>
              <p style={{ 
                fontSize: typography.sizes.sm, 
                color: colors.text.muted,
                marginBottom: spacing.scale.sm,
                fontFamily: typography.fontFamilies.body
              }}>
                Fast generation, optimized for short-form content
              </p>
              <ul style={{ 
                listStyle: 'none',
                padding: 0,
                margin: 0,
                fontSize: typography.sizes.xs,
                color: colors.text.muted,
                fontFamily: typography.fontFamilies.body
              }}>
                <li style={{ marginBottom: spacing.scale.xs }}>• Duration: 4, 8, or 12 seconds only</li>
                <li style={{ marginBottom: spacing.scale.xs }}>• Faster generation time</li>
                <li>• Best for quick hooks and teasers</li>
              </ul>
            </button>

            {/* Veo 3 Option */}
            <button
              onClick={() => setVideoModel('veo-3')}
              className="p-6 rounded-xl border-2 transition-all text-left"
              style={{
                borderColor: videoModel === 'veo-3' 
                  ? layout.navbar.primaryCta.background 
                  : colors.borders.subtle,
                backgroundColor: videoModel === 'veo-3' 
                  ? `${layout.navbar.primaryCta.background}10` 
                  : colors.background.section,
                cursor: 'pointer'
              }}
            >
              <div className="flex items-center justify-between mb-3">
                <h3 style={{ 
                  fontSize: typography.sizes.lg, 
                  fontWeight: typography.weights.semibold,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamilies.heading
                }}>
                  Veo 3 (Google)
                </h3>
                {videoModel === 'veo-3' && (
                  <div className="w-5 h-5 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: layout.navbar.primaryCta.background }}>
                    <span style={{ color: layout.navbar.primaryCta.textColor, fontSize: '12px' }}>✓</span>
                  </div>
                )}
              </div>
              <p style={{ 
                fontSize: typography.sizes.sm, 
                color: colors.text.muted,
                marginBottom: spacing.scale.sm,
                fontFamily: typography.fontFamilies.body
              }}>
                High-quality, longer videos with flexible duration
              </p>
              <ul style={{ 
                listStyle: 'none',
                padding: 0,
                margin: 0,
                fontSize: typography.sizes.xs,
                color: colors.text.muted,
                fontFamily: typography.fontFamilies.body
              }}>
                <li style={{ marginBottom: spacing.scale.xs }}>• Duration: 4-148 seconds (8s initial + extensions)</li>
                <li style={{ marginBottom: spacing.scale.xs }}>• Higher quality output</li>
                <li>• Best for detailed, value-rich content</li>
              </ul>
            </button>
          </div>
          
          {videoModel === 'veo-3' && (
            <div 
              className="mt-4 p-4 rounded-lg"
              style={{
                backgroundColor: '#dbeafe',
                border: '1px solid #93c5fd',
                color: '#1e40af'
              }}
            >
              <p style={{ fontSize: typography.sizes.sm, fontFamily: typography.fontFamilies.body }}>
                <strong>✓ Veo 3 Selected:</strong> The AI will create longer, detailed scripts (40-148 seconds recommended). 
                Videos start at 8 seconds and are automatically extended in 7-second increments to reach the target duration. 
                Maximum length: 148 seconds (8s initial + 20 extensions of 7s each).
              </p>
            </div>
          )}
        </div>
      )}

      {/* AI-Powered Generation Notice */}
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
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-6 h-6" style={{ color: colors.text.primary }} />
          <h2 style={{ 
            fontSize: typography.sizes.sectionTitle, 
            fontWeight: typography.weights.semibold,
            color: colors.text.primary,
            fontFamily: typography.fontFamilies.heading
          }}>
            AI-Powered Video Generation
          </h2>
        </div>
        <p style={{ 
          fontSize: typography.sizes.md, 
          color: colors.text.primary,
          marginBottom: spacing.scale.md,
          lineHeight: typography.lineHeights.relaxed,
          fontFamily: typography.fontFamilies.body
        }}>
          Our AI will automatically analyze your documents and decide:
        </p>
        <ul style={{ 
          listStyle: 'none',
          padding: 0,
          margin: 0,
          fontSize: typography.sizes.sm,
          color: colors.text.muted,
          lineHeight: typography.lineHeights.relaxed,
          fontFamily: typography.fontFamilies.body
        }}>
          <li style={{ marginBottom: spacing.scale.sm }}>• <strong>Best video topics</strong> based on your content</li>
          <li style={{ marginBottom: spacing.scale.sm }}>• <strong>Optimal duration</strong> for maximum engagement</li>
          <li style={{ marginBottom: spacing.scale.sm }}>• <strong>Target audience</strong> that would benefit most</li>
          <li style={{ marginBottom: spacing.scale.sm }}>• <strong>Key messages</strong> that will resonate best</li>
          <li>• <strong>LinkedIn optimization</strong> for professional content</li>
        </ul>
      </div>

      {/* Generate Button */}
      <div className="mb-8">
        <button
          onClick={handleGenerateVideo}
          disabled={loading || generatingVideo || documents.length === 0}
          className="w-full py-4 px-6 rounded-lg font-medium transition-all flex items-center justify-center gap-3"
          style={{
            backgroundColor: (loading || generatingVideo || documents.length === 0) 
              ? colors.borders.subtle 
              : layout.navbar.primaryCta.background,
            color: (loading || generatingVideo || documents.length === 0)
              ? colors.text.muted
              : layout.navbar.primaryCta.textColor,
            fontSize: typography.sizes.md,
            fontWeight: typography.weights.semibold,
            fontFamily: typography.fontFamilies.body,
            cursor: (loading || generatingVideo || documents.length === 0) ? 'not-allowed' : 'pointer',
            opacity: (loading || generatingVideo || documents.length === 0) ? 0.6 : 1
          }}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Generating Video...</span>
            </>
          ) : generatingVideo ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Video Generation in Progress...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              <span>Generate Marketing Video</span>
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div 
          className="rounded-lg p-4 mb-8"
          style={{
            backgroundColor: '#fee2e2',
            border: '1px solid #fecaca',
            color: '#991b1b'
          }}
        >
          <p style={{ fontSize: typography.sizes.sm }}>
            {typeof error === 'string' ? error : JSON.stringify(error, null, 2)}
          </p>
        </div>
      )}

      {/* Video Result */}
      {videoResult && (
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
          <h3 style={{ 
            fontSize: typography.sizes.sectionTitle, 
            fontWeight: typography.weights.semibold,
            color: colors.text.primary,
            marginBottom: spacing.scale['2xl'],
            fontFamily: typography.fontFamilies.heading
          }}>
            Generated Video
          </h3>

          {/* Video Script */}
          {videoResult.script && (
            <div className="mb-6">
              <h4 style={{ 
                fontSize: typography.sizes.md, 
                fontWeight: typography.weights.medium,
                color: colors.text.primary,
                marginBottom: spacing.scale.sm,
                fontFamily: typography.fontFamilies.heading
              }}>
                Video Script
              </h4>
              <div 
                className="rounded-lg p-4"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  fontSize: typography.sizes.sm,
                  color: colors.text.primary,
                  lineHeight: typography.lineHeights.relaxed,
                  fontFamily: typography.fontFamilies.body,
                  whiteSpace: 'pre-wrap'
                }}
              >
                {videoResult.script}
              </div>
            </div>
          )}

          {/* Video Player */}
          {videoResult.video_job && (
            <div>
              <SoraVideoPlayer
                videoJob={videoResult.video_job}
                onStatusChange={(status, progress, video_url) => {
                  // Update video job status
                  setVideoResult(prev => ({
                    ...prev,
                    video_job: {
                      ...prev.video_job,
                      status: status,
                      progress: progress || prev.video_job?.progress || 0,
                      video_url: video_url || prev.video_job?.video_url
                    }
                  }))
                  
                  // Update generatingVideo state based on status
                  if (status === 'completed' || status === 'failed') {
                    setGeneratingVideo(false)
                  } else if (status === 'queued' || status === 'in_progress') {
                    setGeneratingVideo(true)
                  }
                }}
              />
            </div>
          )}
        </div>
      )}
      </div>
    </>
  )
}

export default DocumentVideo

