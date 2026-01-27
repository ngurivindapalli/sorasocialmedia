import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { 
  FileText, Copy, Check, ChevronRight, ChevronLeft, Share2, 
  Loader2, Image, Linkedin, Calendar, Video, AlertTriangle,
  ArrowLeft, List, Eye, BookOpen
} from 'lucide-react'
import { api, API_URL } from '../utils/api'
import { contentCalendar, getContentByDay, weekThemes } from '../data/contentCalendar'
import LoadingOverlay from '../components/LoadingOverlay'

// Cache for generated images - stored in memory and localStorage
const IMAGE_CACHE_KEY = 'content_calendar_images'

function ContentCalendarView() {
  const { day } = useParams()
  const navigate = useNavigate()
  const currentDay = parseInt(day) || 1
  const content = getContentByDay(currentDay)

  const [copied, setCopied] = useState(false)
  const [generatingImage, setGeneratingImage] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [error, setError] = useState(null)
  const [linkedinConnections, setLinkedinConnections] = useState([])
  const [postingToLinkedIn, setPostingToLinkedIn] = useState(false)
  const [postSuccess, setPostSuccess] = useState(null)
  const [currentSlide, setCurrentSlide] = useState(0)
  const [activeTab, setActiveTab] = useState('post') // 'post' or 'details'

  // Load cached image from localStorage
  const loadCachedImage = useCallback(() => {
    try {
      const cache = JSON.parse(localStorage.getItem(IMAGE_CACHE_KEY) || '{}')
      return cache[currentDay] || null
    } catch {
      return null
    }
  }, [currentDay])

  // Save image to cache
  const saveCachedImage = useCallback((imageData) => {
    try {
      const cache = JSON.parse(localStorage.getItem(IMAGE_CACHE_KEY) || '{}')
      cache[currentDay] = imageData
      localStorage.setItem(IMAGE_CACHE_KEY, JSON.stringify(cache))
    } catch (err) {
      console.error('Error caching image:', err)
    }
  }, [currentDay])

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

  // Load cached image and auto-generate if on Post tab and no cache exists
  useEffect(() => {
    const cachedImage = loadCachedImage()
    if (cachedImage) {
      setGeneratedImage(cachedImage)
    } else if (activeTab === 'post' && !content?.isVideo && !generatingImage && !generatedImage) {
      // Auto-generate image when on Post tab and no cached image
      handleGenerateImage()
    }
  }, [currentDay, activeTab])

  // Reset state when day changes
  useEffect(() => {
    const cachedImage = loadCachedImage()
    setGeneratedImage(cachedImage)
    setError(null)
    setPostSuccess(null)
    setCurrentSlide(0)
  }, [currentDay, loadCachedImage])

  if (!content) {
    return (
      <div className="min-h-screen bg-white p-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl font-bold text-[#111827] mb-4">Day {currentDay} not found</h1>
          <Link to="/content-calendar" className="text-blue-600 hover:underline">
            Back to Content Calendar
          </Link>
        </div>
      </div>
    )
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const generateFullPost = () => {
    let post = `${content.headline}\n\n`
    
    if (content.content.observation) {
      post += `${content.content.observation}\n\n`
    }
    if (content.content.examples) {
      post += content.content.examples.map(ex => `• ${ex}`).join('\n') + '\n\n'
    }
    if (content.content.conditions) {
      post += content.content.conditions.map((c, i) => `${i + 1}. ${c}`).join('\n') + '\n\n'
    }
    if (content.content.before) {
      post += `BEFORE: ${content.content.before}\n\n`
      post += `ACTION: ${content.content.action}\n\n`
      post += `RESULT: ${content.content.outcome}\n\n`
    }
    if (content.content.leaks) {
      post += content.content.leaks.map(l => `• ${l.leak}: ${l.stat}`).join('\n') + '\n\n'
    }
    if (content.content.slides) {
      post += content.content.slides.map((s, i) => 
        s.question ? `${i + 1}. ${s.question}\n${s.explanation}` : 
        s.step ? `Step ${s.step}: ${s.title}\n${s.description}` :
        s.option ? `${s.option}: ${s.cost || s.result}` : ''
      ).join('\n\n') + '\n\n'
    }
    if (content.content.sections) {
      post += content.content.sections.map(s => 
        `${s.observation || s.title}\n${s.example || s.content || ''}\n${s.solution || ''}`
      ).join('\n\n') + '\n\n'
    }
    if (content.content.changes) {
      post += content.content.changes.join('\n') + '\n\n'
    }
    if (content.content.questions) {
      post += content.content.questions.map(q => `Q: ${q.q}\nWhy: ${q.why}`).join('\n\n') + '\n\n'
    }
    if (content.content.findings) {
      post += content.content.findings.map(f => `• ${f}`).join('\n') + '\n\n'
    }
    if (content.content.learnings) {
      post += content.content.learnings.join('\n') + '\n\n'
    }
    if (content.content.script) {
      if (typeof content.content.script === 'string') {
        post += content.content.script + '\n\n'
      } else if (content.content.script.text1) {
        post += `TEXT 1: ${content.content.script.text1}\n\n`
        if (content.content.script.response1) post += `IF "2 weeks": ${content.content.script.response1}\n\n`
        if (content.content.script.response2) post += `IF "exploring": ${content.content.script.response2}\n\n`
      }
    }
    
    post += `${content.cta}\n\n---\nRepurpose: ${content.repurpose}`
    return post
  }

  const handleGenerateImage = async () => {
    // Check cache first
    const cachedImage = loadCachedImage()
    if (cachedImage) {
      setGeneratedImage(cachedImage)
      return
    }

    setGeneratingImage(true)
    setError(null)
    setGeneratedImage(null)

    try {
      const imagePrompt = `${content.headline}. Professional business image, clean modern design, suitable for LinkedIn and social media. High quality, professional photography style.`

      const response = await api.post('/api/image/generate', {
        prompt: imagePrompt,
        model: 'imagen-4.0-generate-001',
        size: '1024x1024',
        quality: 'high',
        aspect_ratio: '1:1',
        n: 1
      }, {
        timeout: 120000
      })

      let imageData = null
      if (response.data.image_url) {
        imageData = response.data.image_url
      } else if (response.data.image_base64) {
        imageData = `data:image/png;base64,${response.data.image_base64}`
      }

      if (imageData) {
        setGeneratedImage(imageData)
        // Save to cache to preserve credits
        saveCachedImage(imageData)
      }
    } catch (err) {
      console.error('Error generating image:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to generate image. Please try again.')
    } finally {
      setGeneratingImage(false)
    }
  }

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
        caption: generateFullPost(),
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
      setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Failed to post to LinkedIn.')
    } finally {
      setPostingToLinkedIn(false)
    }
  }

  const handlePostToCompanyPage = async () => {
    if (!generatedImage) {
      setError('Please generate an image first before posting to LinkedIn.')
      return
    }

    setPostingToLinkedIn(true)
    setError(null)
    setPostSuccess(null)

    try {
      // Get image data - if base64, extract just the base64 part
      let imageBase64 = null
      let imageUrl = null
      
      if (generatedImage.startsWith('data:image')) {
        // Extract base64 data
        const match = generatedImage.match(/base64,(.+)/)
        if (match) {
          imageBase64 = match[1]
        }
      } else {
        imageUrl = generatedImage
      }

      const postData = {
        caption: generateFullPost(),
        image_url: imageUrl,
        image_base64: imageBase64
      }

      const response = await api.post('/api/post/linkedin/company', postData)
      
      if (response.data.success) {
        const postUrl = response.data.post_url
        setPostSuccess(postUrl || 'Posted to AIGIS company page successfully!')
        setTimeout(() => setPostSuccess(null), 10000) // Keep longer to see URL
      } else {
        setError(response.data.error || 'Failed to post to LinkedIn company page')
      }
    } catch (err) {
      console.error('Error posting to LinkedIn company page:', err)
      setError(err.response?.data?.detail || err.response?.data?.error || err.message || 'Failed to post to LinkedIn company page.')
    } finally {
      setPostingToLinkedIn(false)
    }
  }

  const weekTheme = weekThemes[content.week]
  const fullPost = generateFullPost()

  return (
    <div className="min-h-screen bg-white p-8 relative">
      {/* Loading Overlay for Image Generation */}
      <LoadingOverlay 
        isLoading={generatingImage} 
        type="image" 
        message="Generating post image..."
        subMessage="Creating a professional image for your LinkedIn post. This typically takes 15-30 seconds."
        fullScreen={true}
      />

      <div className="max-w-4xl mx-auto">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-6">
          <Link 
            to="/content-calendar"
            className="flex items-center gap-2 text-[#6b7280] hover:text-[#111827] transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Calendar
          </Link>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate(`/content-calendar/day/${Math.max(1, currentDay - 1)}`)}
              disabled={currentDay <= 1}
              className="p-2 rounded-lg hover:bg-[#f5f5f5] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="text-sm text-[#6b7280]">Day {currentDay} of 30</span>
            <button
              onClick={() => navigate(`/content-calendar/day/${Math.min(30, currentDay + 1)}`)}
              disabled={currentDay >= 30}
              className="p-2 rounded-lg hover:bg-[#f5f5f5] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-2 text-sm text-[#6b7280] mb-2">
            <Calendar className="w-4 h-4" />
            Week {content.week}: {weekTheme?.name}
          </div>
          <h1 className="text-3xl font-bold text-[#111827] mb-2">
            Day {content.day} — {content.format}
          </h1>
          <p className="text-[#6b7280]">{weekTheme?.description}</p>
        </div>

        {/* Post / Details Tab Toggle */}
        {!content.isVideo && (
          <div className="flex gap-2 mb-6 bg-[#f5f5f5] p-1 rounded-lg w-fit">
            <button
              onClick={() => setActiveTab('post')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all ${
                activeTab === 'post'
                  ? 'bg-white text-[#111827] shadow-sm'
                  : 'text-[#6b7280] hover:text-[#111827]'
              }`}
            >
              <Eye className="w-4 h-4" />
              Post Preview
            </button>
            <button
              onClick={() => setActiveTab('details')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md font-medium text-sm transition-all ${
                activeTab === 'details'
                  ? 'bg-white text-[#111827] shadow-sm'
                  : 'text-[#6b7280] hover:text-[#111827]'
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Details
            </button>
          </div>
        )}

        {/* Video Warning */}
        {content.isVideo && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <Video className="w-5 h-5 text-amber-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-amber-800">Video Content</h3>
                <p className="text-sm text-amber-700 mt-1">{content.videoNote}</p>
              </div>
            </div>
          </div>
        )}

        {/* POST PREVIEW TAB */}
        {activeTab === 'post' && !content.isVideo && (
          <div className="space-y-6">
            {/* LinkedIn Post Preview Card */}
            <div className="bg-white border border-[#e5e7eb] rounded-xl shadow-lg overflow-hidden">
              {/* Post Header */}
              <div className="p-4 border-b border-[#e5e7eb]">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#1e293b] to-[#334155] flex items-center justify-center">
                    <span className="text-white font-bold text-lg">A</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-[#111827]">AIGIS</h3>
                    <p className="text-sm text-[#6b7280]">Company • LinkedIn Post Preview</p>
                  </div>
                </div>
              </div>

              {/* Post Image */}
              <div className="aspect-square bg-[#f5f5f5] relative">
                {generatedImage ? (
                  <img 
                    src={generatedImage.startsWith('http') || generatedImage.startsWith('data:') ? generatedImage : `${API_URL}${generatedImage}`}
                    alt="Post preview"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-[#9ca3af]">
                    <Image className="w-16 h-16 mb-3" />
                    <p className="text-sm">Image will be generated automatically</p>
                    {error && (
                      <p className="text-red-500 text-sm mt-2 max-w-xs text-center">{error}</p>
                    )}
                  </div>
                )}
              </div>

              {/* Post Caption */}
              <div className="p-4">
                <div className="text-[#111827] text-sm whitespace-pre-wrap leading-relaxed max-h-40 overflow-y-auto">
                  {fullPost.length > 500 ? fullPost.substring(0, 500) + '...' : fullPost}
                </div>
                <button
                  onClick={() => copyToClipboard(fullPost)}
                  className="mt-3 flex items-center gap-2 text-sm text-[#1e293b] hover:text-[#334155] transition-colors"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  Copy Full Caption
                </button>
              </div>

              {/* Post Actions */}
              <div className="px-4 pb-4 space-y-3">
                {generatedImage && (
                  <>
                    {/* Post to AIGIS Company Page - Primary Action */}
                    <button
                      onClick={handlePostToCompanyPage}
                      disabled={postingToLinkedIn}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#0077b5] hover:bg-[#005885] text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {postingToLinkedIn ? (
                        <>
                          <Loader2 className="w-5 h-5 animate-spin" />
                          Posting to LinkedIn...
                        </>
                      ) : (
                        <>
                          <Linkedin className="w-5 h-5" />
                          Post to AIGIS Company Page
                        </>
                      )}
                    </button>

                    {/* Download Image */}
                    <a
                      href={generatedImage.startsWith('http') || generatedImage.startsWith('data:') ? generatedImage : `${API_URL}${generatedImage}`}
                      download="content-image.png"
                      className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-[#f5f5f5] hover:bg-[#e5e7eb] text-[#111827] font-medium rounded-lg transition-colors"
                    >
                      <Image className="w-4 h-4" />
                      Download Image
                    </a>

                    {/* Optional: Post to Personal Profile */}
                    {linkedinConnections.length > 0 && (
                      <button
                        onClick={handlePostToLinkedIn}
                        disabled={postingToLinkedIn}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-transparent border border-[#0077b5] text-[#0077b5] hover:bg-[#0077b5]/10 font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                      >
                        <Linkedin className="w-4 h-4" />
                        Post to Personal Profile
                      </button>
                    )}

                    {postSuccess && (
                      <div className="p-3 bg-green-100 border border-green-300 rounded-lg text-green-700 text-sm">
                        <p className="font-medium">✓ Posted successfully!</p>
                        {postSuccess.startsWith('http') && (
                          <a 
                            href={postSuccess} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-green-800 underline hover:no-underline mt-1 block"
                          >
                            View Post on LinkedIn →
                          </a>
                        )}
                      </div>
                    )}
                  </>
                )}

                {!generatedImage && !generatingImage && (
                  <button
                    onClick={handleGenerateImage}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition-all"
                  >
                    <Image className="w-5 h-5" />
                    Generate Image
                  </button>
                )}
              </div>
            </div>

            {/* Cached Image Notice */}
            {generatedImage && loadCachedImage() && (
              <div className="flex items-center gap-2 text-sm text-[#6b7280] bg-[#f5f5f5] px-4 py-2 rounded-lg">
                <Check className="w-4 h-4 text-green-600" />
                Image cached - won't regenerate on next visit (saving credits)
              </div>
            )}
          </div>
        )}

        {/* DETAILS TAB - Only show when on details tab or for video content */}
        {(activeTab === 'details' || content.isVideo) && (
          <>

        {/* Special Notes */}
        {content.note && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5" />
              <p className="text-sm text-blue-700">{content.note}</p>
            </div>
          </div>
        )}

        {/* Headline */}
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

        {/* Content Section - Varies by type */}
        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Content</h2>
          </div>

          {/* Observation + Examples */}
          {content.content.observation && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-[#6b7280] mb-2">Key Observation:</p>
                <div className="bg-[#f9fafb] rounded-lg p-4">
                  <p className="text-[#111827] leading-relaxed">{content.content.observation}</p>
                </div>
              </div>
              {content.content.examples && (
                <div>
                  <p className="text-sm font-medium text-[#6b7280] mb-2">Examples:</p>
                  <div className="bg-[#f9fafb] rounded-lg p-4 space-y-2">
                    {content.content.examples.map((example, index) => (
                      <p key={index} className="text-[#111827] leading-relaxed">• {example}</p>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Video Script */}
          {content.content.hook && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-[#6b7280] mb-2">Hook:</p>
                <div className="bg-[#f9fafb] rounded-lg p-4">
                  <p className="text-[#111827] leading-relaxed italic">"{content.content.hook}"</p>
                </div>
              </div>
              {content.content.script && (
                <div>
                  <p className="text-sm font-medium text-[#6b7280] mb-2">Script ({content.content.duration}):</p>
                  <div className="bg-[#f9fafb] rounded-lg p-4">
                    <p className="text-[#111827] leading-relaxed">{content.content.script}</p>
                  </div>
                </div>
              )}
              {content.content.insight && (
                <div>
                  <p className="text-sm font-medium text-[#6b7280] mb-2">Key Insight:</p>
                  <div className="bg-[#f9fafb] rounded-lg p-4">
                    <p className="text-[#111827] leading-relaxed">{content.content.insight}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Carousel Slides */}
          {content.content.slides && (
            <div className="space-y-4">
              <div className="flex items-center justify-center gap-2 mb-4">
                {content.content.slides.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentSlide(index)}
                    className={`w-8 h-8 rounded-lg font-medium text-sm transition-colors ${
                      currentSlide === index
                        ? 'bg-[#1e293b] text-white'
                        : 'bg-[#f5f5f5] text-[#4b5563] hover:bg-[#e5e7eb]'
                    }`}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>
              <div className="bg-[#f9fafb] rounded-lg p-6">
                {content.content.slides[currentSlide]?.question && (
                  <>
                    <p className="text-sm text-[#6b7280] mb-2">Slide {currentSlide + 1}</p>
                    <h3 className="text-xl font-semibold text-[#111827] mb-3">
                      {content.content.slides[currentSlide].question}
                    </h3>
                    <p className="text-[#111827] leading-relaxed">
                      {content.content.slides[currentSlide].explanation}
                    </p>
                  </>
                )}
                {content.content.slides[currentSlide]?.step && (
                  <>
                    <p className="text-sm text-[#6b7280] mb-2">Step {content.content.slides[currentSlide].step}</p>
                    <h3 className="text-xl font-semibold text-[#111827] mb-3">
                      {content.content.slides[currentSlide].title}
                    </h3>
                    <p className="text-[#111827] leading-relaxed">
                      {content.content.slides[currentSlide].description}
                    </p>
                  </>
                )}
                {content.content.slides[currentSlide]?.option && (
                  <>
                    <h3 className="text-xl font-semibold text-[#111827] mb-3">
                      {content.content.slides[currentSlide].option}
                    </h3>
                    {content.content.slides[currentSlide].cost && (
                      <p className="text-[#111827]"><strong>Cost:</strong> {content.content.slides[currentSlide].cost}</p>
                    )}
                    {content.content.slides[currentSlide].result && (
                      <p className="text-[#111827]"><strong>Result:</strong> {content.content.slides[currentSlide].result}</p>
                    )}
                  </>
                )}
              </div>
            </div>
          )}

          {/* Conditions */}
          {content.content.conditions && (
            <div>
              <p className="text-sm font-medium text-[#6b7280] mb-2">Conditions:</p>
              <div className="bg-[#f9fafb] rounded-lg p-4 space-y-3">
                {content.content.conditions.map((condition, index) => (
                  <p key={index} className="text-[#111827] leading-relaxed">
                    <span className="font-semibold">{index + 1}.</span> {condition}
                  </p>
                ))}
              </div>
            </div>
          )}

          {/* Case Study (Before/Action/Outcome) */}
          {content.content.before && (
            <div className="space-y-4">
              <div>
                <p className="text-sm font-medium text-[#6b7280] mb-2">Before:</p>
                <div className="bg-red-50 rounded-lg p-4">
                  <p className="text-[#111827] leading-relaxed">{content.content.before}</p>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-[#6b7280] mb-2">Action:</p>
                <div className="bg-yellow-50 rounded-lg p-4">
                  <p className="text-[#111827] leading-relaxed">{content.content.action}</p>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-[#6b7280] mb-2">Outcome:</p>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-[#111827] leading-relaxed">{content.content.outcome}</p>
                </div>
              </div>
            </div>
          )}

          {/* Leaks/Stats */}
          {content.content.leaks && (
            <div className="space-y-3">
              {content.content.leaks.map((leak, index) => (
                <div key={index} className="bg-[#f9fafb] rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-[#111827]">{leak.leak}</h4>
                    <span className="text-red-600 font-medium">{leak.stat}</span>
                  </div>
                  <p className="text-sm text-[#6b7280]">Fix: {leak.fix}</p>
                </div>
              ))}
            </div>
          )}

          {/* Thread/List Changes */}
          {content.content.changes && (
            <div className="bg-[#f9fafb] rounded-lg p-4 space-y-2">
              {content.content.changes.map((change, index) => (
                <p key={index} className="text-[#111827] leading-relaxed">{change}</p>
              ))}
            </div>
          )}

          {/* Sections (Field Notes) */}
          {content.content.sections && (
            <div className="space-y-4">
              {content.content.sections.map((section, index) => (
                <div key={index} className="bg-[#f9fafb] rounded-lg p-4">
                  <h4 className="font-semibold text-[#111827] mb-2">
                    {section.observation || section.title}
                  </h4>
                  {section.example && (
                    <p className="text-[#6b7280] text-sm mb-2">Example: {section.example}</p>
                  )}
                  {section.content && (
                    <p className="text-[#111827]">{section.content}</p>
                  )}
                  {section.solution && (
                    <p className="text-green-700 text-sm mt-2">→ {section.solution}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Poll */}
          {content.content.options && (
            <div>
              <p className="text-sm font-medium text-[#6b7280] mb-2">Poll Question:</p>
              <div className="bg-[#f9fafb] rounded-lg p-4 mb-4">
                <p className="text-[#111827] font-medium mb-3">{content.content.question}</p>
                <div className="space-y-2">
                  {content.content.options.map((option, index) => (
                    <div key={index} className="bg-white rounded-lg p-3 border border-[#e5e7eb]">
                      {option}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Questions (Qualification) */}
          {content.content.questions && (
            <div className="space-y-4">
              {content.content.questions.map((q, index) => (
                <div key={index} className="bg-[#f9fafb] rounded-lg p-4">
                  <h4 className="font-semibold text-[#111827] mb-2">Q{index + 1}: {q.q}</h4>
                  <p className="text-sm text-[#6b7280]">Why: {q.why}</p>
                </div>
              ))}
            </div>
          )}

          {/* Findings/Data */}
          {content.content.findings && (
            <div className="bg-[#f9fafb] rounded-lg p-4 space-y-2">
              {content.content.intro && <p className="text-[#111827] mb-3">{content.content.intro}</p>}
              {content.content.findings.map((finding, index) => (
                <p key={index} className="text-[#111827]">• {typeof finding === 'string' ? finding : `${finding.finding}: ${finding.data}`}</p>
              ))}
            </div>
          )}

          {/* Learnings */}
          {content.content.learnings && (
            <div className="bg-[#f9fafb] rounded-lg p-4 space-y-2">
              {content.content.learnings.map((learning, index) => (
                <p key={index} className="text-[#111827]">{learning}</p>
              ))}
            </div>
          )}

          {/* Engagement Question */}
          {content.content.question && !content.content.options && (
            <div className="bg-[#f9fafb] rounded-lg p-4">
              <p className="text-[#111827] text-lg font-medium mb-3">{content.content.question}</p>
              {content.content.context && <p className="text-[#6b7280]">{content.content.context}</p>}
            </div>
          )}

          {/* Script (text messages) */}
          {content.content.script?.text1 && (
            <div className="space-y-4">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm font-medium text-blue-800 mb-2">First Text:</p>
                <p className="text-[#111827]">{content.content.script.text1}</p>
              </div>
              {content.content.script.response1 && (
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-green-800 mb-2">If "2 weeks":</p>
                  <p className="text-[#111827]">{content.content.script.response1}</p>
                </div>
              )}
              {content.content.script.response2 && (
                <div className="bg-yellow-50 rounded-lg p-4">
                  <p className="text-sm font-medium text-yellow-800 mb-2">If "exploring":</p>
                  <p className="text-[#111827]">{content.content.script.response2}</p>
                </div>
              )}
            </div>
          )}

          {/* Request/ICP */}
          {content.content.request && (
            <div className="space-y-4">
              <p className="text-[#111827]">{content.content.request}</p>
              {content.content.icp1 && (
                <div className="bg-[#f9fafb] rounded-lg p-4">
                  <p className="text-[#111827]">{content.content.icp1}</p>
                </div>
              )}
              {content.content.icp2 && (
                <div className="bg-[#f9fafb] rounded-lg p-4">
                  <p className="text-[#111827]">{content.content.icp2}</p>
                </div>
              )}
              {content.content.offer && (
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-green-800">{content.content.offer}</p>
                </div>
              )}
            </div>
          )}

          {/* What/Who/Reward (Fellowship) */}
          {content.content.what && (
            <div className="space-y-3">
              <div className="bg-[#f9fafb] rounded-lg p-4">
                <p className="text-sm font-medium text-[#6b7280] mb-1">What:</p>
                <p className="text-[#111827]">{content.content.what}</p>
              </div>
              <div className="bg-[#f9fafb] rounded-lg p-4">
                <p className="text-sm font-medium text-[#6b7280] mb-1">Who:</p>
                <p className="text-[#111827]">{content.content.who}</p>
              </div>
              <div className="bg-[#f9fafb] rounded-lg p-4">
                <p className="text-sm font-medium text-[#6b7280] mb-1">Reward:</p>
                <p className="text-[#111827]">{content.content.reward}</p>
              </div>
            </div>
          )}
        </div>

        {/* CTA */}
        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Share2 className="w-5 h-5 text-[#1e293b]" />
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

        {/* Repurpose */}
        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Repurpose</h2>
          </div>
          <div className="bg-[#f0f9ff] border border-[#bae6fd] rounded-lg p-4">
            <p className="text-[#111827] leading-relaxed">{content.repurpose}</p>
          </div>
        </div>

        {/* Full Post + Generate */}
        {!content.isVideo && (
          <>
            <div className="bg-[#1e293b] rounded-lg shadow-sm p-6 mb-6">
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
              <div className="bg-white rounded-lg p-4 max-h-60 overflow-y-auto">
                <pre className="text-[#111827] whitespace-pre-wrap font-sans leading-relaxed text-sm">{fullPost}</pre>
              </div>
            </div>

            {/* Generate Media */}
            <div className="bg-[#1e293b] rounded-lg shadow-sm p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Generate Media</h2>
              <p className="text-white/80 text-sm mb-4">
                Generate an image for this post using Google Imagen AI.
              </p>
              <button
                onClick={handleGenerateImage}
                disabled={generatingImage}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generatingImage ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating with Imagen...
                  </>
                ) : (
                  <>
                    <Image className="w-5 h-5" />
                    Generate Image
                  </>
                )}
              </button>

              {error && (
                <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
                  {error}
                </div>
              )}

              {generatedImage && (
                <div className="mt-4 space-y-3">
                  {/* Post to AIGIS Company Page - Primary Action */}
                  <button
                    onClick={handlePostToCompanyPage}
                    disabled={postingToLinkedIn}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#0077b5] hover:bg-[#005885] text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {postingToLinkedIn ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Posting to LinkedIn...
                      </>
                    ) : (
                      <>
                        <Linkedin className="w-5 h-5" />
                        Post to AIGIS Company Page
                      </>
                    )}
                  </button>
                  
                  {/* Optional: Post to Personal Profile */}
                  {linkedinConnections.length > 0 && (
                    <button
                      onClick={handlePostToLinkedIn}
                      disabled={postingToLinkedIn}
                      className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-transparent border border-[#0077b5] text-[#0077b5] hover:bg-[#0077b5]/10 font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                    >
                      <Linkedin className="w-4 h-4" />
                      Post to Personal Profile
                    </button>
                  )}
                  
                  {postSuccess && (
                    <div className="p-3 bg-green-100 border border-green-300 rounded-lg text-green-700 text-sm">
                      <p className="font-medium">✓ Posted successfully!</p>
                      {postSuccess.startsWith('http') && (
                        <a 
                          href={postSuccess} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-green-800 underline hover:no-underline mt-1 block"
                        >
                          View Post on LinkedIn →
                        </a>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}

            {/* Generated Image - Only show on Details tab if we have one */}
            {activeTab === 'details' && generatedImage && (
              <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
                <h3 className="text-lg font-semibold text-[#111827] mb-4">Generated Image</h3>
                <div className="rounded-lg overflow-hidden border border-[#e5e7eb]">
                  <img 
                    src={generatedImage.startsWith('http') || generatedImage.startsWith('data:') ? generatedImage : `${API_URL}${generatedImage}`}
                    alt="Generated content"
                    className="w-full h-auto"
                  />
                </div>
                <a
                  href={generatedImage.startsWith('http') || generatedImage.startsWith('data:') ? generatedImage : `${API_URL}${generatedImage}`}
                  download="content-image.png"
                  className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-[#1e293b] text-white rounded-lg hover:bg-[#334155] transition-colors"
                >
                  <Image className="w-4 h-4" />
                  Download Image
                </a>
              </div>
            )}
          </>
        )}

        {/* Quick Nav */}
        <div className="mt-8 p-4 bg-[#f9fafb] rounded-lg">
          <h3 className="font-medium text-[#111827] mb-3">Quick Navigation</h3>
          <div className="flex flex-wrap gap-2">
            {contentCalendar.map((c) => (
              <button
                key={c.day}
                onClick={() => navigate(`/content-calendar/day/${c.day}`)}
                className={`w-8 h-8 rounded text-sm font-medium transition-colors ${
                  c.day === currentDay
                    ? 'bg-[#1e293b] text-white'
                    : c.isVideo
                    ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                    : 'bg-white border border-[#e5e7eb] text-[#4b5563] hover:bg-[#f5f5f5]'
                }`}
                title={`Day ${c.day}: ${c.format}${c.isVideo ? ' (Video)' : ''}`}
              >
                {c.day}
              </button>
            ))}
          </div>
          <p className="mt-2 text-xs text-[#6b7280]">
            <span className="inline-block w-3 h-3 bg-amber-100 rounded mr-1"></span> = Video content (hand-generated)
          </p>
        </div>
      </div>
    </div>
  )
}

export default ContentCalendarView
