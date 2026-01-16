import { useState, useEffect } from 'react'
import { FileText, Copy, Check, ChevronRight, Share2, Loader2, Sparkles, Image, Linkedin } from 'lucide-react'
import { api, API_URL } from '../utils/api'

function ContentCalendarDay3() {
  const [copied, setCopied] = useState(false)
  const [currentSlide, setCurrentSlide] = useState(0)
  const [generatingImages, setGeneratingImages] = useState(false)
  const [generatedImages, setGeneratedImages] = useState({})
  const [error, setError] = useState(null)
  const [linkedinConnections, setLinkedinConnections] = useState([])
  const [postingToLinkedIn, setPostingToLinkedIn] = useState(false)
  const [postSuccess, setPostSuccess] = useState(null)

  const content = {
    headline: "How we define a convertible lead for AI execution (5 questions)",
    slides: [
      {
        question: "What's the immediate pain point?",
        explanation: "If they can't articulate a specific problem happening right now, they're not ready to convert. We look for urgency indicators like 'we're losing revenue' or 'our team is overwhelmed.'"
      },
      {
        question: "Do they have budget allocated?",
        explanation: "Even if they're interested, without budget or approval authority, they're just researching. We ask: 'Is this something you'd invest in this quarter?'"
      },
      {
        question: "What's their decision timeline?",
        explanation: "A lead who says 'maybe next year' isn't convertible. We qualify leads who can make decisions within 60-90 days. Anything longer goes to nurture."
      },
      {
        question: "Have they tried a solution before?",
        explanation: "Leads who've attempted to solve this problem (and failed) are more likely to convert. They understand the complexity and are ready for a real solution."
      },
      {
        question: "What happens if they don't solve this?",
        explanation: "The cost of inaction matters. If they can't articulate consequences—lost revenue, team burnout, competitive disadvantage—they're not feeling enough pain to convert."
      }
    ],
    cta: "Share slide 1 if this helped.",
    repurpose: "Longform LinkedIn article for AEO."
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const copySlide = (slide, index) => {
    const slideText = `Slide ${index + 1}: ${slide.question}\n\n${slide.explanation}`
    copyToClipboard(slideText)
  }

  const copyAllSlides = () => {
    const allSlides = content.slides.map((slide, index) => 
      `Slide ${index + 1}: ${slide.question}\n\n${slide.explanation}`
    ).join('\n\n---\n\n')
    copyToClipboard(allSlides)
  }

  const handleGenerateImage = async (slideIndex) => {
    setGeneratingImages(true)
    setError(null)

    try {
      const slide = content.slides[slideIndex]
      const imagePrompt = `${content.headline} - ${slide.question}. ${slide.explanation}. Professional business infographic style, clean design, modern typography.`

      const response = await api.post('/api/image/generate', {
        prompt: imagePrompt,
        model: 'nanobanana',
        size: '1024x1024',
        quality: 'standard',
        aspect_ratio: '1:1',
        n: 1
      }, {
        timeout: 60000
      })

      const imageUrl = response.data.image_url || 
        (response.data.image_base64 ? `data:image/png;base64,${response.data.image_base64}` : null)
      
      if (imageUrl) {
        setGeneratedImages(prev => ({ ...prev, [slideIndex]: imageUrl }))
      }
    } catch (err) {
      console.error('Error generating image:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to generate image. Please try again.')
    } finally {
      setGeneratingImages(false)
    }
  }

  const handleGenerateAllImages = async () => {
    setGeneratingImages(true)
    setError(null)

    try {
      for (let i = 0; i < content.slides.length; i++) {
        const slide = content.slides[i]
        const imagePrompt = `${content.headline} - ${slide.question}. ${slide.explanation}. Professional business infographic style, clean design, modern typography.`

        const response = await api.post('/api/image/generate', {
          prompt: imagePrompt,
          model: 'nanobanana',
          size: '1024x1024',
          quality: 'standard',
          aspect_ratio: '1:1',
          n: 1
        }, {
          timeout: 60000
        })

        const imageUrl = response.data.image_url || 
          (response.data.image_base64 ? `data:image/png;base64,${response.data.image_base64}` : null)
        
        if (imageUrl) {
          setGeneratedImages(prev => ({ ...prev, [i]: imageUrl }))
        }
        
        // Small delay between requests
        if (i < content.slides.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000))
        }
      }
    } catch (err) {
      console.error('Error generating images:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to generate images. Please try again.')
    } finally {
      setGeneratingImages(false)
    }
  }

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

  const handlePostToLinkedIn = async () => {
    if (linkedinConnections.length === 0) {
      setError('No LinkedIn connections found. Please connect your LinkedIn account in Settings first.')
      return
    }

    const firstImage = generatedImages[0]
    if (!firstImage) {
      setError('Please generate at least the first slide image before posting to LinkedIn.')
      return
    }

    setPostingToLinkedIn(true)
    setError(null)
    setPostSuccess(null)

    try {
      const connectionIds = linkedinConnections.map(conn => conn.id)
      const carouselText = `${content.headline}\n\n${content.slides.map((slide, i) => `Slide ${i + 1}: ${slide.question}\n${slide.explanation}`).join('\n\n')}\n\n${content.cta}`
      
      const postData = {
        connection_ids: connectionIds,
        caption: carouselText,
        image_url: firstImage,
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
          <h1 className="text-3xl font-bold text-[#111827] mb-2">Day 3 — Carousel (5 slides)</h1>
          <p className="text-[#6b7280]">Carousel post template for social media engagement</p>
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
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-[#1e293b]" />
              <h2 className="text-xl font-semibold text-[#111827]">Carousel Slides</h2>
            </div>
            <button
              onClick={copyAllSlides}
              className="flex items-center gap-2 px-3 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              Copy All Slides
            </button>
          </div>

          {/* Slide Navigation */}
          <div className="flex items-center justify-center gap-2 mb-6">
            {content.slides.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentSlide(index)}
                className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                  currentSlide === index
                    ? 'bg-[#1e293b] text-white'
                    : 'bg-[#f5f5f5] text-[#4b5563] hover:bg-[#e5e7eb]'
                }`}
              >
                {index + 1}
              </button>
            ))}
          </div>

          {/* Current Slide Display */}
          <div className="bg-[#f9fafb] rounded-lg p-6 mb-4 min-h-[200px]">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="text-sm font-medium text-[#6b7280] mb-2">Slide {currentSlide + 1} of {content.slides.length}</div>
                <h3 className="text-xl font-semibold text-[#111827] mb-4">
                  {content.slides[currentSlide].question}
                </h3>
                <p className="text-[#111827] leading-relaxed">
                  {content.slides[currentSlide].explanation}
                </p>
              </div>
            </div>
            {generatedImages[currentSlide] && (
              <div className="mt-4 rounded-lg overflow-hidden border border-[#e5e7eb]">
                <img 
                  src={generatedImages[currentSlide].startsWith('http') || generatedImages[currentSlide].startsWith('data:') ? generatedImages[currentSlide] : `${API_URL}${generatedImages[currentSlide]}`}
                  alt={`Slide ${currentSlide + 1} image`}
                  className="w-full h-auto"
                  onError={(e) => {
                    console.error('Image load error:', e);
                    console.error('Image URL:', generatedImages[currentSlide]);
                  }}
                />
              </div>
            )}
          </div>

          {/* Slide Navigation Arrows */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => setCurrentSlide((prev) => (prev > 0 ? prev - 1 : content.slides.length - 1))}
              className="flex items-center gap-2 px-4 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
            >
              <ChevronRight className="w-4 h-4 rotate-180" />
              Previous
            </button>
            <div className="flex items-center gap-2">
              <button
                onClick={() => copySlide(content.slides[currentSlide], currentSlide)}
                className="flex items-center gap-2 px-4 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                Copy This Slide
              </button>
              <button
                onClick={() => handleGenerateImage(currentSlide)}
                disabled={generatingImages || generatedImages[currentSlide]}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-[#1e293b] text-white hover:bg-[#334155] rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generatingImages ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : generatedImages[currentSlide] ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <Image className="w-4 h-4" />
                )}
                {generatedImages[currentSlide] ? 'Generated' : 'Generate Image'}
              </button>
            </div>
            <button
              onClick={() => setCurrentSlide((prev) => (prev < content.slides.length - 1 ? prev + 1 : 0))}
              className="flex items-center gap-2 px-4 py-2 text-sm text-[#1e293b] hover:bg-[#f5f5f5] rounded-lg transition-colors"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Generate All Images Button */}
        <div className="bg-[#1e293b] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Generate All Carousel Images</h2>
          </div>
          <p className="text-white/80 text-sm mb-4">
            Generate images for all 5 carousel slides at once.
          </p>
          <button
            onClick={handleGenerateAllImages}
            disabled={generatingImages}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {generatingImages ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating All Images...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate All 5 Images
              </>
            )}
          </button>
          {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-300 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
          {Object.keys(generatedImages).length > 0 && (
            <div className="mt-4">
              <button
                onClick={handlePostToLinkedIn}
                disabled={postingToLinkedIn || !generatedImages[0]}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-[#0077b5] hover:bg-[#005885] text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {postingToLinkedIn ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Posting...
                  </>
                ) : (
                  <>
                    <Linkedin className="w-5 h-5" />
                    {linkedinConnections.length > 0 ? 'Post Carousel to LinkedIn' : 'Connect LinkedIn First'}
                  </>
                )}
              </button>
              {postSuccess && (
                <div className="mt-3 p-3 bg-green-100 border border-green-300 rounded-lg text-green-700 text-sm">
                  ✓ Posted successfully! {typeof postSuccess === 'string' && postSuccess.includes('linkedin.com') && (
                    <a href={postSuccess} target="_blank" rel="noopener noreferrer" className="underline ml-1">View post</a>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* All Slides List */}
        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-4">All Slides Overview</h2>
          <div className="space-y-4">
            {content.slides.map((slide, index) => (
              <div
                key={index}
                className="bg-[#f9fafb] rounded-lg p-4 border border-[#e5e7eb]"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-[#111827]">Slide {index + 1}: {slide.question}</h3>
                  <button
                    onClick={() => copySlide(slide, index)}
                    className="flex items-center gap-1 px-2 py-1 text-xs text-[#1e293b] hover:bg-[#f5f5f5] rounded transition-colors"
                  >
                    <Copy className="w-3 h-3" />
                  </button>
                </div>
                <p className="text-[#4b5563] text-sm leading-relaxed">{slide.explanation}</p>
              </div>
            ))}
          </div>
        </div>

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

        <div className="bg-white border border-[#e5e7eb] rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <FileText className="w-5 h-5 text-[#1e293b]" />
            <h2 className="text-xl font-semibold text-[#111827]">Repurpose</h2>
          </div>
          <div className="bg-[#f0f9ff] border border-[#bae6fd] rounded-lg p-4 mb-4">
            <p className="text-[#111827] leading-relaxed">{content.repurpose}</p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-[#fef3c7] border border-[#fbbf24] rounded-lg">
          <p className="text-sm text-[#92400e]">
            <strong>Design Notes:</strong> Each slide should be visually clean with the question as the headline and the explanation as body text. Use consistent branding and consider adding icons or simple graphics to make each slide more engaging. The carousel format works best on Instagram and LinkedIn.
          </p>
        </div>
      </div>
    </div>
  )
}

export default ContentCalendarDay3
