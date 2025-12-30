import { useState } from 'react'
import { Sparkles, Check } from 'lucide-react'
import design from '../../design.json'

function VideoOptionsSelector({ 
  options, 
  onSelect, 
  isOpen 
}) {
  const [selectedOption, setSelectedOption] = useState(null)
  const { colors, typography, spacing, layout } = design

  if (!isOpen || !options || options.length === 0) return null

  const handleSelect = (option) => {
    setSelectedOption(option.id)
  }

  const handleConfirm = () => {
    if (selectedOption) {
      const option = options.find(opt => opt.id === selectedOption)
      if (option) {
        onSelect(option)
      }
    }
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div 
        className="bg-[#111] border border-gray-800 rounded-3xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        style={{
          boxShadow: '0 20px 60px rgba(0,0,0,0.5)'
        }}
      >
        <div className="flex items-center gap-3 mb-6">
          <Sparkles className="w-6 h-6" style={{ color: colors.text.primary }} />
          <h2 
            style={{
              fontSize: typography.sizes.sectionTitle,
              fontWeight: typography.weights.bold,
              color: colors.text.primary,
              fontFamily: typography.fontFamilies.heading
            }}
          >
            Choose Your Video Style
          </h2>
        </div>

        <p 
          style={{
            fontSize: typography.sizes.sm,
            color: colors.text.muted,
            marginBottom: spacing.scale['2xl'],
            fontFamily: typography.fontFamilies.body,
            lineHeight: typography.lineHeights.relaxed
          }}
        >
          We've generated {options.length} different video options based on your documents. Select the one that best fits your goals.
        </p>

        <div className="space-y-4 mb-6">
          {options.map((option) => (
            <div
              key={option.id}
              onClick={() => handleSelect(option)}
              className={`p-6 rounded-xl border-2 cursor-pointer transition-all ${
                selectedOption === option.id 
                  ? 'border-purple-500 bg-purple-500/10' 
                  : 'border-gray-700 hover:border-gray-600'
              }`}
              style={{
                backgroundColor: selectedOption === option.id 
                  ? 'rgba(139, 92, 246, 0.1)' 
                  : colors.background.section
              }}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 
                      style={{
                        fontSize: typography.sizes.md,
                        fontWeight: typography.weights.semibold,
                        color: colors.text.primary,
                        fontFamily: typography.fontFamilies.heading
                      }}
                    >
                      {option.title || `Option ${option.id}`}
                    </h3>
                    {selectedOption === option.id && (
                      <Check className="w-5 h-5 text-purple-500" />
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    {option.topic && (
                      <div>
                        <span 
                          style={{
                            fontSize: typography.sizes.xs,
                            fontWeight: typography.weights.medium,
                            color: colors.text.muted,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          Topic:
                        </span>
                        <span 
                          style={{
                            fontSize: typography.sizes.sm,
                            color: colors.text.primary,
                            marginLeft: spacing.scale.xs,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          {option.topic}
                        </span>
                      </div>
                    )}
                    
                    {option.approach && (
                      <div>
                        <span 
                          style={{
                            fontSize: typography.sizes.xs,
                            fontWeight: typography.weights.medium,
                            color: colors.text.muted,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          Approach:
                        </span>
                        <span 
                          style={{
                            fontSize: typography.sizes.sm,
                            color: colors.text.primary,
                            marginLeft: spacing.scale.xs,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          {option.approach}
                        </span>
                      </div>
                    )}
                    
                    {option.duration && (
                      <div>
                        <span 
                          style={{
                            fontSize: typography.sizes.xs,
                            fontWeight: typography.weights.medium,
                            color: colors.text.muted,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          Duration:
                        </span>
                        <span 
                          style={{
                            fontSize: typography.sizes.sm,
                            color: colors.text.primary,
                            marginLeft: spacing.scale.xs,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          {option.duration} seconds
                        </span>
                      </div>
                    )}
                    
                    {option.target_audience && (
                      <div>
                        <span 
                          style={{
                            fontSize: typography.sizes.xs,
                            fontWeight: typography.weights.medium,
                            color: colors.text.muted,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          Audience:
                        </span>
                        <span 
                          style={{
                            fontSize: typography.sizes.sm,
                            color: colors.text.primary,
                            marginLeft: spacing.scale.xs,
                            fontFamily: typography.fontFamilies.body
                          }}
                        >
                          {option.target_audience}
                        </span>
                      </div>
                    )}
                    
                    {option.why_this_works && (
                      <div 
                        className="mt-3 p-3 rounded-lg"
                        style={{
                          backgroundColor: colors.background.section,
                          fontSize: typography.sizes.xs,
                          color: colors.text.muted,
                          fontFamily: typography.fontFamilies.body,
                          lineHeight: typography.lineHeights.relaxed
                        }}
                      >
                        <strong>Why this works:</strong> {option.why_this_works}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={handleConfirm}
          disabled={!selectedOption}
          className="w-full py-4 px-6 rounded-lg font-medium transition-all flex items-center justify-center gap-3"
          style={{
            backgroundColor: selectedOption 
              ? (layout?.navbar?.primaryCta?.background || '#6366f1')
              : colors.borders.subtle,
            color: selectedOption
              ? (layout?.navbar?.primaryCta?.textColor || '#ffffff')
              : colors.text.muted,
            fontSize: typography.sizes.md,
            fontWeight: typography.weights.semibold,
            fontFamily: typography.fontFamilies.body,
            cursor: selectedOption ? 'pointer' : 'not-allowed',
            opacity: selectedOption ? 1 : 0.6
          }}
        >
          <Check className="w-5 h-5" />
          Continue with Selected Option
        </button>
      </div>
    </div>
  )
}

export default VideoOptionsSelector






















