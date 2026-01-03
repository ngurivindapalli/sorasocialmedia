import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import '../App.css'
import Logo from './Logo'
import FallingPostsGallery from './FallingPostsGallery'

// Custom hook for scroll animations (Meridian-style)
function useScrollAnimation(options = {}) {
  const [isVisible, setIsVisible] = useState(false)
  const [hasAnimated, setHasAnimated] = useState(false)
  const elementRef = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasAnimated) {
            setIsVisible(true)
            if (!options.repeat) {
              setHasAnimated(true)
            }
          } else if (!entry.isIntersecting && options.repeat) {
            setIsVisible(false)
          }
        })
      },
      {
        threshold: options.threshold || 0.1,
        rootMargin: options.rootMargin || '0px 0px -50px 0px',
      }
    )

    if (elementRef.current) {
      observer.observe(elementRef.current)
    }

    return () => {
      if (elementRef.current) {
        observer.unobserve(elementRef.current)
      }
    }
  }, [hasAnimated, options.repeat, options.threshold, options.rootMargin])

  return [elementRef, isVisible]
}

// Hook for counting numbers on scroll
function useCountUp(end, duration = 2000, isVisible) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    if (!isVisible) return

    let startTime = null
    const startValue = 0

    const animate = (currentTime) => {
      if (!startTime) startTime = currentTime
      const progress = Math.min((currentTime - startTime) / duration, 1)
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4)
      const currentCount = Math.floor(startValue + (end - startValue) * easeOutQuart)
      
      setCount(currentCount)

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        setCount(end)
      }
    }

    requestAnimationFrame(animate)
  }, [isVisible, end, duration])

  return count
}

function GrowthAnalyticsSection() {
  const [isVisible, setIsVisible] = useState(false)
  const [graphProgress, setGraphProgress] = useState(0)
  const sectionRef = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          setIsVisible(entry.isIntersecting)
        })
      },
      { threshold: 0.1 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    const handleScroll = () => {
      if (!sectionRef.current) return
      
      const rect = sectionRef.current.getBoundingClientRect()
      const windowHeight = window.innerHeight
      const elementTop = rect.top
      const elementHeight = rect.height
      
      // Calculate scroll progress: 0 when element enters viewport, 1 when it's centered
      let progress = 0
      if (elementTop < windowHeight && elementTop + elementHeight > 0) {
        // Element is in viewport
        const viewportCenter = windowHeight / 2
        const elementCenter = elementTop + elementHeight / 2
        const distanceFromCenter = Math.abs(viewportCenter - elementCenter)
        
        // Start animating when element is 200px from center, finish when centered
        const startDistance = 400
        const endDistance = 0
        const totalDistance = startDistance - endDistance
        
        if (distanceFromCenter <= startDistance) {
          const normalizedDistance = Math.max(0, Math.min(1, (startDistance - distanceFromCenter) / totalDistance))
          // Ease out for smooth animation
          const eased = 1 - Math.pow(1 - normalizedDistance, 3)
          progress = eased
        }
      }
      
      setGraphProgress(progress * 100)
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll() // Initial calculation

    return () => {
      window.removeEventListener('scroll', handleScroll)
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  // Graph data points (months and growth percentages)
  const graphData = [
    { month: 'Month 1', value: 15 },
    { month: 'Month 2', value: 28 },
    { month: 'Month 3', value: 42 },
    { month: 'Month 4', value: 58 },
    { month: 'Month 5', value: 75 },
    { month: 'Month 6', value: 92 },
  ]

  const maxValue = 100
  const graphHeight = 300
  const graphWidth = 500

  return (
    <div ref={sectionRef} className="max-w-[1400px] mx-auto px-6" style={{ paddingLeft: '60px', paddingRight: '60px' }}>
      {/* Two-Column Layout - Meridian Style */}
      <div className="grid md:grid-cols-2 gap-12 items-center mb-12">
        {/* Left Column: Text Content */}
        <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <h2 className="text-4xl md:text-5xl font-bold text-[#111827] mb-6" style={{ fontSize: '48px', fontWeight: 700, marginBottom: '24px', lineHeight: '1.1' }}>
            See your social media grow
          </h2>
          <p className="text-xl text-[#4b5563] mb-6" style={{ fontSize: '20px', marginBottom: '24px', lineHeight: '1.6' }}>
            Companies using Aigis Marketing see an average of 3x growth in engagement and reach within 6 months. Our AI-powered content pipeline helps you create, analyze, and optimize faster than ever.
          </p>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[#1e293b] flex items-center justify-center flex-shrink-0 mt-1">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-[#111827]" style={{ fontSize: '18px', fontWeight: 600 }}>3x average engagement increase</p>
                <p className="text-base text-[#4b5563]" style={{ fontSize: '16px' }}>Consistent growth across Instagram and LinkedIn</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[#1e293b] flex items-center justify-center flex-shrink-0 mt-1">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-[#111827]" style={{ fontSize: '18px', fontWeight: 600 }}>10x faster content creation</p>
                <p className="text-base text-[#4b5563]" style={{ fontSize: '16px' }}>From analysis to published video in minutes, not days</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[#1e293b] flex items-center justify-center flex-shrink-0 mt-1">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="text-lg font-semibold text-[#111827]" style={{ fontSize: '18px', fontWeight: 600 }}>Data-driven optimization</p>
                <p className="text-base text-[#4b5563]" style={{ fontSize: '16px' }}>Real-time insights help you refine your strategy continuously</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Animated Graph */}
        <div className={`transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="bg-white border border-[#e5e7eb] rounded-xl p-8 shadow-lg" style={{ borderRadius: '12px', padding: '32px' }}>
            <div className="mb-6">
              <h3 className="text-xl font-semibold text-[#111827] mb-2" style={{ fontSize: '20px', fontWeight: 600, marginBottom: '8px' }}>
                Engagement Growth
              </h3>
              <p className="text-sm text-[#4b5563]" style={{ fontSize: '14px' }}>Average engagement rate over 6 months</p>
            </div>
            <div className="relative" style={{ height: `${graphHeight}px`, width: '100%' }}>
              {/* Y-axis labels */}
              <div className="absolute left-0 top-0 bottom-0 flex flex-col justify-between pr-3" style={{ width: '40px' }}>
                <span className="text-xs text-[#6b7280]" style={{ fontSize: '12px' }}>100%</span>
                <span className="text-xs text-[#6b7280]" style={{ fontSize: '12px' }}>75%</span>
                <span className="text-xs text-[#6b7280]" style={{ fontSize: '12px' }}>50%</span>
                <span className="text-xs text-[#6b7280]" style={{ fontSize: '12px' }}>25%</span>
                <span className="text-xs text-[#6b7280]" style={{ fontSize: '12px' }}>0%</span>
              </div>

              {/* Graph area */}
              <div className="ml-10 relative" style={{ height: `${graphHeight}px`, width: 'calc(100% - 40px)' }}>
                {/* Grid lines and animated graph */}
                <svg 
                  className="absolute inset-0 w-full h-full" 
                  viewBox={`0 0 ${graphWidth} ${graphHeight}`}
                  preserveAspectRatio="none"
                  style={{ overflow: 'visible' }}
                >
                  <defs>
                    <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#1e293b" stopOpacity="0.8" />
                      <stop offset="100%" stopColor="#1e293b" stopOpacity="0.2" />
                    </linearGradient>
                  </defs>

                  {/* Grid lines */}
                  {[0, 25, 50, 75, 100].map((y) => (
                    <line
                      key={y}
                      x1="0"
                      y1={(100 - y) * (graphHeight / 100)}
                      x2={graphWidth}
                      y2={(100 - y) * (graphHeight / 100)}
                      stroke="#e5e7eb"
                      strokeWidth="1"
                    />
                  ))}
                  
                  {/* Area fill */}
                  <path
                    d={`M 0 ${graphHeight} ${graphData.map((point, index) => {
                      const x = (index / (graphData.length - 1)) * graphWidth
                      const animatedValue = (point.value / maxValue) * (graphProgress / 100)
                      const y = graphHeight - (animatedValue * graphHeight)
                      return `L ${x} ${y}`
                    }).join(' ')} L ${graphWidth} ${graphHeight} Z`}
                    fill="url(#lineGradient)"
                    opacity={isVisible ? 1 : 0}
                    style={{ transition: 'opacity 0.5s' }}
                  />

                  {/* Line */}
                  <path
                    d={`M 0 ${graphHeight} ${graphData.map((point, index) => {
                      const x = (index / (graphData.length - 1)) * graphWidth
                      const animatedValue = (point.value / maxValue) * (graphProgress / 100)
                      const y = graphHeight - (animatedValue * graphHeight)
                      return `L ${x} ${y}`
                    }).join(' ')}`}
                    fill="none"
                    stroke="#1e293b"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    opacity={isVisible ? 1 : 0}
                    style={{ transition: 'opacity 0.5s' }}
                  />

                  {/* Data points */}
                  {graphData.map((point, index) => {
                    const x = (index / (graphData.length - 1)) * graphWidth
                    const animatedValue = (point.value / maxValue) * (graphProgress / 100)
                    const y = graphHeight - (animatedValue * graphHeight)
                    const pointProgress = (index + 1) * (100 / graphData.length)
                    return (
                      <g key={index}>
                        <circle
                          cx={x}
                          cy={y}
                          r="6"
                          fill="#1e293b"
                          opacity={isVisible && graphProgress >= pointProgress ? 1 : 0}
                          style={{ transition: 'opacity 0.3s' }}
                        />
                        <circle
                          cx={x}
                          cy={y}
                          r="10"
                          fill="#1e293b"
                          opacity={isVisible && graphProgress >= pointProgress ? 0.2 : 0}
                          style={{ transition: 'opacity 0.3s' }}
                        />
                      </g>
                    )
                  })}
                </svg>

                {/* X-axis labels */}
                <div className="absolute bottom-0 left-0 right-0 flex justify-between mt-2" style={{ marginTop: '8px' }}>
                  {graphData.map((point, index) => (
                    <span key={index} className="text-xs text-[#6b7280]" style={{ fontSize: '12px' }}>
                      {point.month.split(' ')[1]}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Two Boxes: Competitor Analysis & Brand Personalization */}
      <div className="grid md:grid-cols-2 gap-8 mt-12">
        {/* Competitor Analysis Box */}
        <div 
          className={`bg-[#1e293b] border border-[#1e293b] rounded-xl p-8 transition-all duration-1000 delay-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
          style={{ 
            borderRadius: '12px', 
            padding: '32px',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#334155'
            e.currentTarget.style.boxShadow = '0 0 20px rgba(30, 41, 59, 0.3), 0 0 40px rgba(30, 41, 59, 0.15)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#1e293b'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-lg bg-[#0f172a] flex items-center justify-center" style={{ borderRadius: '8px' }}>
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-2xl font-semibold text-white" style={{ fontSize: '24px', fontWeight: 600 }}>
              Competitor Analysis
            </h3>
          </div>
          <p className="text-base text-white/80 mb-4" style={{ fontSize: '16px', color: 'rgba(255, 255, 255, 0.8)', lineHeight: '1.7', marginBottom: '16px' }}>
            Analyze top-performing creators and competitors in your space. Our AI extracts visual patterns, engagement strategies, and content themes that drive results.
          </p>
          <ul className="space-y-2">
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-white/60 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm text-white/70" style={{ fontSize: '14px' }}>Identify top-performing content patterns</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-white/60 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm text-white/70" style={{ fontSize: '14px' }}>Track engagement metrics and trends</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-white/60 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm text-white/70" style={{ fontSize: '14px' }}>Discover what resonates with your audience</span>
            </li>
          </ul>
        </div>

        {/* Brand Personalization Box */}
        <div 
          className={`bg-[#1e293b] border border-[#1e293b] rounded-xl p-8 transition-all duration-1000 delay-700 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
          style={{ 
            borderRadius: '12px', 
            padding: '32px',
            transition: 'all 0.3s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = '#334155'
            e.currentTarget.style.boxShadow = '0 0 20px rgba(30, 41, 59, 0.3), 0 0 40px rgba(30, 41, 59, 0.15)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = '#1e293b'
            e.currentTarget.style.boxShadow = 'none'
          }}
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="w-12 h-12 rounded-lg bg-[#0f172a] flex items-center justify-center" style={{ borderRadius: '8px' }}>
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </div>
            <h3 className="text-2xl font-semibold text-white" style={{ fontSize: '24px', fontWeight: 600 }}>
              Brand Personalization
            </h3>
          </div>
          <p className="text-base text-white/80 mb-4" style={{ fontSize: '16px', color: 'rgba(255, 255, 255, 0.8)', lineHeight: '1.7', marginBottom: '16px' }}>
            Your brand context is what makes your content unique. We learn your brand's voice, style, and messaging so every piece of content feels authentically yours—not generic AI output.
          </p>
          <ul className="space-y-2">
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-white/60 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm text-white/70" style={{ fontSize: '14px' }}>Build a lasting brand memory that improves with every piece of content</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-white/60 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm text-white/70" style={{ fontSize: '14px' }}>Ensure every image and video matches your brand's unique style and voice</span>
            </li>
            <li className="flex items-start gap-2">
              <svg className="w-5 h-5 text-white/60 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm text-white/70" style={{ fontSize: '14px' }}>Stand out from competitors with content that's unmistakably yours</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function UseCasesSection({ useCases }) {
  const sectionRef = useRef(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
          }
        })
      },
      { threshold: 0.2 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  // Extended list of user cases for infinite loop
  const allUserCases = [
    'Content Creators',
    'CEOs',
    'Influencers',
    'Marketing Teams',
    'Agencies',
    'Founders',
    'Executives',
    'Social Media Managers',
    'Brand Managers',
    'Entrepreneurs',
    'Small Business Owners',
    'E-commerce Brands',
    'SaaS Companies',
    'Consultants',
    'Coaches',
    'Educators',
    'Non-profits',
    'Startups',
    'Enterprise Teams',
    'Freelancers',
  ]

  // Navy blue gradient variations
  const navyGradients = [
    'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
    'linear-gradient(135deg, #334155 0%, #1e293b 100%)',
    'linear-gradient(135deg, #475569 0%, #334155 100%)',
    'linear-gradient(135deg, #1e293b 0%, #334155 100%)',
    'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
    'linear-gradient(135deg, #334155 0%, #475569 100%)',
  ]

  return (
    <div 
      ref={sectionRef}
      className="py-32 bg-white relative" 
      style={{ paddingTop: '80px', paddingBottom: '100px', minHeight: '600px' }}
    >
      <div className="max-w-[1400px] mx-auto px-6 relative" style={{ paddingLeft: '60px', paddingRight: '60px' }}>
        {/* Heading - Above boxes */}
        <div className="text-center mb-12" style={{ marginBottom: '48px' }}>
          <h2 className="text-4xl md:text-5xl font-bold text-[#111827] mb-6" style={{ fontSize: '48px', fontWeight: 700, marginBottom: '24px', lineHeight: '1.1' }}>
            Built for Anyone
          </h2>
        </div>

        {/* Infinite Scrolling Boxes - Middle section */}
        <div 
          className="relative mb-8"
          style={{ 
            marginBottom: '32px',
            height: '160px',
            overflow: 'hidden',
            paddingTop: '10px',
            paddingBottom: '10px',
            position: 'relative',
          }}
        >
          {/* Fade gradients at edges for seamless look */}
          <div 
            className="absolute left-0 top-0 bottom-0 z-10 pointer-events-none"
            style={{
              width: '150px',
              background: 'linear-gradient(to right, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0))',
            }}
          />
          <div 
            className="absolute right-0 top-0 bottom-0 z-10 pointer-events-none"
            style={{
              width: '150px',
              background: 'linear-gradient(to left, rgba(255, 255, 255, 1), rgba(255, 255, 255, 0))',
            }}
          />
          
          <div 
            className="absolute left-0 flex gap-10"
            style={{ 
              zIndex: 1, 
              pointerEvents: 'none', 
              height: '140px',
              animation: isVisible ? 'scroll-seamless 60s linear infinite' : 'none',
              willChange: 'transform',
            }}
          >
            {/* Duplicate boxes for seamless loop - need 3 sets for perfect loop */}
            {[...Array(3)].map((_, duplicateIndex) => (
              <div key={duplicateIndex} className="flex gap-10" style={{ flexShrink: 0 }}>
                {allUserCases.map((userCase, index) => {
                  const gradientIndex = index % navyGradients.length
                  // Same rotation for all boxes - consistent angle
                  const rotation = -4 // Single consistent rotation for all
                  
                  return (
                    <div
                      key={`${duplicateIndex}-${index}`}
                      className="rounded-xl overflow-hidden shadow-lg border border-[#1e293b]/30 flex-shrink-0"
                      style={{
                        width: '140px',
                        height: '140px',
                        background: navyGradients[gradientIndex],
                        transform: `rotate(${rotation}deg)`,
                        minWidth: '140px',
                        maxWidth: '140px',
                      }}
                    >
                      <div 
                        className="w-full h-full flex items-center justify-center text-white font-semibold text-center px-2"
                        style={{ 
                          fontSize: '13px',
                          transform: `rotate(${-rotation}deg)`,
                          lineHeight: '1.2',
                        }}
                      >
                        {userCase}
                      </div>
                    </div>
                  )
                })}
              </div>
            ))}
          </div>
        </div>

        {/* Subtext - Below boxes */}
        <div className="text-center">
          <p className="text-2xl text-[#111827] font-medium" style={{ fontSize: '24px', lineHeight: '1.5', fontWeight: 500 }}>
            Whether you're a solo creator, a CEO, or a marketing team, Aigis Marketing scales with you
          </p>
        </div>
      </div>
    </div>
  )
}

function FinalCTASection({ handleBookCall }) {
  const [ctaRef, ctaVisible] = useScrollAnimation({ threshold: 0.2 })

  return (
    <div className="py-20 bg-white" style={{ paddingTop: '40px', paddingBottom: '80px' }}>
      <div 
        ref={ctaRef}
        className={`max-w-[1200px] mx-auto px-6 text-center transition-all duration-1000 ${ctaVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
        style={{ paddingLeft: '40px', paddingRight: '40px' }}
      >
        <h2 className="text-4xl font-bold text-[#111827] mb-4" style={{ fontSize: '40px', fontWeight: 700, marginBottom: '16px' }}>
          Ready to dominate social media?
        </h2>
        <p className="text-xl text-[#4b5563] mb-8 max-w-2xl mx-auto" style={{ fontSize: '20px', marginBottom: '32px' }}>
          Join a growing community using AI to create brand-aligned ads and content that actually convert
        </p>
        <button
          onClick={handleBookCall}
          className="px-6 py-3 bg-[#1e293b] text-white text-sm font-medium rounded-lg smooth-hover inline-flex items-center transition-all duration-300 hover:scale-105"
          style={{
            paddingLeft: '24px',
            paddingRight: '24px',
            paddingTop: '12px',
            paddingBottom: '12px',
            fontSize: '14px',
            fontWeight: 500,
            borderRadius: '8px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#334155'
            e.currentTarget.style.transform = 'translateY(-2px) scale(1.05)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#1e293b'
            e.currentTarget.style.transform = 'translateY(0) scale(1)'
          }}
        >
          Get Started Free
          <span className="ml-2">→</span>
        </button>
      </div>
    </div>
  )
}

function TechnologySection() {
  const [leftRef, leftVisible] = useScrollAnimation({ threshold: 0.2 })
  const [rightRef, rightVisible] = useScrollAnimation({ threshold: 0.2 })

  return (
    <div className="py-20 bg-white" style={{ paddingTop: '80px', paddingBottom: '80px' }}>
      <div className="max-w-[1200px] mx-auto px-6" style={{ paddingLeft: '40px', paddingRight: '40px' }}>
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div 
            ref={leftRef}
            className={`transition-all duration-1000 ${leftVisible ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-8'}`}
          >
            <h3 className="text-3xl font-bold text-[#111827] mb-4" style={{ fontSize: '32px', fontWeight: 700, marginBottom: '16px' }}>
              Powered by cutting-edge AI
            </h3>
            <p className="text-lg text-[#4b5563] mb-6" style={{ fontSize: '18px', marginBottom: '24px' }}>
              Aigis Marketing combines the best AI models to deliver professional results
            </p>
            <p className="text-base text-[#4b5563] mb-6" style={{ fontSize: '16px', lineHeight: '1.7', marginBottom: '24px' }}>
              We use GPT-4 for intelligent script generation, Whisper for accurate audio transcription, Google Imagen for brand-aligned image generation, and Veo 3.1 for cinematic video generation. Every component is optimized for quality and speed.
            </p>
            <div className="flex flex-wrap gap-3">
              <span className="px-4 py-2 bg-[#1e293b] border border-[#1e293b] rounded-lg text-sm text-white transition-all duration-300 hover:scale-105">GPT-4</span>
              <span className="px-4 py-2 bg-[#1e293b] border border-[#1e293b] rounded-lg text-sm text-white transition-all duration-300 hover:scale-105">Veo 3.1</span>
              <span className="px-4 py-2 bg-[#1e293b] border border-[#1e293b] rounded-lg text-sm text-white transition-all duration-300 hover:scale-105">Whisper</span>
              <span className="px-4 py-2 bg-[#1e293b] border border-[#1e293b] rounded-lg text-sm text-white transition-all duration-300 hover:scale-105">Imagen</span>
              <span className="px-4 py-2 bg-[#1e293b] border border-[#1e293b] rounded-lg text-sm text-white transition-all duration-300 hover:scale-105">Memory (S3 + Mem0)</span>
            </div>
          </div>
          <div 
            ref={rightRef}
            className={`bg-[#1e293b] border border-[#1e293b] rounded-xl p-8 transition-all duration-1000 delay-300 ${rightVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'}`}
            style={{ 
              borderRadius: '12px', 
              padding: '32px',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#334155'
              e.currentTarget.style.boxShadow = '0 0 20px rgba(30, 41, 59, 0.3), 0 0 40px rgba(30, 41, 59, 0.15)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#1e293b'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <div className="space-y-4">
              <div 
                className="p-4 bg-[#0f172a] rounded-lg border border-[#334155] transition-all duration-300"
                style={{ transition: 'all 0.3s ease' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#475569'
                  e.currentTarget.style.boxShadow = '0 0 15px rgba(71, 85, 105, 0.2), 0 0 30px rgba(71, 85, 105, 0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#334155'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <p className="text-sm text-white mb-2 font-semibold" style={{ fontSize: '14px', marginBottom: '8px', fontWeight: 600 }}>Video Analysis</p>
                <p className="text-xs text-white/70" style={{ fontSize: '12px' }}>Scrape and analyze Instagram videos to understand what makes content viral</p>
              </div>
              <div 
                className="p-4 bg-[#0f172a] rounded-lg border border-[#334155] transition-all duration-300"
                style={{ transition: 'all 0.3s ease' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#475569'
                  e.currentTarget.style.boxShadow = '0 0 15px rgba(71, 85, 105, 0.2), 0 0 30px rgba(71, 85, 105, 0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#334155'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <p className="text-sm text-white mb-2 font-semibold" style={{ fontSize: '14px', marginBottom: '8px', fontWeight: 600 }}>Trend Discovery</p>
                <p className="text-xs text-white/70" style={{ fontSize: '12px' }}>Identify trending topics on LinkedIn and turn them into video content</p>
              </div>
              <div 
                className="p-4 bg-[#0f172a] rounded-lg border border-[#334155] transition-all duration-300"
                style={{ transition: 'all 0.3s ease' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#475569'
                  e.currentTarget.style.boxShadow = '0 0 15px rgba(71, 85, 105, 0.2), 0 0 30px rgba(71, 85, 105, 0.1)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = '#334155'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <p className="text-sm text-white mb-2 font-semibold" style={{ fontSize: '14px', marginBottom: '8px', fontWeight: 600 }}>AI Generation</p>
                <p className="text-xs text-white/70" style={{ fontSize: '12px' }}>Generate professional videos from scripts using Veo 3.1 and images with Google Imagen</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function SocialMediaAnalyticsSection() {
  const [isVisible, setIsVisible] = useState(false)
  const sectionRef = useRef(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsVisible(true)
          }
        })
      },
      { threshold: 0.2 }
    )

    if (sectionRef.current) {
      observer.observe(sectionRef.current)
    }

    return () => {
      if (sectionRef.current) {
        observer.unobserve(sectionRef.current)
      }
    }
  }, [])

  // Social media activity data
  const activityData = [
    { platform: 'Instagram', posts: 124, change: 32, trend: 'up' },
    { platform: 'LinkedIn', posts: 89, change: 18, trend: 'up' },
    { platform: 'TikTok', posts: 156, change: 45, trend: 'up' },
    { platform: 'Twitter', posts: 67, change: -8, trend: 'down' },
    { platform: 'Facebook', posts: 43, change: 12, trend: 'up' },
  ]

  // Post scoring data
  const scoringData = [
    { metric: 'Engagement Rate', score: 92, grade: 'A+' },
    { metric: 'Brand Alignment', score: 88, grade: 'A' },
    { metric: 'Content Quality', score: 95, grade: 'A+' },
    { metric: 'Timing Optimization', score: 85, grade: 'B+' },
    { metric: 'Audience Match', score: 90, grade: 'A' },
  ]

  return (
    <div ref={sectionRef} className="max-w-[1400px] mx-auto px-6" style={{ paddingLeft: '60px', paddingRight: '60px' }}>
      <div className="grid md:grid-cols-2 gap-8">
        {/* Left: Social Media Activity Changes */}
        <div className={`transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="bg-white border border-[#e5e7eb] rounded-xl p-8 shadow-lg" style={{ borderRadius: '12px', padding: '32px' }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-[#1e293b] flex items-center justify-center" style={{ borderRadius: '8px' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-[#111827]" style={{ fontSize: '24px', fontWeight: 600 }}>
                Social Media Activity
              </h3>
            </div>
            <p className="text-sm text-[#4b5563] mb-6" style={{ fontSize: '14px', marginBottom: '24px' }}>
              Track how your content activity changes across platforms after using Aigis Marketing
            </p>
            
            {/* Time period selector */}
            <div className="flex gap-2 mb-6">
              <button className="px-4 py-2 bg-[#1e293b] text-white text-sm font-medium rounded-lg" style={{ fontSize: '14px', fontWeight: 500, borderRadius: '8px' }}>
                Last Month
              </button>
              <button className="px-4 py-2 bg-white border border-[#e5e7eb] text-[#4b5563] text-sm font-medium rounded-lg hover:bg-gray-50" style={{ fontSize: '14px', fontWeight: 500, borderRadius: '8px' }}>
                Last 7 Days
              </button>
            </div>

            {/* Activity Table */}
            <div className="bg-[#1e293b] rounded-lg overflow-hidden" style={{ borderRadius: '8px' }}>
              <div className="grid grid-cols-3 gap-4 p-4 border-b border-[#334155]" style={{ borderBottom: '1px solid #334155' }}>
                <div className="text-sm font-semibold text-white" style={{ fontSize: '14px', fontWeight: 600 }}>Platform</div>
                <div className="text-sm font-semibold text-white" style={{ fontSize: '14px', fontWeight: 600 }}>Posts</div>
                <div className="text-sm font-semibold text-white" style={{ fontSize: '14px', fontWeight: 600 }}>Change</div>
              </div>
              {activityData.map((item, index) => (
                <div 
                  key={index} 
                  className="grid grid-cols-3 gap-4 p-4 border-b border-[#334155] last:border-b-0 transition-all duration-300 hover:bg-[#0f172a]" 
                  style={{ 
                    borderBottom: index < activityData.length - 1 ? '1px solid #334155' : 'none',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div className="text-sm text-white" style={{ fontSize: '14px' }}>{item.platform}</div>
                  <div className="text-sm text-white" style={{ fontSize: '14px' }}>{item.posts}</div>
                  <div className="flex items-center gap-1">
                    <span className={`text-sm font-medium ${item.trend === 'up' ? 'text-green-400' : 'text-red-400'}`} style={{ fontSize: '14px', fontWeight: 500 }}>
                      {item.change > 0 ? '+' : ''}{item.change}
                    </span>
                    <svg 
                      className={`w-4 h-4 ${item.trend === 'up' ? 'text-green-400' : 'text-red-400'}`} 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                    >
                      {item.trend === 'up' ? (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                      )}
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Post Scoring */}
        <div className={`transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="bg-white border border-[#e5e7eb] rounded-xl p-8 shadow-lg" style={{ borderRadius: '12px', padding: '32px' }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-[#1e293b] flex items-center justify-center" style={{ borderRadius: '8px' }}>
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold text-[#111827]" style={{ fontSize: '24px', fontWeight: 600 }}>
                Post Scoring
              </h3>
            </div>
            <p className="text-sm text-[#4b5563] mb-6" style={{ fontSize: '14px', marginBottom: '24px' }}>
              Every generated post is automatically scored across multiple dimensions to ensure quality and performance
            </p>

            {/* Scoring Cards */}
            <div className="space-y-4">
              {scoringData.map((item, index) => (
                <div 
                  key={index}
                  className="bg-[#1e293b] rounded-lg p-4 transition-all duration-300 hover:bg-[#0f172a]" 
                  style={{ 
                    borderRadius: '8px', 
                    padding: '16px',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white" style={{ fontSize: '14px', fontWeight: 500 }}>
                      {item.metric}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-white" style={{ fontSize: '18px', fontWeight: 700 }}>
                        {item.score}
                      </span>
                      <span className="px-2 py-1 bg-[#0f172a] text-white text-xs font-semibold rounded" style={{ fontSize: '12px', fontWeight: 600, borderRadius: '4px' }}>
                        {item.grade}
                      </span>
                    </div>
                  </div>
                  {/* Progress bar */}
                  <div className="w-full bg-[#0f172a] rounded-full h-2" style={{ borderRadius: '9999px', height: '8px' }}>
                    <div 
                      className="bg-white h-2 rounded-full transition-all duration-1000" 
                      style={{ 
                        borderRadius: '9999px', 
                        height: '8px',
                        width: isVisible ? `${item.score}%` : '0%',
                        transition: 'width 1s ease-out'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Overall Score */}
            <div className="mt-6 pt-6 border-t border-[#e5e7eb]">
              <div className="flex items-center justify-between">
                <span className="text-base font-semibold text-[#111827]" style={{ fontSize: '16px', fontWeight: 600 }}>
                  Overall Score
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-3xl font-bold text-[#1e293b]" style={{ fontSize: '32px', fontWeight: 700 }}>
                    {Math.round(scoringData.reduce((sum, item) => sum + item.score, 0) / scoringData.length)}
                  </span>
                  <span className="px-3 py-1 bg-[#1e293b] text-white text-sm font-semibold rounded-lg" style={{ fontSize: '14px', fontWeight: 600, borderRadius: '8px' }}>
                    A
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function LandingPage() {
  const handleBookCall = () => {
    window.location.href = '/signup'
  }

  const useCases = [
    {
      title: "Content Creators",
      description: "Scale your video production without hiring a team. Analyze what works, generate new content, and maintain your posting schedule."
    },
    {
      title: "Marketing Teams",
      description: "Turn blog posts, case studies, and reports into engaging video content. Repurpose existing content across platforms."
    },
    {
      title: "Agencies",
      description: "Deliver high-quality video content for multiple clients. Analyze competitor strategies and create videos that outperform."
    },
    {
      title: "Founders & Executives",
      description: "Build thought leadership with consistent video content. Turn LinkedIn trends into professional videos that establish your expertise."
    }
  ]

  return (
    <div className="min-h-screen bg-black text-white" style={{ fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif" }}>
      {/* Navigation */}
      <nav 
        className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm border-b border-gray-200" 
        style={{ 
          height: '64px',
        }}
      >
        <div className="max-w-[1800px] mx-auto px-6 h-full flex items-center justify-between" style={{ paddingLeft: '60px', paddingRight: '100px' }}>
          <div className="flex items-center gap-3">
            <div className="text-[#111827]">
              <Logo />
            </div>
            <span className="text-[#111827] text-lg font-semibold tracking-tight">Aigis Marketing</span>
          </div>
          <div className="flex items-center gap-8" style={{ gap: '32px' }}>
            <a href="#blog" className="text-[#111827] text-sm font-medium hover:text-[#1e293b] transition-colors">Blog</a>
            <a href="#pricing" className="text-[#111827] text-sm font-medium hover:text-[#1e293b] transition-colors">Pricing</a>
            <button
              onClick={handleBookCall}
              className="px-5 py-2 text-sm font-medium rounded-lg smooth-hover border border-[#111827]"
              style={{
                paddingLeft: '20px',
                paddingRight: '20px',
                paddingTop: '8px',
                paddingBottom: '8px',
                fontSize: '14px',
                fontWeight: 500,
                backgroundColor: 'transparent',
                color: '#111827',
                borderRadius: '8px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#f5f5f5'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              Login
            </button>
            <button
              onClick={handleBookCall}
              className="px-5 py-2 text-sm font-medium rounded-lg smooth-hover"
              style={{
                paddingLeft: '20px',
                paddingRight: '20px',
                paddingTop: '8px',
                paddingBottom: '8px',
                fontSize: '14px',
                fontWeight: 500,
                backgroundColor: '#1e293b',
                color: '#ffffff',
                borderRadius: '8px',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#334155'
                e.currentTarget.style.transform = 'translateY(-1px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#1e293b'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
            >
              Get a demo
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section with Two-Column Layout */}
      <div className="relative pt-32 pb-16 overflow-hidden" style={{ paddingTop: '120px', paddingBottom: '64px', minHeight: '700px' }}>
        {/* Gradient background */}
          <div 
          className="absolute inset-0 z-0"
            style={{ 
            background: 'linear-gradient(180deg, #f5f5f5 0%, #ffffff 30%, #1e293b 100%)',
            }}
          />
        
        {/* Two-Column Layout */}
        <div className="relative z-10 max-w-[1800px] mx-auto px-6" style={{ paddingLeft: '60px', paddingRight: '100px' }}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-2 items-center min-h-[700px]">
            
            {/* Left Column: Text Content - Pushed more to the left like Meridian */}
            <div className="flex flex-col justify-center max-w-[520px]" style={{ zIndex: 10, marginLeft: '0' }}>
              <h1 className="text-5xl md:text-6xl font-bold text-[#111827] mb-6" style={{ fontSize: '56px', fontWeight: 700, marginBottom: '24px', lineHeight: '1.1' }}>
                Generate AI content that matches your brand—images, videos, and posts that perform
          </h1>
              <p className="text-xl text-[#111827] mb-8" style={{ fontSize: '20px', marginBottom: '32px', lineHeight: '1.6' }}>
                Analyze competitors and top creators, then generate brand-aligned images and videos—all personalized to your unique brand memory and style. Your context is what makes your content stand out.
          </p>
              
              {/* CTA Buttons */}
              <div className="flex flex-row gap-4 mb-12">
          <button
            onClick={handleBookCall}
                  className="px-6 py-3 bg-[#1e293b] text-white text-sm font-medium rounded-lg smooth-hover inline-flex items-center"
            style={{
              paddingLeft: '24px',
              paddingRight: '24px',
              paddingTop: '12px',
              paddingBottom: '12px',
              fontSize: '14px',
              fontWeight: 500,
              borderRadius: '8px',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#334155'
                    e.currentTarget.style.transform = 'translateY(-1px)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#1e293b'
                    e.currentTarget.style.transform = 'translateY(0)'
                  }}
                >
                  Get a demo
                </button>
          <button
            onClick={handleBookCall}
                  className="px-6 py-3 bg-[#111827] text-white text-sm font-medium rounded-lg smooth-hover inline-flex items-center"
            style={{
              paddingLeft: '24px',
              paddingRight: '24px',
              paddingTop: '12px',
              paddingBottom: '12px',
              fontSize: '14px',
              fontWeight: 500,
              borderRadius: '8px',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
            onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = '#000000'
              e.currentTarget.style.transform = 'translateY(-1px)'
            }}
            onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = '#111827'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
                  Get started
          </button>
              </div>
              
              {/* Trust Section */}
              <div className="mt-8">
                <p className="text-sm text-[#111827] mb-4" style={{ fontSize: '14px', marginBottom: '16px' }}>
                  Trusted by 1,000+ marketers
                </p>
                {/* Partner logos placeholder - you can add actual logos later */}
                <div className="flex flex-row gap-6 items-center opacity-60">
                  <div className="text-[#111827] font-semibold text-sm">Origin</div>
                  <div className="text-[#111827] font-semibold text-sm">APL</div>
                  <div className="text-[#111827] font-semibold text-sm">Hex</div>
                  <div className="text-[#111827] font-semibold text-sm">HOORAY</div>
                  <div className="text-[#111827] font-semibold text-sm">Generation Lab</div>
                </div>
              </div>
            </div>
            
            {/* Right Column: Falling Posts Gallery - Pushed left, closer to text */}
            <div className="relative h-full min-h-[700px] w-full" style={{ zIndex: 5, paddingLeft: '-20px', paddingRight: '120px', overflow: 'visible' }}>
              <FallingPostsGallery />
            </div>
            
          </div>
        </div>
      </div>

      {/* Use Cases Section */}
      <UseCasesSection useCases={useCases} />

      {/* Growth & Analytics Section - Meridian Style */}
      <div className="py-20 bg-white" style={{ paddingTop: '60px', paddingBottom: '60px' }}>
        <GrowthAnalyticsSection />
      </div>

      {/* Social Media Analytics & Post Scoring Section */}
      <div className="py-20 bg-white" style={{ paddingTop: '60px', paddingBottom: '60px' }}>
        <SocialMediaAnalyticsSection />
      </div>


      {/* Final CTA Section */}
      <FinalCTASection handleBookCall={handleBookCall} />

      {/* Footer */}
      <div className="border-t border-[#e5e7eb] py-8 bg-white">
        <div className="max-w-[1200px] mx-auto px-6" style={{ paddingLeft: '40px', paddingRight: '40px' }}>
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm" style={{ fontSize: '14px', color: '#4b5563' }}>
            <div className="flex items-center gap-6">
              <Link to="/terms-of-service" className="text-[#1e293b] hover:underline">Terms of Service</Link>
              <Link to="/privacy-policy" className="text-[#1e293b] hover:underline">Privacy Policy</Link>
            </div>
            <div className="text-center md:text-right">
              <div>Powered by GPT-4, Whisper, Google Imagen, Veo 3.1, and Memory (S3 + Mem0)</div>
              <div className="mt-1">© 2025 Aigis Marketing</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LandingPage
