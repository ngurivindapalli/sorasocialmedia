import { useState } from 'react'
import { Instagram, Loader2, AlertCircle, CheckCircle2, X } from 'lucide-react'
import { api } from '../utils/api'

function InstagramManualPostButton({ videoUrl, caption, onSuccess, onError }) {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [postCaption, setPostCaption] = useState(caption || 'Check out this AI-generated video!')
  const [posting, setPosting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleOpenModal = () => {
    setIsModalOpen(true)
    setError('')
    setSuccess(false)
    setPostCaption(caption || 'Check out this AI-generated video!')
  }

  const handleCloseModal = () => {
    if (!posting) {
      setIsModalOpen(false)
      setUsername('')
      setPassword('')
      setError('')
      setSuccess(false)
    }
  }

  const handlePost = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setPosting(true)

    try {
      if (!username.trim()) {
        setError('Username is required')
        setPosting(false)
        return
      }

      if (!password) {
        setError('Password is required')
        setPosting(false)
        return
      }

      console.log('[Instagram Manual Post] Starting post...')
      console.log('[Instagram Manual Post] Video URL:', videoUrl)
      console.log('[Instagram Manual Post] Username:', username)

      const response = await api.post('/api/post/instagram/manual', {
        video_url: videoUrl,
        caption: postCaption,
        username: username.trim(),
        password: password
      })

      console.log('[Instagram Manual Post] Response:', response.data)

      if (response.data.success) {
        setSuccess(true)
        if (onSuccess) {
          onSuccess(response.data)
        }
        // Close modal after 3 seconds
        setTimeout(() => {
          setIsModalOpen(false)
          setUsername('')
          setPassword('')
          setSuccess(false)
        }, 3000)
      } else {
        setError(response.data.error || response.data.message || 'Failed to post video')
        if (onError) {
          onError(response.data.error)
        }
      }
    } catch (err) {
      console.error('[Instagram Manual Post] Error:', err)
      let errorMessage = 'Failed to post video'
      
      if (err.response?.data?.error) {
        errorMessage = err.response.data.error
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
      if (onError) {
        onError(errorMessage)
      }
    } finally {
      setPosting(false)
    }
  }

  if (!isModalOpen) {
    return (
      <button
        onClick={handleOpenModal}
        className="flex-1 bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 hover:from-purple-700 hover:via-pink-700 hover:to-red-600 text-white font-semibold py-3 px-6 rounded-lg transition-all flex items-center justify-center gap-2"
        title="Post to Instagram using browser automation"
      >
        <Instagram className="w-5 h-5" />
        Post to Instagram
      </button>
    )
  }

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-center justify-center p-4"
        onClick={handleCloseModal}
      >
        {/* Modal */}
        <div 
          className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6 relative z-50"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          <button
            onClick={handleCloseModal}
            disabled={posting}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Header */}
          <div className="flex items-center gap-3 mb-6">
            <Instagram className="w-8 h-8 text-pink-600" />
            <h3 className="text-2xl font-bold text-gray-900">Post to Instagram</h3>
          </div>

          {/* Info */}
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Browser Automation:</strong> We'll open a browser window and automatically post your video to Instagram. 
              Your password is only used locally and never stored.
            </p>
          </div>

          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
              <p className="text-green-800">
                {error || 'Video posted successfully! Check your Instagram to confirm.'}
              </p>
            </div>
          )}

          {error && !success && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-red-800 font-medium">Error</p>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handlePost} className="space-y-4">
            <div>
              <label htmlFor="instagram-username" className="block text-sm font-medium text-gray-700 mb-1">
                Instagram Username
              </label>
              <input
                type="text"
                id="instagram-username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
                placeholder="your_username"
                disabled={posting || success}
                required
              />
            </div>

            <div>
              <label htmlFor="instagram-password" className="block text-sm font-medium text-gray-700 mb-1">
                Instagram Password
              </label>
              <input
                type="password"
                id="instagram-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
                placeholder="Your password (won't be stored)"
                disabled={posting || success}
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Your password is used only to log in via browser automation and is never stored.
              </p>
            </div>

            <div>
              <label htmlFor="post-caption" className="block text-sm font-medium text-gray-700 mb-1">
                Caption
              </label>
              <textarea
                id="post-caption"
                value={postCaption}
                onChange={(e) => setPostCaption(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
                placeholder="Write a caption..."
                rows={3}
                disabled={posting || success}
              />
            </div>

            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={handleCloseModal}
                disabled={posting}
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={posting || success}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {posting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Posting...
                  </>
                ) : success ? (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    Posted!
                  </>
                ) : (
                  <>
                    <Instagram className="w-5 h-5" />
                    Post Now
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  )
}

export default InstagramManualPostButton



