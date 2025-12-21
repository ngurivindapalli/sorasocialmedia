import { useState } from 'react'
import { Brain, Plus, FileText, Upload, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { api } from '../utils/api'
import { authUtils } from '../utils/auth'

function HyperspellMemories() {
  const [text, setText] = useState('')
  const [collection, setCollection] = useState('user_memories')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState(null)
  const [currentUser] = useState(authUtils.getCurrentUser())
  const [isLoggedIn] = useState(!!currentUser)

  const handleAddMemory = async (e) => {
    e.preventDefault()
    
    if (!text.trim()) {
      setError('Please enter some text to add as a memory')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(false)

    try {
      const response = await api.post('/api/hyperspell/add-memory', {
        text: text.trim(),
        collection: collection.trim() || 'user_memories'
      })

      if (response.data.success) {
        setSuccess(true)
        setText('') // Clear form
        setTimeout(() => setSuccess(false), 3000)
      }
    } catch (err) {
      console.error('Error adding memory:', err)
      
      // Extract error message properly
      let errorMessage = 'Failed to add memory'
      
      if (err.response?.data) {
        const errorData = err.response.data
        
        if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(e => e.msg || e.message || JSON.stringify(e)).join(', ')
        } else if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (errorData.detail && typeof errorData.detail === 'object') {
          errorMessage = errorData.detail.msg || errorData.detail.message || 'Validation error occurred'
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Brain className="w-8 h-8 text-indigo-600" />
            <h1 className="text-4xl font-bold text-gray-900">Hyperspell Memories</h1>
          </div>
          <p className="text-gray-600">
            Add text memories to Hyperspell. All memories are stored in your Hyperspell account.
          </p>
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <form onSubmit={handleAddMemory} className="space-y-6">
            {/* Collection Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Collection (Optional)
              </label>
              <input
                type="text"
                value={collection}
                onChange={(e) => setCollection(e.target.value)}
                placeholder="e.g., user_memories, company_info, product_details"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                disabled={loading}
              />
              <p className="mt-1 text-xs text-gray-500">
                Organize memories into collections for easier retrieval
              </p>
            </div>

            {/* Text Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Memory Text <span className="text-red-500">*</span>
              </label>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter the text you want to store as a memory. This could be company information, product details, user preferences, or any other context you want the AI to remember."
                rows={10}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                disabled={loading}
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                {text.length} characters
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading || !text.trim()}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-4 rounded-lg hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Adding Memory...
                </>
              ) : (
                <>
                  <Plus className="w-5 h-5" />
                  Add Memory to Hyperspell
                </>
              )}
            </button>
          </form>

          {/* Success Message */}
          {success && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-green-800">Memory Added Successfully!</p>
                <p className="text-sm text-green-700">
                  Your memory has been added to Hyperspell and will be available for AI queries.
                </p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-red-800">Error</p>
                <p className="text-sm text-red-600">{typeof error === 'string' ? error : JSON.stringify(error)}</p>
              </div>
            </div>
          )}

          {/* Info Box */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-3">
              <Brain className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-800">
                <p className="font-semibold mb-1">About Hyperspell Memories</p>
                <ul className="list-disc list-inside space-y-1 text-blue-700">
                  <li>All memories are stored in your Hyperspell account</li>
                  <li>Memories can be organized into collections</li>
                  <li>AI queries will search through all stored memories</li>
                  <li>Use collections to organize related memories together</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HyperspellMemories







