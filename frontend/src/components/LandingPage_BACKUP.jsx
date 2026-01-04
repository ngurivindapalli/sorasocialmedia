import { useState, useEffect, useRef } from 'react'
import '../App.css'
import { AnimatedHero } from './ui/animated-hero'
import { WavyBlock, WavyBlockItem } from './ui/wavy-text-block'
import Logo from './Logo'

function LandingPage() {
  const handleGetStarted = () => {
    window.location.href = '/signup'
  }
  const [isVisible, setIsVisible] = useState({})
  const [tiltStyles, setTiltStyles] = useState({})
  const sectionRefs = useRef({})

  // Scroll fade-in effect using Intersection Observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const key = entry.target.getAttribute('data-section-key')
            if (key) {
              setIsVisible((prev) => ({ ...prev, [key]: true }))
            }
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    )
    
    // Use setTimeout to ensure DOM is ready
    const timeoutId = setTimeout(() => {
      Object.values(sectionRefs.current).forEach((el) => {
        if (el) {
          observer.observe(el)
        }
      })
    }, 100)

    return () => {
      clearTimeout(timeoutId)
      observer.disconnect()
    }
  }, [])

  // Tilt effect handler
  const handleMouseMove = (e, key) => {
    const card = e.currentTarget
    const rect = card.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    
    const rotateX = ((y - centerY) / centerY) * -5
    const rotateY = ((x - centerX) / centerX) * 5
    
    setTiltStyles((prev) => ({
      ...prev,
      [key]: {
        transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`,
      },
    }))
  }

  const handleMouseLeave = (key) => {
    setTiltStyles((prev) => ({
      ...prev,
      [key]: {
        transform: 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)',
      },
    }))
  }

  // Smooth scroll behavior
  useEffect(() => {
    document.documentElement.style.scrollBehavior = 'smooth'
    return () => {
      document.documentElement.style.scrollBehavior = 'auto'
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-r from-[#cfd7f1] via-[#f0d7d2] to-[#f7f1f4] text-[#111827] inertia-scroll" style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif' }}>
      {/* Navigation */}
      <nav 
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md" 
        style={{ 
          height: '64px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderBottom: '1px solid #e5e7eb'
        }}
      >
        <div className="max-w-[1400px] mx-auto px-6 h-full flex items-center justify-between" style={{ paddingLeft: '40px', paddingRight: '40px' }}>
          <div className="flex items-center gap-3">
            <div className="text-[#111827]">
              <Logo />
            </div>
            <span className="text-[#111827] text-lg font-semibold tracking-tight">VideoHook</span>
          </div>
          <div className="flex items-center gap-8" style={{ gap: '32px' }}>
            <a 
              href="#" 
              className="text-sm font-medium text-[#4b5563] hover:text-[#111827] smooth-hover" 
              style={{ 
                fontSize: '14px', 
                fontWeight: 400,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#111827'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = '#4b5563'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              Blog
            </a>
            <a 
              href="#"
              className="text-sm font-medium text-[#4b5563] hover:text-[#111827] smooth-hover"
              style={{
                fontSize: '14px',
                fontWeight: 400,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#111827'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = '#4b5563'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              Pricing
            </a>
            <button
              onClick={() => window.location.href = '/signup'}
              className="px-5 py-2 text-sm font-medium rounded-full smooth-hover"
              style={{
                paddingLeft: '24px',
                paddingRight: '24px',
                paddingTop: '10px',
                paddingBottom: '10px',
                fontSize: '14px',
                fontWeight: 500,
                backgroundColor: '#000000',
                color: '#ffffff',
                borderRadius: '999px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#111827'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#000000'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              Sign up for free
            </button>
            <button
              onClick={() => window.location.href = '/login'}
              className="px-5 py-2 text-sm font-medium rounded-lg smooth-hover"
              style={{
                paddingLeft: '20px',
                paddingRight: '20px',
                paddingTop: '8px',
                paddingBottom: '8px',
                fontSize: '14px',
                fontWeight: 500,
                backgroundColor: 'transparent',
                color: '#111827',
                border: '1px solid #e5e7eb',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f9fafb'
                e.currentTarget.style.borderColor = '#111827'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.borderColor = '#e5e7eb'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              Log in
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <div className="relative" style={{ marginTop: '64px' }}>
        {/* Background Video */}
        <div className="absolute inset-0 overflow-hidden">
          <video
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-full object-cover"
          >
            <source src="/unicorn-1763411713178.webm" type="video/webm" />
            <source src="/bg-video.mp4" type="video/mp4" />
          </video>
        </div>

        <div className="relative max-w-[1120px] mx-auto">
          <AnimatedHero onGetStarted={handleGetStarted} />
        </div>
      </div>

      {/* How it works with Wavy Animation */}
      <div 
        className="bg-white section-snap overflow-hidden" 
        style={{ paddingTop: '120px', paddingBottom: '120px' }}
        ref={(el) => (sectionRefs.current['how-it-works'] = el)}
        data-section-key="how-it-works"
      >
        <div className="max-w-[1120px] mx-auto px-10" style={{ paddingLeft: '80px', paddingRight: '80px' }}>
          <WavyBlock className="space-y-16" style={{ gap: '96px' }} offset={['start end', 'end start']}>
            {/* Step 01 */}
            <WavyBlockItem 
              index={0}
              config={{
                baseOffsetFactor: 0.05,
                baseExtra: 0,
                baseAmplitude: 80,
                lengthEffect: 0.6,
                frequency: 35,
                progressScale: 4,
                phaseShiftDeg: -180,
                spring: { damping: 22, stiffness: 300 },
              }}
            >
              <div 
                className={`flex items-center bg-[#f9fafb] rounded-3xl shadow-[0_18px_40px_rgba(15,23,42,0.06)] tilt-effect smooth-hover ${isVisible['step-01'] ? 'fade-in' : ''}`}
                style={{ 
                  gap: '64px', 
                  borderRadius: '24px', 
                  padding: '40px',
                  ...tiltStyles['step-01']
                }}
                onMouseMove={(e) => handleMouseMove(e, 'step-01')}
                onMouseLeave={() => handleMouseLeave('step-01')}
                ref={(el) => (sectionRefs.current['step-01'] = el)}
                data-section-key="step-01"
              >
                <div className="flex-1" style={{ maxWidth: '420px' }}>
                  <p className="text-xs text-[#9ca3af] uppercase mb-3" style={{ fontSize: '12px', color: '#9ca3af', letterSpacing: '0.16em', marginBottom: '12px' }}>01</p>
                  <h3 className="font-semibold mb-4 text-[#111827]" style={{ fontSize: '28px', fontWeight: 600, marginBottom: '16px' }}>Smart Content Discovery</h3>
                <p className="text-base text-[#4b5563]" style={{ fontSize: '16px', color: '#4b5563', lineHeight: 1.7, maxWidth: '420px' }}>
                  Analyze top-performing Instagram videos from any creator or discover trending topics on LinkedIn. 
                  Our AI extracts visual patterns, engagement metrics, and content strategies that drive results.
                </p>
              </div>
              <div className="flex-1 flex items-center justify-center" style={{ maxWidth: '420px' }}>
                <div className="w-full h-64 bg-gradient-to-br from-purple-100 via-pink-100 to-blue-100 rounded-2xl"></div>
                </div>
              </div>
            </WavyBlockItem>

            {/* Step 02 */}
            <WavyBlockItem 
              index={1}
              config={{
                baseOffsetFactor: 0.05,
                baseExtra: 0,
                baseAmplitude: 80,
                lengthEffect: 0.6,
                frequency: 35,
                progressScale: 4,
                phaseShiftDeg: -180,
                spring: { damping: 22, stiffness: 300 },
              }}
            >
              <div 
                className={`flex items-center bg-[#f9fafb] rounded-3xl shadow-[0_18px_40px_rgba(15,23,42,0.06)] tilt-effect smooth-hover ${isVisible['step-02'] ? 'fade-in fade-in-delay-1' : ''}`}
                style={{ 
                  gap: '64px', 
                  borderRadius: '24px', 
                  padding: '40px',
                  ...tiltStyles['step-02']
                }}
                onMouseMove={(e) => handleMouseMove(e, 'step-02')}
                onMouseLeave={() => handleMouseLeave('step-02')}
                ref={(el) => (sectionRefs.current['step-02'] = el)}
                data-section-key="step-02"
              >
                <div className="flex-1 flex items-center justify-center order-1" style={{ maxWidth: '420px' }}>
                  <div className="w-full h-64 bg-gradient-to-br from-blue-100 via-indigo-100 to-purple-100 rounded-2xl"></div>
                </div>
                <div className="flex-1 order-2" style={{ maxWidth: '420px' }}>
                  <p className="text-xs text-[#9ca3af] uppercase mb-3" style={{ fontSize: '12px', color: '#9ca3af', letterSpacing: '0.16em', marginBottom: '12px' }}>02</p>
                  <h3 className="font-semibold mb-4 text-[#111827]" style={{ fontSize: '28px', fontWeight: 600, marginBottom: '16px' }}>AI Script Generation</h3>
                <p className="text-base text-[#4b5563]" style={{ fontSize: '16px', color: '#4b5563', lineHeight: 1.7, maxWidth: '420px' }}>
                  GPT-4 with Structured Outputs creates professional Sora video scripts. 
                  Each script includes visual style, camera movements, lighting, and timing—ready for AI video generation.
                </p>
                </div>
              </div>
            </WavyBlockItem>

            {/* Step 03 */}
            <WavyBlockItem 
              index={2}
              config={{
                baseOffsetFactor: 0.05,
                baseExtra: 0,
                baseAmplitude: 80,
                lengthEffect: 0.6,
                frequency: 35,
                progressScale: 4,
                phaseShiftDeg: -180,
                spring: { damping: 22, stiffness: 300 },
              }}
            >
              <div 
                className={`flex items-center bg-[#f9fafb] rounded-3xl shadow-[0_18px_40px_rgba(15,23,42,0.06)] tilt-effect smooth-hover ${isVisible['step-03'] ? 'fade-in fade-in-delay-2' : ''}`}
                style={{ 
                  gap: '64px', 
                  borderRadius: '24px', 
                  padding: '40px',
                  ...tiltStyles['step-03']
                }}
                onMouseMove={(e) => handleMouseMove(e, 'step-03')}
                onMouseLeave={() => handleMouseLeave('step-03')}
                ref={(el) => (sectionRefs.current['step-03'] = el)}
                data-section-key="step-03"
              >
                <div className="flex-1" style={{ maxWidth: '420px' }}>
                  <p className="text-xs text-[#9ca3af] uppercase mb-3" style={{ fontSize: '12px', color: '#9ca3af', letterSpacing: '0.16em', marginBottom: '12px' }}>03</p>
                  <h3 className="font-semibold mb-4 text-[#111827]" style={{ fontSize: '28px', fontWeight: 600, marginBottom: '16px' }}>Sora Video Generation</h3>
                <p className="text-base text-[#4b5563]" style={{ fontSize: '16px', color: '#4b5563', lineHeight: 1.7, maxWidth: '420px' }}>
                  Transform scripts into professional videos using OpenAI Sora. 
                  Generate 5-16 second videos with cinematic quality, ready to download and share across your content pipeline.
                </p>
              </div>
              <div className="flex-1 flex items-center justify-center" style={{ maxWidth: '420px' }}>
                <div className="w-full h-64 bg-gradient-to-br from-green-100 via-emerald-100 to-teal-100 rounded-2xl"></div>
              </div>
            </div>
            </WavyBlockItem>
          </WavyBlock>
        </div>
      </div>

      {/* Products */}
      <div 
        className="max-w-[1120px] mx-auto px-10 py-20 section-snap" 
        style={{ paddingLeft: '80px', paddingRight: '80px' }}
        ref={(el) => (sectionRefs.current['products'] = el)}
        data-section-key="products"
      >
        <div className={`mb-12 ${isVisible['products'] ? 'fade-in' : ''}`}>
          <p className="text-xs text-[#9ca3af] uppercase mb-3" style={{ fontSize: '12px', color: '#9ca3af', letterSpacing: '0.16em', marginBottom: '12px' }}>PRODUCTS</p>
          <h2 className="font-semibold text-[#111827]" style={{ fontSize: '28px', fontWeight: 600 }}>
            Two tools. One pipeline.
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Instagram Tool */}
          <div 
            onClick={() => window.location.href = '/signup'}
            className={`group bg-[#f9fafb] border border-[#e5e7eb] rounded-3xl p-10 cursor-pointer tilt-effect smooth-hover ${isVisible['product-instagram'] ? 'fade-in fade-in-delay-1' : ''}`}
            style={{
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              ...tiltStyles['product-instagram']
            }}
            onMouseMove={(e) => handleMouseMove(e, 'product-instagram')}
            onMouseLeave={() => handleMouseLeave('product-instagram')}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(15, 23, 42, 0.12)'
            }}
            ref={(el) => (sectionRefs.current['product-instagram'] = el)}
            data-section-key="product-instagram"
          >
            <h3 className="text-xl font-semibold mb-3 text-[#111827]">Instagram Video Analysis</h3>
            <p className="text-sm text-[#4b5563] mb-6 leading-relaxed">
              Transform existing Instagram content into new viral videos with AI-powered analysis
            </p>

            <div className="space-y-2 mb-6">
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">Automatic video scraping</span>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">AI transcription with Whisper</span>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">Vision API analysis</span>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">Sora video generation</span>
              </div>
            </div>

            <div className="text-sm text-[#111827] font-medium">
              Launch Tool →
            </div>
          </div>

          {/* LinkedIn Tool */}
          <div 
            onClick={() => window.location.href = '/signup'}
            className={`group bg-[#f9fafb] border border-[#e5e7eb] rounded-3xl p-10 cursor-pointer tilt-effect smooth-hover ${isVisible['product-linkedin'] ? 'fade-in fade-in-delay-2' : ''}`}
            style={{
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
              ...tiltStyles['product-linkedin']
            }}
            onMouseMove={(e) => handleMouseMove(e, 'product-linkedin')}
            onMouseLeave={() => handleMouseLeave('product-linkedin')}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 20px 40px rgba(15, 23, 42, 0.12)'
            }}
            ref={(el) => (sectionRefs.current['product-linkedin'] = el)}
            data-section-key="product-linkedin"
          >
            <h3 className="text-xl font-semibold mb-3 text-[#111827]">LinkedIn Trend Videos</h3>
            <p className="text-sm text-[#4b5563] mb-6 leading-relaxed">
              Create professional content from trending industry topics with AI assistance
            </p>

            <div className="space-y-2 mb-6">
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">Real-time trend discovery</span>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">Profile and post scraping</span>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">AI conversational interface</span>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-1.5 h-1.5 rounded-full bg-[#111827] mt-1.5"></div>
                <span className="text-sm text-[#4b5563]">Professional video output</span>
              </div>
            </div>

            <div className="text-sm text-[#111827] font-medium">
              Launch Tool →
            </div>
          </div>
        </div>
      </div>

      {/* CTA */}
      <div 
        className="max-w-[1120px] mx-auto px-10 py-20 section-snap" 
        style={{ paddingLeft: '80px', paddingRight: '80px' }}
        ref={(el) => (sectionRefs.current['cta'] = el)}
        data-section-key="cta"
      >
        <div 
          className={`bg-[#f9fafb] rounded-3xl text-center tilt-effect smooth-hover ${isVisible['cta'] ? 'fade-in' : ''}`}
          style={{ 
            borderRadius: '24px', 
            padding: '64px',
            ...tiltStyles['cta']
          }}
          onMouseMove={(e) => handleMouseMove(e, 'cta')}
          onMouseLeave={() => handleMouseLeave('cta')}
        >
          <h2 className="font-semibold mb-4 text-[#111827]" style={{ fontSize: '28px', fontWeight: 600, marginBottom: '16px' }}>
            Ready to achieve content market fit?
          </h2>
          <p className="text-base text-[#4b5563] mb-8 max-w-xl mx-auto" style={{ fontSize: '16px', color: '#4b5563', marginBottom: '32px' }}>
            Join creators using AI to build sustainable content pipelines
          </p>
          <button
            onClick={handleGetStarted}
            className="px-8 py-3 bg-black text-white text-sm font-medium rounded-full smooth-hover"
            style={{ 
              paddingLeft: '24px', 
              paddingRight: '24px', 
              paddingTop: '10px', 
              paddingBottom: '10px',
              borderRadius: '999px',
              fontSize: '14px',
              fontWeight: 500,
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px) scale(1.05)'
              e.currentTarget.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0) scale(1)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            Book a Demo
          </button>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t mt-20" style={{ borderColor: '#e5e7eb' }}>
        <div className="max-w-[1120px] mx-auto px-10 py-8" style={{ paddingLeft: '80px', paddingRight: '80px' }}>
          <div className="flex items-center justify-between text-sm" style={{ fontSize: '14px', color: '#6b7280' }}>
            <div>Powered by OpenAI GPT-4, Whisper, and Sora</div>
            <div>© 2025 VideoHook</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LandingPage











