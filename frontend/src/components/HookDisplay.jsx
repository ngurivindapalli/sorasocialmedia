import { Sparkles, TrendingUp, Copy, Check } from 'lucide-react'
import { useState } from 'react'

function HookDisplay({ hooks }) {
  const [copiedIndex, setCopiedIndex] = useState(null)

  const copyToClipboard = async (text, index) => {
    await navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 2000)
  }

  const socialHooks = hooks.filter(h => h.type === 'social_media')
  const marketingHooks = hooks.filter(h => h.type === 'marketing')

  const HookCard = ({ hook, index, icon: Icon, color }) => (
    <div className="bg-black/30 rounded-lg p-5 border border-white/10 hover:border-white/20 transition-all">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon className={`w-5 h-5 ${color}`} />
          <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            {hook.platform}
          </span>
        </div>
        <button
          onClick={() => copyToClipboard(hook.text, index)}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          title="Copy hook"
        >
          {copiedIndex === index ? (
            <Check className="w-4 h-4 text-green-400" />
          ) : (
            <Copy className="w-4 h-4 text-gray-400" />
          )}
        </button>
      </div>
      
      <p className="text-white text-lg font-medium mb-3 leading-relaxed">
        {hook.text}
      </p>
      
      <p className="text-gray-400 text-sm">
        <span className="font-semibold text-gray-300">Why it works:</span> {hook.reasoning}
      </p>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Social Media Hooks */}
      {socialHooks.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-yellow-400" />
            <h4 className="text-xl font-bold text-white">Social Media Hooks</h4>
          </div>
          <div className="grid gap-4">
            {socialHooks.map((hook, idx) => (
              <HookCard
                key={idx}
                hook={hook}
                index={`social-${idx}`}
                icon={Sparkles}
                color="text-yellow-400"
              />
            ))}
          </div>
        </div>
      )}

      {/* Marketing Hooks */}
      {marketingHooks.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-400" />
            <h4 className="text-xl font-bold text-white">Marketing Hooks</h4>
          </div>
          <div className="grid gap-4">
            {marketingHooks.map((hook, idx) => (
              <HookCard
                key={idx}
                hook={hook}
                index={`marketing-${idx}`}
                icon={TrendingUp}
                color="text-green-400"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default HookDisplay
