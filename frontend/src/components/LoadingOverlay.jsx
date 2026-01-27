import { Loader2, Sparkles, Brain, Image } from 'lucide-react'

/**
 * LoadingOverlay - A full-screen or section loading overlay with animations
 * 
 * Props:
 * - isLoading: boolean - Whether to show the overlay
 * - type: 'image' | 'context' | 'generic' - Type of loading (determines icon and message)
 * - message: string - Custom message to display
 * - subMessage: string - Secondary message
 * - fullScreen: boolean - Whether to cover the entire screen or just parent container
 */
function LoadingOverlay({ 
  isLoading, 
  type = 'generic', 
  message, 
  subMessage, 
  fullScreen = false 
}) {
  if (!isLoading) return null

  const getIcon = () => {
    switch (type) {
      case 'image':
        return <Image className="w-12 h-12 text-[#1e293b]" />
      case 'context':
        return <Brain className="w-12 h-12 text-[#1e293b]" />
      default:
        return <Sparkles className="w-12 h-12 text-[#1e293b]" />
    }
  }

  const getDefaultMessage = () => {
    switch (type) {
      case 'image':
        return 'Generating your image...'
      case 'context':
        return 'Gathering brand context...'
      default:
        return 'Loading...'
    }
  }

  const getDefaultSubMessage = () => {
    switch (type) {
      case 'image':
        return 'This may take 15-30 seconds'
      case 'context':
        return 'Analyzing and summarizing your brand information'
      default:
        return 'Please wait'
    }
  }

  const containerClasses = fullScreen
    ? 'fixed inset-0 z-50 bg-white/95 backdrop-blur-sm'
    : 'absolute inset-0 z-40 bg-white/95 backdrop-blur-sm rounded-lg'

  return (
    <div className={containerClasses}>
      <div className="flex flex-col items-center justify-center h-full min-h-[300px]">
        {/* Animated Icon Container */}
        <div className="relative mb-6">
          {/* Outer pulsing ring */}
          <div className="absolute inset-0 -m-4 rounded-full bg-[#1e293b]/10 animate-ping" style={{ animationDuration: '2s' }} />
          
          {/* Middle rotating ring */}
          <div className="absolute inset-0 -m-3 rounded-full border-2 border-dashed border-[#1e293b]/30 animate-spin" style={{ animationDuration: '8s' }} />
          
          {/* Icon container with bounce */}
          <div className="relative p-4 bg-gradient-to-br from-[#f5f5f5] to-white rounded-full shadow-lg animate-pulse">
            {getIcon()}
          </div>
          
          {/* Spinning loader around icon */}
          <div className="absolute -inset-2">
            <Loader2 className="w-full h-full text-[#1e293b] animate-spin" style={{ animationDuration: '2s' }} />
          </div>
        </div>

        {/* Progress dots animation */}
        <div className="flex gap-1.5 mb-6">
          <div className="w-2.5 h-2.5 bg-[#1e293b] rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2.5 h-2.5 bg-[#1e293b] rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2.5 h-2.5 bg-[#1e293b] rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>

        {/* Messages */}
        <h3 className="text-xl font-semibold text-[#111827] mb-2 text-center">
          {message || getDefaultMessage()}
        </h3>
        <p className="text-sm text-[#4b5563] text-center max-w-md px-4">
          {subMessage || getDefaultSubMessage()}
        </p>

        {/* Animated progress bar */}
        <div className="mt-6 w-48 h-1.5 bg-[#e5e7eb] rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-[#1e293b] to-[#334155] rounded-full animate-pulse"
            style={{
              width: '70%',
              animation: 'loading-progress 2s ease-in-out infinite'
            }}
          />
        </div>
      </div>

      <style jsx>{`
        @keyframes loading-progress {
          0% {
            width: 0%;
            margin-left: 0%;
          }
          50% {
            width: 70%;
            margin-left: 15%;
          }
          100% {
            width: 0%;
            margin-left: 100%;
          }
        }
      `}</style>
    </div>
  )
}

export default LoadingOverlay
