import { useState, useEffect } from 'react'
import { Settings, Save, Check } from 'lucide-react'
import axios from 'axios'
import design from '../../design.json'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function UserPreferences() {
  const [preferences, setPreferences] = useState({
    brand_voice: '',
    content_style: '',
    target_audience: '',
    preferred_video_length: '',
    video_model_preference: 'sora-2',
    platform_preferences: {
      linkedin: true,
      instagram: false,
      tiktok: false,
      twitter: false
    },
    content_themes: [],
    brand_colors: [],
    tone_preferences: []
  })
  
  const [newTheme, setNewTheme] = useState('')
  const [newColor, setNewColor] = useState('')
  const [newTone, setNewTone] = useState('')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  
  const { colors, typography, spacing, layout } = design

  // Load existing preferences
  useEffect(() => {
    loadPreferences()
  }, [])

  const loadPreferences = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/user/preferred-settings`)
      if (response.data) {
        setPreferences(prev => ({
          ...prev,
          ...response.data,
          preferred_video_length: response.data.preferred_duration || '',
          video_model_preference: response.data.preferred_video_model || 'sora-2'
        }))
      }
    } catch (error) {
      console.log('[UserPreferences] No existing preferences found')
    }
  }

  const handleSave = async () => {
    setLoading(true)
    setSaved(false)
    
    try {
      await axios.post(`${API_URL}/api/user/preferences`, preferences)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('[UserPreferences] Error saving preferences:', error)
    } finally {
      setLoading(false)
    }
  }

  const addTheme = () => {
    if (newTheme.trim()) {
      setPreferences(prev => ({
        ...prev,
        content_themes: [...prev.content_themes, newTheme.trim()]
      }))
      setNewTheme('')
    }
  }

  const removeTheme = (index) => {
    setPreferences(prev => ({
      ...prev,
      content_themes: prev.content_themes.filter((_, i) => i !== index)
    }))
  }

  const addColor = () => {
    if (newColor.trim()) {
      setPreferences(prev => ({
        ...prev,
        brand_colors: [...prev.brand_colors, newColor.trim()]
      }))
      setNewColor('')
    }
  }

  const removeColor = (index) => {
    setPreferences(prev => ({
      ...prev,
      brand_colors: prev.brand_colors.filter((_, i) => i !== index)
    }))
  }

  const addTone = () => {
    if (newTone.trim()) {
      setPreferences(prev => ({
        ...prev,
        tone_preferences: [...prev.tone_preferences, newTone.trim()]
      }))
      setNewTone('')
    }
  }

  const removeTone = (index) => {
    setPreferences(prev => ({
      ...prev,
      tone_preferences: prev.tone_preferences.filter((_, i) => i !== index)
    }))
  }

  return (
    <div 
      className="rounded-2xl"
      style={{
        backgroundColor: colors.background.card,
        border: `1px solid ${colors.borders.subtle}`,
        borderRadius: '24px',
        padding: spacing.scale['3xl'],
        boxShadow: '0 18px 40px rgba(15,23,42,0.06)'
      }}
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Settings className="w-6 h-6" style={{ color: colors.text.primary }} />
          <h2 style={{ 
            fontSize: typography.sizes.sectionTitle, 
            fontWeight: typography.weights.semibold,
            color: colors.text.primary,
            fontFamily: typography.fontFamilies.heading
          }}>
            User Preferences & Brand Context
          </h2>
        </div>
        <button
          onClick={handleSave}
          disabled={loading}
          className="flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all"
          style={{
            backgroundColor: saved ? '#10b981' : (layout?.navbar?.primaryCta?.background || '#6366f1'),
            color: layout?.navbar?.primaryCta?.textColor || '#ffffff',
            fontSize: typography.sizes.md,
            fontWeight: typography.weights.semibold,
            fontFamily: typography.fontFamilies.body,
            opacity: loading ? 0.6 : 1
          }}
        >
          {saved ? (
            <>
              <Check className="w-5 h-5" />
              Saved!
            </>
          ) : (
            <>
              <Save className="w-5 h-5" />
              Save Preferences
            </>
          )}
        </button>
      </div>

      <p style={{ 
        fontSize: typography.sizes.sm, 
        color: colors.text.muted,
        marginBottom: spacing.scale['2xl'],
        fontFamily: typography.fontFamilies.body
      }}>
        Set your preferences to help AI generate more personalized scripts and videos that match your brand voice and style.
      </p>

      <div className="space-y-6">
        {/* Brand Voice */}
        <div>
          <label style={{ 
            display: 'block',
            fontSize: typography.sizes.sm, 
            fontWeight: typography.weights.medium,
            color: colors.text.primary,
            marginBottom: spacing.scale.sm,
            fontFamily: typography.fontFamilies.body
          }}>
            Brand Voice
          </label>
          <textarea
            value={preferences.brand_voice}
            onChange={(e) => setPreferences(prev => ({ ...prev, brand_voice: e.target.value }))}
            placeholder="e.g., Professional but friendly, Authoritative, Conversational, Inspirational"
            className="w-full px-4 py-3 rounded-lg focus:outline-none"
            style={{
              backgroundColor: colors.background.section,
              border: `1px solid ${colors.borders.subtle}`,
              color: colors.text.primary,
              fontSize: typography.sizes.sm,
              fontFamily: typography.fontFamilies.body,
              minHeight: '80px',
              resize: 'vertical'
            }}
          />
        </div>

        {/* Content Style */}
        <div>
          <label style={{ 
            display: 'block',
            fontSize: typography.sizes.sm, 
            fontWeight: typography.weights.medium,
            color: colors.text.primary,
            marginBottom: spacing.scale.sm,
            fontFamily: typography.fontFamilies.body
          }}>
            Content Style
          </label>
          <select
            value={preferences.content_style}
            onChange={(e) => setPreferences(prev => ({ ...prev, content_style: e.target.value }))}
            className="w-full px-4 py-3 rounded-lg focus:outline-none"
            style={{
              backgroundColor: colors.background.section,
              border: `1px solid ${colors.borders.subtle}`,
              color: colors.text.primary,
              fontSize: typography.sizes.sm,
              fontFamily: typography.fontFamilies.body
            }}
          >
            <option value="">Select content style...</option>
            <option value="educational">Educational</option>
            <option value="entertaining">Entertaining</option>
            <option value="inspirational">Inspirational</option>
            <option value="professional">Professional</option>
            <option value="conversational">Conversational</option>
            <option value="storytelling">Storytelling</option>
          </select>
        </div>

        {/* Target Audience */}
        <div>
          <label style={{ 
            display: 'block',
            fontSize: typography.sizes.sm, 
            fontWeight: typography.weights.medium,
            color: colors.text.primary,
            marginBottom: spacing.scale.sm,
            fontFamily: typography.fontFamilies.body
          }}>
            Target Audience
          </label>
          <input
            type="text"
            value={preferences.target_audience}
            onChange={(e) => setPreferences(prev => ({ ...prev, target_audience: e.target.value }))}
            placeholder="e.g., B2B SaaS founders, Marketing directors, LinkedIn professionals"
            className="w-full px-4 py-3 rounded-lg focus:outline-none"
            style={{
              backgroundColor: colors.background.section,
              border: `1px solid ${colors.borders.subtle}`,
              color: colors.text.primary,
              fontSize: typography.sizes.sm,
              fontFamily: typography.fontFamilies.body
            }}
          />
        </div>

        {/* Video Preferences */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label style={{ 
              display: 'block',
              fontSize: typography.sizes.sm, 
              fontWeight: typography.weights.medium,
              color: colors.text.primary,
              marginBottom: spacing.scale.sm,
              fontFamily: typography.fontFamilies.body
            }}>
              Preferred Video Length (seconds)
            </label>
            <input
              type="number"
              value={preferences.preferred_video_length}
              onChange={(e) => setPreferences(prev => ({ ...prev, preferred_video_length: e.target.value }))}
              placeholder="e.g., 15, 30, 60"
              className="w-full px-4 py-3 rounded-lg focus:outline-none"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                color: colors.text.primary,
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            />
          </div>

          <div>
            <label style={{ 
              display: 'block',
              fontSize: typography.sizes.sm, 
              fontWeight: typography.weights.medium,
              color: colors.text.primary,
              marginBottom: spacing.scale.sm,
              fontFamily: typography.fontFamilies.body
            }}>
              Preferred Video Model
            </label>
            <select
              value={preferences.video_model_preference}
              onChange={(e) => setPreferences(prev => ({ ...prev, video_model_preference: e.target.value }))}
              className="w-full px-4 py-3 rounded-lg focus:outline-none"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                color: colors.text.primary,
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            >
              <option value="sora-2">Sora 2 (Fast)</option>
              <option value="veo-3">Veo 3 (High Quality)</option>
            </select>
          </div>
        </div>

        {/* Content Themes */}
        <div>
          <label style={{ 
            display: 'block',
            fontSize: typography.sizes.sm, 
            fontWeight: typography.weights.medium,
            color: colors.text.primary,
            marginBottom: spacing.scale.sm,
            fontFamily: typography.fontFamilies.body
          }}>
            Content Themes
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newTheme}
              onChange={(e) => setNewTheme(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTheme()}
              placeholder="Add a content theme..."
              className="flex-1 px-4 py-2 rounded-lg focus:outline-none"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                color: colors.text.primary,
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            />
            <button
              onClick={addTheme}
              className="px-4 py-2 rounded-lg"
              style={{
                backgroundColor: layout?.navbar?.primaryCta?.background || '#6366f1',
                color: layout?.navbar?.primaryCta?.textColor || '#ffffff',
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {preferences.content_themes.map((theme, index) => (
              <span
                key={index}
                className="px-3 py-1 rounded-full flex items-center gap-2"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  fontSize: typography.sizes.xs,
                  fontFamily: typography.fontFamilies.body
                }}
              >
                {theme}
                <button
                  onClick={() => removeTheme(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Brand Colors */}
        <div>
          <label style={{ 
            display: 'block',
            fontSize: typography.sizes.sm, 
            fontWeight: typography.weights.medium,
            color: colors.text.primary,
            marginBottom: spacing.scale.sm,
            fontFamily: typography.fontFamilies.body
          }}>
            Brand Colors
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newColor}
              onChange={(e) => setNewColor(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addColor()}
              placeholder="e.g., #6366f1, Deep Blue, Warm Orange"
              className="flex-1 px-4 py-2 rounded-lg focus:outline-none"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                color: colors.text.primary,
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            />
            <button
              onClick={addColor}
              className="px-4 py-2 rounded-lg"
              style={{
                backgroundColor: layout?.navbar?.primaryCta?.background || '#6366f1',
                color: layout?.navbar?.primaryCta?.textColor || '#ffffff',
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {preferences.brand_colors.map((color, index) => (
              <span
                key={index}
                className="px-3 py-1 rounded-full flex items-center gap-2"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  fontSize: typography.sizes.xs,
                  fontFamily: typography.fontFamilies.body
                }}
              >
                {color}
                <button
                  onClick={() => removeColor(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Tone Preferences */}
        <div>
          <label style={{ 
            display: 'block',
            fontSize: typography.sizes.sm, 
            fontWeight: typography.weights.medium,
            color: colors.text.primary,
            marginBottom: spacing.scale.sm,
            fontFamily: typography.fontFamilies.body
          }}>
            Tone Preferences
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newTone}
              onChange={(e) => setNewTone(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addTone()}
              placeholder="e.g., Professional, Authentic, Engaging"
              className="flex-1 px-4 py-2 rounded-lg focus:outline-none"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                color: colors.text.primary,
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            />
            <button
              onClick={addTone}
              className="px-4 py-2 rounded-lg"
              style={{
                backgroundColor: layout?.navbar?.primaryCta?.background || '#6366f1',
                color: layout?.navbar?.primaryCta?.textColor || '#ffffff',
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body
              }}
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {preferences.tone_preferences.map((tone, index) => (
              <span
                key={index}
                className="px-3 py-1 rounded-full flex items-center gap-2"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  fontSize: typography.sizes.xs,
                  fontFamily: typography.fontFamilies.body
                }}
              >
                {tone}
                <button
                  onClick={() => removeTone(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      </div>

      {saved && (
        <div 
          className="mt-4 p-3 rounded-lg"
          style={{
            backgroundColor: '#d1fae5',
            border: '1px solid #86efac',
            color: '#166534'
          }}
        >
          <p style={{ fontSize: typography.sizes.sm }}>
            ✓ Preferences saved! These will be used to personalize future content generation.
          </p>
        </div>
      )}
    </div>
  )
}

export default UserPreferences

