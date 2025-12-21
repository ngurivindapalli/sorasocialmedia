import { useState, useEffect, useRef } from 'react'
import '../App.css'

function TikTokTools() {
  const [isVisible, setIsVisible] = useState({})
  const sectionRefs = useRef({})

  // Scroll fade-in effect
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

  return (
    <div 
      className="min-h-screen flex items-center justify-center"
      style={{ 
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif",
        paddingTop: '80px',
        paddingBottom: '80px',
        paddingLeft: '40px',
        paddingRight: '40px'
      }}
    >
      <div 
        className={`max-w-2xl mx-auto text-center ${isVisible['placeholder'] ? 'fade-in' : ''}`}
        ref={(el) => (sectionRefs.current['placeholder'] = el)}
        data-section-key="placeholder"
      >
        <div 
          className="bg-white rounded-3xl p-12 shadow-[0_18px_40px_rgba(15,23,42,0.06)] smooth-hover"
          style={{
            borderRadius: '24px',
            padding: '64px',
            border: '1px solid #e5e7eb'
          }}
        >
          <div 
            className="w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center"
            style={{
              backgroundColor: '#f9fafb',
              marginBottom: '24px'
            }}
          >
            <span style={{ fontSize: '40px' }}>🎵</span>
          </div>
          <h2 
            className="font-semibold mb-4 text-[#111827]"
            style={{ 
              fontSize: '28px', 
              fontWeight: 600, 
              marginBottom: '16px' 
            }}
          >
            TikTok Tools
          </h2>
          <p 
            className="text-base text-[#4b5563]"
            style={{ 
              fontSize: '16px', 
              color: '#4b5563', 
              lineHeight: 1.7 
            }}
          >
            TikTok integration coming soon! This feature will allow you to analyze trending TikTok videos and generate Sora video hooks.
          </p>
        </div>
      </div>
    </div>
  )
}

export default TikTokTools

