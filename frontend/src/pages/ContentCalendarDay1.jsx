import { useState, useEffect } from 'react'
import { Image, FileText, Copy, Check, Loader2, Sparkles, Video, Linkedin, Share2 } from 'lucide-react'
import { api, API_URL } from '../utils/api'
import SoraVideoPlayer from '../components/SoraVideoPlayer'
import VideoGenerationLoader from '../components/VideoGenerationLoader'

function ContentCalendarDay1() {
  const [copied, setCopied] = useState(false)
  const [generatingImage, setGeneratingImage] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [generatingVideo, setGeneratingVideo] = useState(false)
  const [videoResult, setVideoResult] = useState(null)
  const [error, setError] = useState(null)

  // Update generatingVideo state based on video status
  useEffect(() => {
    if (videoResult) {
      const isGenerating = videoResult.status === 'queued' || videoResult.status === 'in_progress'
      setGeneratingVideo(isGenerating)
    } else {
      setGeneratingVideo(false)
    }
  }, [videoResult])
  const [linkedinConnections, setLinkedinConnections] = useState([])
  const [postingToLinkedIn, setPostingToLinkedIn] = useState(false)
  const [postSuccess, setPostSuccess] = useState(null)

  const content = {
    headline: "We ran 18 operator interviews this month. Here's the single thing every healthy business is missing.",
    observation: "Every high-performing clinic we spoke to had one thing in common: they track lead conversion at the operator level, not just the clinic level.",
    examples: [
      "A 3-location practice discovered their top operator converts 2.3x better than their lowest—now they route leads accordingly.",
      "Another clinic found that follow-up timing (not just frequency) was the differentiator—their best operator responds within 4 minutes."
    ],
    cta: "Comment 'Notes' and I'll DM the short checklist.",
    repurpose: "Thread on X summarizing 3 excerpts."
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleGenerateImage = async () => {
    setGeneratingImage(true)
    setError(null)
    setGeneratedImage(null)

    try {
      // Create an image prompt from the headline and content
      const imagePrompt = `${content.headline}. Professional business image showing operator interviews, clinic operations, or data visualization. Clean, modern, professional style.`

      const response = await api.post('/api/image/generate', {
        prompt: imagePrompt,
        model: 'nanobanana', // or 'gemini-3-pro-image'
        size: '1024x1024',
        quality: 'standard',
        aspect_ratio: '1:1',
        n: 1
      }, {
        timeout: 60000 // 60 second timeout
      })

      if (response.data.image_url) {
        setGeneratedImage(response.data.image_url)
      } else if (response.data.image_base64) {
        // Convert base64 to blob URL if needed
        const imageUrl = `data:image/png;base64,${response.data.image_base64}`
        setGeneratedImage(imageUrl)
      }
    } catch (err) {
      console.error('Error generating image:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to generate image. Please try again.')
    } finally {
      setGeneratingImage(false)
    }
  }

  const handleGenerateVideo = async () => {
    setGeneratingVideo(true)
    setError(null)
    setVideoResult(null)

    try {
      // Create a video prompt from the headline and content
      const videoPrompt = `${content.headline}\n\n${content.observation}\n\nVisual: Professional business setting showing operator interviews, clinic operations, or data visualization. Clean, modern, professional style.`

      // Calculate extensions needed for target duration
      // Base: 8 seconds, each extension: 7 seconds
      // For Day 1, we want a short video (15 seconds total)
      const targetDuration = 15
      const baseDuration = 8
      const extensionSeconds = 7
      const extensionsNeeded = Math.ceil((targetDuration - baseDuration) / extensionSeconds)

      const response = await api.post('/api/veo3/generate', {
        prompt: videoPrompt,
        duration: 8,
        resolution: '1280x720',
        max_extensions: extensionsNeeded // Automatically extend to reach target duration
      }, {
        timeout: 300000 // 5 minutes timeout
      })

      setVideoResult({
        job_id: response.data.job_id,
        status: response.data.status || 'queued',
        model: 'veo-3',
        progress: 0
      })
    } catch (err) {
      console.error('Error generating video:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to generate video. Please try again.')
      setGeneratingVideo(false)
    }
  }

  const fullPost = `${content.headline}\n\n${content.observation}\n\n${content.examples.map((ex, i) => `• ${ex}`).join('\n')}\n\n${content.cta}\n\n---\nRepurpose: ${content.repurpose}`

  // Fetch LinkedIn connections on mount
  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const response = await api.get('/api/connections')
        console.log('All connections:', response.data)
        const linkedin = response.data.filter(conn => conn.platform === 'linkedin' && conn.is_active)
        console.log('LinkedIn connections:', linkedin)
        setLinkedinConnections(linkedin)
      } catch (err) {
        console.error('Error fetching LinkedIn connections:', err)
        // Still show button even if fetch fails
      }
    }
    fetchConnections()
  }, [])

  const handlePostToLinkedIn = async () => {
    if (linkedinConnections.length === 0) {
      setError('No LinkedIn connections found. Please connect your LinkedIn account in Settings first.')
      return
    }

    if (!generatedImage) {
      setError('Please generate an image first before posting to LinkedIn.')
      return
    }

    setPostingToLinkedIn(true)
    setError(null)
    setPostSuccess(null)

    try {
      const connectionIds = linkedinConnections.map(conn => conn.id)
      const postData = {
        connection_ids: connectionIds,
        caption: fullPost,
        image_url: generatedImage,
        video_url: null
      }

      const response = await api.post('/api/post/video', postData)
      
      if (response.data.success) {
        const postUrl = response.data.posts?.[0]?.post_url || response.data.posts?.[0]?.postUrl
        setPostSuccess(postUrl || 'Posted successfully!')
        setTimeout(() => setPostSuccess(null), 5000)
      } else {
        setError(response.data.errors?.[0] || response.data.error || 'Failed to post to LinkedIn')
      }
    } catch (err) {
      console.error('Error posting to LinkedIn:', err)
      setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Failed to post to LinkedIn. Please try again.')
    } finally {
      setPostingToLinkedIn(false)
    }
  }

  return (
    <div className="min-h-screen bg-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#111827] mb-2">Day 1 — Text + Image</h1>
          <p className="text-[#6b7280]">Content calendar template for social media posting</p>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Headline</h2>
          </div>
          <div className="bg-[#f9fafb] rounded-lg p-4 mb-4">
            <p className="text-[#111827] text-lg leading-relaxed">{content.headline}</p>
          </div>
          <button
            onClick={() => copyToClipboard(content.headline)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            Copy Headline
          </button>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Content</h2>
          </div>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-[#6b7280] mb-2">One-sentence observation:</p>
              <div className="bg-[#f9fafb] rounded-lg p-4">
                <p className="text-[#111827] leading-relaxed">{content.observation}</p>
              </div>
            </div>
            <div>
              <p className="text-sm font-medium text-[#6b7280] mb-2">2 bullet examples (real but anonymous):</p>
              <div className="bg-[#f9fafb] rounded-lg p-4 space-y-2">
                {content.examples.map((example, index) => (
                  <p key={index} className="text-[#111827] leading-relaxed">• {example}</p>
                ))}
              </div>
            </div>
          </div>
          <button
            onClick={() => copyToClipboard(`${content.observation}\n\n${content.examples.map((ex, i) => `• ${ex}`).join('\n')}`)}
            className="mt-4 flex items-center gap-2 px-3 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            Copy Content
          </button>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Call to Action</h2>
          </div>
          <div className="bg-[#f9fafb] rounded-lg p-4 mb-4">
            <p className="text-[#111827] text-lg leading-relaxed">{content.cta}</p>
          </div>
          <button
            onClick={() => copyToClipboard(content.cta)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            Copy CTA
          </button>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Repurpose</h2>
          </div>
          <div className="bg-[#f0f9ff] border border-[#bae6fd] rounded-lg p-4 mb-4">
            <p className="text-[#111827] leading-relaxed">{content.repurpose}</p>
          </div>
        </div>

        <div className="bg-[#1e293b] rounded-lg shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Full Post</h2>
            <button
              onClick={() => copyToClipboard(fullPost)}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-white text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors font-medium"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              Copy Full Post
            </button>
          </div>
          <div className="bg-white rounded-lg p-4">
            <pre className="text-[#111827] whitespace-pre-wrap font-sans leading-relaxed">{fullPost}</pre>
          </div>
        </div>

        <div className="bg-[#1e293b] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Generate Media</h2>
          </div>
          <p className="text-white/80 text-sm mb-4">
            Generate an image or video based on this content using AI generation.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={handleGenerateImage}
              disabled={generatingImage}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingImage ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Image className="w-5 h-5" />
                  Generate Image
                </>
              )}
            </button>
            <button
              onClick={handleGenerateVideo}
              disabled={generatingVideo || (videoResult && (videoResult.status === 'queued' || videoResult.status === 'in_progress'))}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {generatingVideo || (videoResult && (videoResult.status === 'queued' || videoResult.status === 'in_progress')) ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Video className="w-5 h-5" />
                  Generate Video
                </>
              )}
            </button>
          </div>
          {/* Always show LinkedIn posting option */}
          <div className="mt-4 pt-4 border-t border-white/20">
            <button
              onClick={handlePostToLinkedIn}
              disabled={postingToLinkedIn || !generatedImage}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#0077b5] hover:bg-[#005885] text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title={!generatedImage ? 'Generate an image first to post to LinkedIn' : linkedinConnections.length === 0 ? 'Connect LinkedIn in Settings first' : 'Post to LinkedIn'}
            >
              {postingToLinkedIn ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Posting to LinkedIn...
                </>
              ) : (
                <>
                  <Linkedin className="w-5 h-5" />
                  {linkedinConnections.length > 0 
                    ? (generatedImage ? 'Post to LinkedIn' : 'Generate Image to Post')
                    : 'Connect LinkedIn Account (Settings → Social Media)'}
                </>
              )}
            </button>
            {linkedinConnections.length === 0 && (
              <p className="mt-2 text-xs text-white/60 text-center">
                No LinkedIn connection found. Go to Settings to connect your account.
              </p>
            )}
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Generated Image */}
        {generatedImage && (
          <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-[#111827] mb-4">Generated Image</h3>
            <div className="rounded-lg overflow-hidden border border-[#e5e7eb]">
              <img 
                src={generatedImage.startsWith('http') || generatedImage.startsWith('data:') ? generatedImage : `${API_URL}${generatedImage}`}
                alt="Generated content image"
                className="w-full h-auto"
                onError={(e) => {
                  console.error('Image load error:', e);
                  console.error('Image URL:', generatedImage);
                }}
              />
            </div>
            <div className="mt-4 flex flex-wrap gap-3">
              <a
                href={generatedImage.startsWith('http') || generatedImage.startsWith('data:') ? generatedImage : `${API_URL}${generatedImage}`}
                download={generatedImage.startsWith('data:') ? 'generated-image.png' : undefined}
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#1e293b] text-white rounded-lg hover:bg-[#334155] transition-colors"
              >
                <Image className="w-4 h-4" />
                Download Image
              </a>
              <button
                onClick={handlePostToLinkedIn}
                disabled={postingToLinkedIn || !generatedImage}
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#0077b5] text-white rounded-lg hover:bg-[#005885] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title={!generatedImage ? 'Generate an image first' : linkedinConnections.length === 0 ? 'Connect LinkedIn in Settings' : 'Post to LinkedIn'}
              >
                {postingToLinkedIn ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Posting...
                  </>
                ) : (
                  <>
                    <Linkedin className="w-4 h-4" />
                    {linkedinConnections.length > 0 ? 'Post to LinkedIn' : 'Connect LinkedIn First'}
                  </>
                )}
              </button>
            </div>
            {postSuccess && (
              <div className="mt-3 p-3 bg-green-100 border border-green-300 rounded-lg text-green-700 text-sm">
                ✓ Posted successfully! {typeof postSuccess === 'string' && postSuccess.includes('linkedin.com') && (
                  <a href={postSuccess} target="_blank" rel="noopener noreferrer" className="underline ml-1">View post</a>
                )}
              </div>
            )}
          </div>
        )}

        {/* Generated Video */}
        {videoResult && (
          <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-[#111827] mb-4">Generated Video</h3>
            <div className="rounded-lg overflow-hidden border border-[#e5e7eb]">
              <SoraVideoPlayer 
                videoJob={videoResult}
                onStatusChange={(status, progress, videoUrl) => {
                  // Update videoResult with new status
                  setVideoResult(prev => prev ? { ...prev, status, progress, video_url: videoUrl || prev.video_url } : null)
                  // Update generatingVideo state
                  const isGenerating = status === 'queued' || status === 'in_progress'
                  setGeneratingVideo(isGenerating)
                }}
              />
            </div>
            {linkedinConnections.length > 0 && videoResult.status === 'completed' && videoResult.video_url && (
              <button
                onClick={async () => {
                  setPostingToLinkedIn(true)
                  setError(null)
                  try {
                    const connectionIds = linkedinConnections.map(conn => conn.id || parseInt(conn.id))
                    const response = await api.post('/api/post/video', {
                      connection_ids: connectionIds,
                      caption: fullPost,
                      video_url: videoResult.video_url
                    })
                    if (response.data.success) {
                      setPostSuccess(response.data.posts?.[0]?.post_url || 'Posted successfully!')
                    } else {
                      setError(response.data.errors?.[0] || 'Failed to post')
                    }
                  } catch (err) {
                    setError(err.response?.data?.detail || 'Failed to post')
                  } finally {
                    setPostingToLinkedIn(false)
                  }
                }}
                disabled={postingToLinkedIn}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-[#0077b5] text-white rounded-lg hover:bg-[#005885] transition-colors disabled:opacity-50"
              >
                {postingToLinkedIn ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Posting...
                  </>
                ) : (
                  <>
                    <Linkedin className="w-4 h-4" />
                    Post Video to LinkedIn
                  </>
                )}
              </button>
            )}
          </div>
        )}

        {generatingVideo && <VideoGenerationLoader message="Generating your video..." />}

        <div className="mt-6 p-4 bg-[#fef3c7] border border-[#fbbf24] rounded-lg">
          <p className="text-sm text-[#92400e]">
            <strong>Note:</strong> This post should be paired with a relevant image. Consider using a chart, infographic, or behind-the-scenes photo that relates to operator interviews or clinic operations.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ContentCalendarDay1
