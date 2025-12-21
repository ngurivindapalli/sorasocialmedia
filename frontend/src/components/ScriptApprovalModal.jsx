import { useState } from 'react'
import { Check, X, Edit2, Save } from 'lucide-react'
import design from '../../design.json'

function ScriptApprovalModal({ 
  script, 
  onApprove, 
  onReject, 
  onEdit, 
  isOpen,
  defaultVideoModel = 'sora-2'
}) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedScript, setEditedScript] = useState(script)
  const { colors, typography, spacing, layout } = design

  if (!isOpen) return null

  const handleSaveEdit = () => {
    if (onEdit) {
      onEdit(editedScript)
    }
    setIsEditing(false)
  }

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div 
        className="bg-[#111] border border-gray-800 rounded-3xl p-8 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        style={{
          boxShadow: '0 20px 60px rgba(0,0,0,0.5)'
        }}
      >
        <div className="flex items-center justify-between mb-6">
          <h2 
            style={{
              fontSize: typography.sizes.sectionTitle,
              fontWeight: typography.weights.bold,
              color: colors.text.primary,
              fontFamily: typography.fontFamilies.heading
            }}
          >
            Review Generated Script
          </h2>
          <button
            onClick={onReject}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="mb-6">
          <p 
            style={{
              fontSize: typography.sizes.sm,
              color: colors.text.muted,
              marginBottom: spacing.scale.md,
              fontFamily: typography.fontFamilies.body
            }}
          >
            Please review the generated script. You can approve it as-is, or edit it before approving.
          </p>
        </div>

        {isEditing ? (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-3">
              <label 
                style={{
                  fontSize: typography.sizes.md,
                  fontWeight: typography.weights.medium,
                  color: colors.text.primary,
                  fontFamily: typography.fontFamilies.heading
                }}
              >
                Edit Script
              </label>
              <button
                onClick={handleSaveEdit}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors"
                style={{
                  backgroundColor: layout?.navbar?.primaryCta?.background || '#6366f1',
                  color: layout?.navbar?.primaryCta?.textColor || '#ffffff'
                }}
              >
                <Save className="w-4 h-4" />
                Save Changes
              </button>
            </div>
            <textarea
              value={editedScript}
              onChange={(e) => setEditedScript(e.target.value)}
              className="w-full p-4 rounded-lg resize-none"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                color: colors.text.primary,
                fontSize: typography.sizes.sm,
                fontFamily: typography.fontFamilies.body,
                minHeight: '300px',
                lineHeight: typography.lineHeights.relaxed
              }}
              placeholder="Edit the script here..."
            />
          </div>
        ) : (
          <div 
            className="mb-6 p-4 rounded-lg"
            style={{
              backgroundColor: colors.background.section,
              border: `1px solid ${colors.borders.subtle}`,
              fontSize: typography.sizes.sm,
              color: colors.text.primary,
              lineHeight: typography.lineHeights.relaxed,
              fontFamily: typography.fontFamilies.body,
              whiteSpace: 'pre-wrap',
              minHeight: '200px',
              maxHeight: '400px',
              overflowY: 'auto'
            }}
          >
            {script}
          </div>
        )}

        <div className="flex gap-4">
          {!isEditing ? (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all flex-1"
                style={{
                  backgroundColor: colors.background.section,
                  border: `1px solid ${colors.borders.subtle}`,
                  color: colors.text.primary,
                  fontSize: typography.sizes.md,
                  fontWeight: typography.weights.medium,
                  fontFamily: typography.fontFamilies.body
                }}
              >
                <Edit2 className="w-5 h-5" />
                Edit Script
              </button>
              <button
                onClick={() => onApprove(defaultVideoModel)}
                className="flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all flex-1"
                style={{
                  backgroundColor: layout?.navbar?.primaryCta?.background || '#6366f1',
                  color: layout?.navbar?.primaryCta?.textColor || '#ffffff',
                  fontSize: typography.sizes.md,
                  fontWeight: typography.weights.semibold,
                  fontFamily: typography.fontFamilies.body
                }}
              >
                <Check className="w-5 h-5" />
                Approve & Generate Video
              </button>
            </>
          ) : (
            <button
              onClick={() => setIsEditing(false)}
              className="flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all w-full"
              style={{
                backgroundColor: colors.background.section,
                border: `1px solid ${colors.borders.subtle}`,
                color: colors.text.primary,
                fontSize: typography.sizes.md,
                fontWeight: typography.weights.medium,
                fontFamily: typography.fontFamilies.body
              }}
            >
              Cancel Edit
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ScriptApprovalModal

