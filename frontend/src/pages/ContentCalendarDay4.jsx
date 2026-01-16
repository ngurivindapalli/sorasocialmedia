import { useState, useEffect } from 'react'
import { FileText, Copy, Check, BookOpen, Loader2, Sparkles, Image, Video, Linkedin } from 'lucide-react'
import { api, API_URL } from '../utils/api'
import SoraVideoPlayer from '../components/SoraVideoPlayer'
import VideoGenerationLoader from '../components/VideoGenerationLoader'

function ContentCalendarDay4() {
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
    headline: "Operator Field Note: Why follow-ups kill chair utilization — 7 real patterns",
    sections: [
      {
        observation: "Pattern 1: The 'We'll Call You Back' Trap",
        example: "A clinic we worked with had 3 operators who would say 'I'll call you back in an hour' but never did. Their no-show rate was 40% higher than operators who scheduled immediately.",
        solution: "Solution: Train operators to book the appointment during the first call. If they can't, set a calendar reminder that triggers a text 5 minutes before the callback time."
      },
      {
        observation: "Pattern 2: Generic Follow-Up Messages",
        example: "One clinic sent the same 'Just checking in!' message to every lead. Their conversion dropped 23% after the first week because leads felt like they were being spammed.",
        solution: "Solution: Personalize every follow-up. Reference something from the initial conversation: 'You mentioned you're looking for evening appointments—we just opened up 3 slots this week.'"
      },
      {
        observation: "Pattern 3: Following Up Too Fast",
        example: "A multi-location practice had operators calling leads 3 times in the first 24 hours. Their lead-to-appointment rate was actually lower than clinics that waited 48 hours between touches.",
        solution: "Solution: Space follow-ups based on lead source. Warm referrals: 24 hours. Cold leads: 48-72 hours. Give people time to process and respond."
      },
      {
        observation: "Pattern 4: No Value in the Follow-Up",
        example: "We analyzed 200 follow-up sequences and found that 78% of them were just 'Are you still interested?' with no new information or value proposition.",
        solution: "Solution: Every follow-up should add value. Share a patient success story, offer a limited-time incentive, or provide educational content about the treatment they inquired about."
      },
      {
        observation: "Pattern 5: Following Up on the Wrong Leads",
        example: "One clinic spent 80% of their follow-up time on leads who said 'maybe next year' while ignoring leads who asked specific questions about pricing and availability.",
        solution: "Solution: Score leads based on engagement. Prioritize follow-ups for leads who: asked specific questions, visited pricing pages, or engaged with multiple pieces of content."
      },
      {
        observation: "Pattern 6: Inconsistent Follow-Up Cadence",
        example: "A 5-location practice had no standardized follow-up process. Some operators followed up 2x, others 7x. The inconsistency confused leads and hurt brand perception.",
        solution: "Solution: Create a standardized follow-up sequence: Day 1 (immediate), Day 3 (value-add), Day 7 (final touch). Document it and train every operator on the same process."
      },
      {
        observation: "Pattern 7: Not Tracking What Works",
        example: "Most clinics we interviewed couldn't tell us which follow-up messages converted best. They were doing the same thing for months without measuring results.",
        solution: "Solution: Track every follow-up. A/B test message types, timing, and channels. Double down on what converts and eliminate what doesn't."
      }
    ],
    cta: "I'll send the 1-page playbook — comment 'playbook'.",
    repurpose: "Gated Execution Gap Index snippet."
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
      // Create an image prompt from the headline
      const imagePrompt = `${content.headline}. Professional business image showing clinic operations, follow-up processes, or data visualization. Clean, modern, professional style suitable for a long-form article header.`

      const response = await api.post('/api/image/generate', {
        prompt: imagePrompt,
        model: 'nanobanana',
        size: '1024x1024',
        quality: 'standard',
        aspect_ratio: '16:9', // Better for article headers
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

  const handleGenerateVideo = async () => {
    setGeneratingVideo(true)
    setError(null)
    setVideoResult(null)

    try {
      // Create a video prompt from the headline and first section
      const videoPrompt = `${content.headline}\n\n${content.sections[0].observation}\n\nVisual: Professional business setting showing clinic operations, follow-up processes, or data visualization. Clean, modern, professional style.`

      // Calculate extensions needed for target duration
      // Base: 8 seconds, each extension: 7 seconds
      // For Day 4, we want a longer video (30 seconds total for thread/long post)
      // BUT: Veo 3 max duration is 30 seconds, so we need to cap it
      const targetDuration = 30
      const baseDuration = 8
      const extensionSeconds = 7
      const maxDuration = 30 // Veo 3 maximum
      // Calculate max possible extensions: (30 - 8) / 7 = 3.14, so max 3 extensions = 29 seconds
      const maxPossibleExtensions = Math.floor((maxDuration - baseDuration) / extensionSeconds)
      const extensionsNeeded = Math.min(
        Math.ceil((targetDuration - baseDuration) / extensionSeconds),
        maxPossibleExtensions
      )

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

  const fullPost = `${content.headline}\n\n${content.sections.map((section, index) => 
    `${section.observation}\n\n${section.example}\n\n${section.solution}`
  ).join('\n\n---\n\n')}\n\n${content.cta}\n\n---\nRepurpose: ${content.repurpose}`

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
        caption: fullPost,
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
          <h1 className="text-3xl font-bold text-[#111827] mb-2">Day 4 — Thread / Long Post</h1>
          <p className="text-[#6b7280]">Operator Field Note template for long-form content</p>
        </div>

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Headline</h2>
          </div>
          <div className="bg-[#f9fafb] rounded-lg p-4 mb-4">
            <p className="text-[#111827] text-lg leading-relaxed font-medium">{content.headline}</p>
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
            <BookOpen className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Body Content (8 Sections)</h2>
          </div>
          <div className="space-y-6">
            {content.sections.map((section, index) => (
              <div key={index} className="bg-[#f9fafb] rounded-lg p-5 border border-[#e5e7eb]">
                <div className="mb-3">
                  <div className="text-sm font-medium text-[#6b7280] mb-1">Section {index + 1}</div>
                  <h3 className="text-lg font-semibold text-[#111827] mb-3">{section.observation}</h3>
                </div>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-[#6b7280] mb-1">Example:</p>
                    <p className="text-[#111827] leading-relaxed">{section.example}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-[#1e40af] mb-1">Solution:</p>
                    <p className="text-[#111827] leading-relaxed font-medium">{section.solution}</p>
                  </div>
                </div>
                <button
                  onClick={() => copyToClipboard(`${section.observation}\n\n${section.example}\n\n${section.solution}`)}
                  className="mt-3 flex items-center gap-2 px-3 py-2 text-xs text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  Copy Section
                </button>
              </div>
            ))}
          </div>
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
          <div className="bg-white rounded-lg p-4 max-h-96 overflow-y-auto">
            <pre className="text-[#111827] whitespace-pre-wrap font-sans leading-relaxed text-sm">{fullPost}</pre>
          </div>
        </div>

        <div className="bg-[#1e293b] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Generate Media</h2>
          </div>
          <p className="text-white/80 text-sm mb-4">
            Generate a header image or video for this long-form post using AI generation.
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
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Generated Image */}
        {generatedImage && (
          <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
            <h3 className="text-lg font-semibold text-[#111827] mb-4">Generated Header Image</h3>
            <div className="rounded-lg overflow-hidden border border-[#e5e7eb]">
              <img 
                src={generatedImage.startsWith('http') || generatedImage.startsWith('data:') ? generatedImage : `${API_URL}${generatedImage}`}
                alt="Generated header image"
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

        {/* Generated Video */}
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

        {generatingVideo && <VideoGenerationLoader message="Generating your video..." />}

        <div className="mt-6 p-4 bg-[#fef3c7] border border-[#fbbf24] rounded-lg">
          <p className="text-sm text-[#92400e]">
            <strong>Posting Tips:</strong> This works best as a thread on X/Twitter (one section per tweet) or as a long-form post on LinkedIn. For X, number each section (1/8, 2/8, etc.) and use line breaks between observation, example, and solution. For LinkedIn, post as a single long-form article with clear section headers.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ContentCalendarDay4
