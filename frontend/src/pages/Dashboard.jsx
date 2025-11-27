import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { authUtils } from '../utils/auth'
import Logo from '../components/Logo'
import InstagramTools from './InstagramTools.jsx'
import LinkedInTools from './LinkedInTools.jsx'
import TikTokTools from './TikTokTools.jsx'
import XTools from './XTools.jsx'
import GeneralChat from './GeneralChat.jsx'
import Settings from './Settings.jsx'
import { Menu, X as XIcon, Instagram, Linkedin, Music, MessageSquare, Settings as SettingsIcon } from 'lucide-react'
import '../App.css'

function Dashboard() {
  // Persist activeTab in localStorage so it doesn't reset
  // Default to 'instagram' for testing - teammates can test Veo generation
  const [activeTab, setActiveTab] = useState(() => {
    const saved = localStorage.getItem('videohook_activeTab')
    return saved || 'instagram'
  })
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const navigate = useNavigate()
  const currentUser = authUtils.getCurrentUser()
  const [isVisible, setIsVisible] = useState({})
  const sectionRefs = useRef({})

  // Save activeTab to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('videohook_activeTab', activeTab)
  }, [activeTab])

  // Skip authentication check - allow direct access to dashboard
  // useEffect(() => {
  //   // Authentication is optional now
  // }, [navigate])

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

  // Smooth scroll behavior
  useEffect(() => {
    document.documentElement.style.scrollBehavior = 'smooth'
    return () => {
      document.documentElement.style.scrollBehavior = 'auto'
    }
  }, [])

  const handleLogout = () => {
    // No logout needed - just clear any stored data
    authUtils.logout()
    // Stay on dashboard - no redirect needed
    window.location.reload()
  }

  const socialMediaTabs = [
    { id: 'chat', label: 'Chat', icon: null },
    { id: 'linkedin', label: 'LinkedIn', icon: Linkedin },
    { id: 'instagram', label: 'Instagram', icon: Instagram },
    { id: 'tiktok', label: 'TikTok', icon: Music },
    { id: 'x', label: 'X', icon: XIcon },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ]

  const renderContent = () => {
    console.log('Rendering content for tab:', activeTab)
    switch (activeTab) {
      case 'linkedin':
        return <LinkedInTools />
      case 'instagram':
        return <InstagramTools />
      case 'tiktok':
        return <TikTokTools />
      case 'x':
        return <XTools />
      case 'settings':
        return <Settings />
      case 'chat':
      default:
        return <GeneralChat />
    }
  }

  // Log activeTab changes
  useEffect(() => {
    console.log('Active tab changed to:', activeTab)
  }, [activeTab])

  return (
    <div 
      className="min-h-screen bg-gradient-to-r from-[#cfd7f1] via-[#f0d7d2] to-[#f7f1f4] text-[#111827] inertia-scroll" 
      style={{ fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif' }}
    >
      {/* Header */}
      <header 
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md" 
        style={{ 
          height: '64px',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          borderBottom: '1px solid #e5e7eb'
        }}
      >
        <div className="h-full flex items-center justify-between w-full" style={{ paddingLeft: '8px', paddingRight: '24px' }}>
          <div className="flex items-center" style={{ gap: '8px' }}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="rounded-lg hover:bg-gray-100 transition-all flex items-center justify-center"
              style={{ 
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                padding: '8px',
                minWidth: '36px',
                minHeight: '36px'
              }}
            >
              {sidebarOpen ? <XIcon className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="text-[#111827] flex items-center">
              <Logo />
            </div>
            <span className="text-[#111827] text-lg font-semibold tracking-tight ml-1">VideoHook</span>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-sm text-[#4b5563]" style={{ fontSize: '14px' }}>
              {currentUser?.username || 'Guest'}
            </span>
            {/* Logout button removed - no authentication required */}
          </div>
        </div>
      </header>

      <div className="flex" style={{ marginTop: '64px' }}>
        {/* Sidebar */}
        <aside
          className={`fixed left-0 top-0 bottom-0 bg-white border-r border-[#e5e7eb] transition-all duration-300 z-30 overflow-y-auto`}
          style={{
            width: sidebarOpen ? '260px' : '0px',
            opacity: sidebarOpen ? 1 : 0,
            transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: sidebarOpen ? '2px 0 8px rgba(0, 0, 0, 0.05)' : 'none',
            paddingTop: '64px'
          }}
        >
          <div className="p-4 space-y-2">
            {socialMediaTabs.map((tab) => {
              const Icon = tab.icon
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    console.log('Switching to tab:', tab.id)
                    setActiveTab(tab.id)
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all smooth-hover ${
                    isActive ? 'bg-[#111827] text-white' : 'text-[#4b5563] hover:bg-[#f9fafb]'
                  }`}
                  style={{
                    fontSize: '14px',
                    fontWeight: isActive ? 500 : 400,
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    cursor: 'pointer'
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.color = '#111827'
                      e.currentTarget.style.transform = 'translateX(4px)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.color = '#4b5563'
                      e.currentTarget.style.transform = 'translateX(0)'
                    }
                  }}
                >
                  {Icon ? (
                    tab.id === 'x' ? (
                      <span className="w-5 h-5 flex items-center justify-center font-bold text-lg" style={{ fontFamily: 'system-ui' }}>𝕏</span>
                    ) : (
                      <Icon className="w-5 h-5" />
                    )
                  ) : (
                    <MessageSquare className="w-5 h-5" />
                  )}
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </aside>

        {/* Main Content */}
        <main
          className="flex-1 transition-all duration-300"
          style={{
            marginLeft: sidebarOpen ? '260px' : '0px',
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        >
          {renderContent()}
        </main>
      </div>
    </div>
  )
}

export default Dashboard
