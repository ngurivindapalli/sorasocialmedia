import { useState, useEffect } from 'react'
import { Video, FileText, Copy, Check, Play, Loader2, Sparkles, Image, Linkedin } from 'lucide-react'
import { api, API_URL } from '../utils/api'
import SoraVideoPlayer from '../components/SoraVideoPlayer'
import VideoGenerationLoader from '../components/VideoGenerationLoader'

function ContentCalendarDay2() {
  const [copied, setCopied] = useState(false)
  const [generatingVideo, setGeneratingVideo] = useState(false)
  const [videoResult, setVideoResult] = useState(null)
  const [generatingImage, setGeneratingImage] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
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
    hook: "Walk into office / soft B-roll",
    opener: "If you run a multi-location clinic, listen.",
    script: "Here's what we learned from 18 operator interviews: the clinics that convert 2x better aren't doing more follow-ups—they're doing smarter follow-ups. One operator we spoke to responds to leads within 4 minutes, and her conversion rate is 2.3x the clinic average. The difference? She asks one question first: 'What made you reach out today?'",
    metric: "2.3x better conversion rate",
    cta: "Say '60-day pilot' if you want the framework.",
    repurpose: "Short 10s cut as ad."
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleGenerateVideo = async () => {
    setGeneratingVideo(true)
    setError(null)
    setVideoResult(null)

    try {
      // Create a video prompt from the script
      const videoPrompt = `${content.opener}\n\n${content.script}\n\nVisual: ${content.hook}`

      // Calculate extensions needed for 45-second video
      // Base: 8 seconds, each extension: 7 seconds
      // Target: 45 seconds
      // Extensions needed: (45 - 8) / 7 = 5.28, so we need 6 extensions
      // Total: 8 + (6 * 7) = 50 seconds (close to 45)
      const targetDuration = 45
      const baseDuration = 8
      const extensionSeconds = 7
      const extensionsNeeded = Math.ceil((targetDuration - baseDuration) / extensionSeconds)
      const finalDuration = baseDuration + (extensionsNeeded * extensionSeconds)

      // Use Veo 3 for video generation
      const response = await api.post('/api/veo3/generate', {
        prompt: videoPrompt,
        duration: 8,
        resolution: '1280x720',
        max_extensions: extensionsNeeded // Automatically extend to reach target duration
      }, {
        timeout: 600000 // 10 minutes timeout for longer videos with extensions
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

  const handleGenerateImage = async () => {
    setGeneratingImage(true)
    setError(null)
    setGeneratedImage(null)

    try {
      // Create an image prompt from the script
      const imagePrompt = `${content.opener}\n\n${content.script}\n\nProfessional business image showing clinic operations, follow-up processes, or data visualization. Clean, modern, professional style.`

      const response = await api.post('/api/image/generate', {
        prompt: imagePrompt,
        model: 'nanobanana',
        size: '1024x1024',
        quality: 'standard',
        aspect_ratio: '16:9', // Video thumbnail style
        n: 1
      }, {
        timeout: 60000
      })

      const imageUrl = response.data.image_url || 
        (response.data.image_base64 ? `data:image/png;base64,${response.data.image_base64}` : null)
      
      if (imageUrl) {
        setGeneratedImage(imageUrl)
      }
    } catch (err) {
      console.error('Error generating image:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to generate image. Please try again.')
    } finally {
      setGeneratingImage(false)
    }
  }

  const fullScript = `HOOK: ${content.hook}\n\nOPENER: ${content.opener}\n\nSCRIPT (30s):\n${content.script}\n\nCTA: ${content.cta}\n\n---\nRepurpose: ${content.repurpose}`

  // Fetch LinkedIn connections on mount
  useEffect(() => {
    const fetchConnections = async () => {
      try {
        const response = await api.get('/api/connections')
        const linkedin = response.data.filter(conn => conn.platform === 'linkedin' && conn.is_active)
        setLinkedinConnections(linkedin)
      } catch (err) {
        console.error('Error fetching LinkedIn connections:', err)
      }
    }
    fetchConnections()
  }, [])

  const handlePostToLinkedIn = async (mediaType = 'image') => {
    if (linkedinConnections.length === 0) {
      setError('No LinkedIn connections found. Please connect your LinkedIn account in Settings first.')
      return
    }

    if (mediaType === 'image' && !generatedImage) {
      setError('Please generate an image first before posting to LinkedIn.')
      return
    }

    if (mediaType === 'video' && (!videoResult || videoResult.status !== 'completed')) {
      setError('Please wait for the video to finish generating before posting.')
      return
    }

    setPostingToLinkedIn(true)
    setError(null)
    setPostSuccess(null)

    try {
      const connectionIds = linkedinConnections.map(conn => conn.id)
      const postData = {
        connection_ids: connectionIds,
        caption: `${content.opener}\n\n${content.script}\n\n${content.cta}`,
        image_url: mediaType === 'image' ? generatedImage : null,
        video_url: mediaType === 'video' && videoResult?.video_url ? videoResult.video_url : null
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
          <h1 className="text-3xl font-bold text-[#111827] mb-2">Day 2 — 45s Native Video (Founder)</h1>
          <p className="text-[#6b7280]">Video script template for native social media content</p>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Video className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Hook</h2>
          </div>
          <div className="bg-[#f9fafb] rounded-lg p-4 mb-4">
            <p className="text-[#111827] leading-relaxed">{content.hook}</p>
          </div>
          <div className="text-sm text-[#6b7280] mb-4">
            <p><strong>Visual:</strong> Walk into office / soft B-roll footage</p>
          </div>
          <button
            onClick={() => copyToClipboard(content.hook)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            Copy Hook
          </button>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Play className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Opener</h2>
          </div>
          <div className="bg-[#f9fafb] rounded-lg p-4 mb-4">
            <p className="text-[#111827] text-lg leading-relaxed font-medium">{content.opener}</p>
          </div>
          <button
            onClick={() => copyToClipboard(content.opener)}
            className="flex items-center gap-2 px-3 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            Copy Opener
          </button>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Script (30s)</h2>
          </div>
          <div className="space-y-4">
            <div className="bg-[#f9fafb] rounded-lg p-4">
              <p className="text-[#111827] leading-relaxed">{content.script}</p>
            </div>
            <div className="bg-[#eff6ff] border border-[#bfdbfe] rounded-lg p-3">
              <p className="text-sm text-[#1e40af]">
                <strong>Key Metric:</strong> {content.metric}
              </p>
            </div>
          </div>
          <button
            onClick={() => copyToClipboard(content.script)}
            className="mt-4 flex items-center gap-2 px-3 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            Copy Script
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
            <h2 className="text-xl font-semibold text-white">Full Video Script</h2>
            <button
              onClick={() => copyToClipboard(fullScript)}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-white text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors font-medium"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              Copy Full Script
            </button>
          </div>
          <div className="bg-white rounded-lg p-4">
            <pre className="text-[#111827] whitespace-pre-wrap font-sans leading-relaxed">{fullScript}</pre>
          </div>
        </div>

        <div className="bg-[#1e293b] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Generate Media</h2>
          </div>
          <p className="text-white/80 text-sm mb-4">
            Generate a video or image based on this script using AI generation.
          </p>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={handleGenerateVideo}
              disabled={generatingVideo || (videoResult && (videoResult.status === 'queued' || videoResult.status === 'in_progress'))}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
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
            <button
              onClick={handleGenerateImage}
              disabled={generatingImage}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
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
          </div>
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Video Result */}
        {videoResult && (
          <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-[#111827] mb-4">Generated Video</h3>
            <div className="rounded-lg overflow-hidden border border-[#e5e7eb]">
              <SoraVideoPlayer 
                videoJob={videoResult}
                onStatusChange={(status, progress, videoUrl) => {
                  setVideoResult(prev => prev ? { ...prev, status, progress, video_url: videoUrl || prev.video_url } : null)
                  const isGenerating = status === 'queued' || status === 'in_progress'
                  setGeneratingVideo(isGenerating)
                }}
              />
            </div>
            {linkedinConnections.length > 0 && videoResult.status === 'completed' && videoResult.video_url && (
              <button
                onClick={() => handlePostToLinkedIn('video')}
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
                onClick={() => handlePostToLinkedIn('image')}
                disabled={postingToLinkedIn || !generatedImage}
                className="inline-flex items-center gap-2 px-4 py-2 bg-[#0077b5] text-white rounded-lg hover:bg-[#005885] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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

        {generatingVideo && <VideoGenerationLoader message="Generating your video..." />}

        <div className="mt-6 p-4 bg-[#fef3c7] border border-[#fbbf24] rounded-lg">
          <p className="text-sm text-[#92400e]">
            <strong>Production Notes:</strong> This is a 45-second native video. Keep it authentic and conversational. The hook should be visually engaging—consider B-roll of walking into the office or soft background footage. The founder should speak directly to camera with natural lighting.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ContentCalendarDay2
