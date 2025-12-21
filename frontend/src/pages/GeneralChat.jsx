import { useState, useEffect, useRef } from 'react'
import { MessageSquare, Send, Loader2 } from 'lucide-react'
import axios from 'axios'
import '../App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function GeneralChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your AI assistant for Aigis Marketing. I can help you understand how the platform works, explain features, guide you through using Instagram and LinkedIn tools, and answer questions about video generation with Sora. What would you like to know?"
    }
  ])
  const [userInput, setUserInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const [isVisible, setIsVisible] = useState({})
  const sectionRefs = useRef({})

  // Scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
  }, [messages])

  const handleSendMessage = async () => {
    if (!userInput.trim() || loading) return

    const userMessage = userInput.trim()
    setUserInput('')
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      // Call general chat endpoint
      const response = await axios.post(`${API_URL}/api/chat/general`, {
        message: userMessage,
        conversation_history: messages
      })

      const aiResponse = response.data

      // Add AI message
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: aiResponse.message
      }])

    } catch (error) {
      console.error('Chat error:', error)
      let errorMessage = 'Failed to process request. Please try again.'
      
      if (error.code === 'ECONNREFUSED' || error.message?.includes('Network Error')) {
        errorMessage = 'Unable to connect to the backend server. Please make sure the backend is running on port 8000.'
      } else if (error.response?.data?.detail) {
        errorMessage = `Error: ${error.response.data.detail}`
      } else if (error.message) {
        errorMessage = `Error: ${error.message}`
      }
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: errorMessage
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div 
      className="min-h-screen flex flex-col"
      style={{ 
        fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif",
        backgroundColor: 'transparent'
      }}
    >
      {/* Chat Container */}
      <div 
        className="flex-1 flex flex-col max-w-4xl mx-auto w-full px-6 py-8"
        style={{ 
          paddingTop: '40px',
          paddingBottom: '40px',
          paddingLeft: '40px',
          paddingRight: '40px'
        }}
      >
        {/* Chat Messages */}
        <div 
          className="flex-1 overflow-y-auto space-y-6 mb-6"
          style={{
            minHeight: 'calc(100vh - 200px)',
            paddingBottom: '20px'
          }}
        >
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              ref={(el) => {
                if (el) {
                  sectionRefs.current[`message-${index}`] = el
                }
              }}
              data-section-key={`message-${index}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl p-4 smooth-hover ${
                  isVisible[`message-${index}`] ? 'fade-in' : ''
                }`}
                style={{
                  backgroundColor: msg.role === 'user' 
                    ? '#111827' 
                    : '#ffffff',
                  color: msg.role === 'user' 
                    ? '#ffffff' 
                    : '#111827',
                  border: msg.role === 'assistant' 
                    ? '1px solid #e5e7eb' 
                    : 'none',
                  borderRadius: '16px',
                  boxShadow: msg.role === 'assistant' 
                    ? '0 2px 8px rgba(0, 0, 0, 0.04)' 
                    : '0 2px 8px rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
              >
                <p style={{ 
                  whiteSpace: 'pre-wrap', 
                  fontSize: '15px',
                  lineHeight: 1.6,
                  margin: 0
                }}>
                  {msg.content}
                </p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div 
                className="rounded-2xl p-4 flex items-center gap-3 smooth-hover"
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '16px',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)'
                }}
              >
                <Loader2 className="w-5 h-5 animate-spin" style={{ color: '#4b5563' }} />
                <span style={{ 
                  fontSize: '15px',
                  color: '#4b5563'
                }}>
                  AI is thinking...
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div 
          className="sticky bottom-0 bg-transparent"
          style={{
            paddingTop: '20px'
          }}
        >
          <div 
            className="rounded-2xl p-4 smooth-hover"
            style={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '16px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
              transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          >
            <div className="flex gap-3 items-end">
              <div className="flex-1">
                <textarea
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about Aigis Marketing..."
                  className="w-full px-4 py-3 rounded-lg focus:outline-none resize-none"
                  style={{
                    backgroundColor: '#f9fafb',
                    border: '1px solid #e5e7eb',
                    color: '#111827',
                    fontSize: '15px',
                    minHeight: '52px',
                    maxHeight: '200px',
                    fontFamily: 'inherit',
                    lineHeight: 1.5
                  }}
                  disabled={loading}
                  rows={1}
                  onInput={(e) => {
                    const target = e.target
                    target.style.height = 'auto'
                    target.style.height = target.scrollHeight + 'px'
                  }}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={loading || !userInput.trim()}
                className="px-6 py-3 font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 smooth-hover"
                style={{
                  backgroundColor: loading || !userInput.trim() ? '#9ca3af' : '#111827',
                  color: '#ffffff',
                  fontSize: '15px',
                  fontWeight: 500,
                  borderRadius: '12px',
                  minWidth: '100px',
                  justifyContent: 'center',
                  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
                }}
                onMouseEnter={(e) => {
                  if (!loading && userInput.trim()) {
                    e.currentTarget.style.backgroundColor = '#000000'
                    e.currentTarget.style.transform = 'translateY(-1px)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!loading && userInput.trim()) {
                    e.currentTarget.style.backgroundColor = '#111827'
                    e.currentTarget.style.transform = 'translateY(0)'
                  }
                }}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Processing</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Send</span>
                  </>
                )}
              </button>
            </div>
            <p style={{ 
              fontSize: '12px',
              color: '#9ca3af',
              marginTop: '12px',
              marginLeft: '4px'
            }}>
              Try: "How does Instagram video analysis work?", "What is Sora?", "How do I use LinkedIn trends?"
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GeneralChat

