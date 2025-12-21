import { useState, useEffect } from 'react'
import { Send, CheckCircle2, XCircle, Loader2, Instagram, Linkedin, X as XIcon, Music } from 'lucide-react'
import { api } from '../utils/api'

const PLATFORM_ICONS = {
  instagram: Instagram,
  linkedin: Linkedin,
  x: XIcon,
  tiktok: Music,
}

function PostVideoButton({ videoUrl, caption, jobId }) {
  const [connections, setConnections] = useState([])
  const [selectedConnections, setSelectedConnections] = useState([])
  const [loading, setLoading] = useState(false)
  const [posting, setPosting] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    if (showModal) {
      loadConnections()
    }
  }, [showModal])

  const loadConnections = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/connections')
      setConnections(response.data)
    } catch (err) {
      setError('Failed to load connections')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleToggleConnection = (connectionId) => {
    setSelectedConnections(prev =>
      prev.includes(connectionId)
        ? prev.filter(id => id !== connectionId)
        : [...prev, connectionId]
    )
  }

  const handlePost = async () => {
    if (selectedConnections.length === 0) {
      setError('Please select at least one account to post to')
      return
    }

    if (!videoUrl) {
      setError('Video URL is required')
      return
    }

    try {
      setPosting(true)
      setError('')
      setResult(null)

      const response = await api.post('/api/post/video', {
        connection_ids: selectedConnections,
        video_url: videoUrl,
        caption: caption || '',
        job_id: jobId
      })

      setResult(response.data)
      
      // Close modal after 3 seconds if successful
      if (response.data.success) {
        setTimeout(() => {
          setShowModal(false)
          setSelectedConnections([])
        }, 3000)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to post video')
      console.error(err)
    } finally {
      setPosting(false)
    }
  }

  if (!videoUrl) {
    return null
  }

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Send className="w-4 h-4" />
        Post to Social Media
      </button>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Post Video to Social Media</h3>
                <button
                  onClick={() => {
                    setShowModal(false)
                    setSelectedConnections([])
                    setResult(null)
                    setError('')
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              {loading ? (
                <div className="flex items-center justify-center p-8">
                  <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                </div>
              ) : connections.length === 0 ? (
                <div className="text-center p-8">
                  <p className="text-gray-600 mb-4">No social media accounts connected</p>
                  <p className="text-sm text-gray-500">
                    Please connect your accounts in Settings first
                  </p>
                </div>
              ) : (
                <>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select accounts to post to:
                    </label>
                    <div className="space-y-2">
                      {connections.map((connection) => {
                        const Icon = PLATFORM_ICONS[connection.platform] || Send
                        const isSelected = selectedConnections.includes(connection.id)

                        return (
                          <label
                            key={connection.id}
                            className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                              isSelected
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={() => handleToggleConnection(connection.id)}
                              className="w-4 h-4 text-blue-600 rounded"
                            />
                            {connection.platform === 'x' ? (
                              <span className="w-5 h-5 flex items-center justify-center font-bold text-lg" style={{ fontFamily: 'system-ui' }}>𝕏</span>
                            ) : (
                              <Icon className="w-5 h-5" />
                            )}
                            <div className="flex-1">
                              <p className="font-medium text-gray-900 capitalize">
                                {connection.platform}
                              </p>
                              <p className="text-sm text-gray-500">@{connection.account_username}</p>
                            </div>
                          </label>
                        )
                      })}
                    </div>
                  </div>

                  {caption && (
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Caption:
                      </label>
                      <textarea
                        value={caption}
                        readOnly
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                        rows="3"
                      />
                    </div>
                  )}

                  {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                      {error}
                    </div>
                  )}

                  {result && (
                    <div className="mb-4 space-y-2">
                      {result.posts.map((post, index) => (
                        <div
                          key={index}
                          className={`p-3 rounded-lg flex items-center gap-2 ${
                            post.success
                              ? 'bg-green-50 border border-green-200'
                              : 'bg-red-50 border border-red-200'
                          }`}
                        >
                          {post.success ? (
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-600" />
                          )}
                          <div className="flex-1">
                            <p className={`text-sm font-medium ${
                              post.success ? 'text-green-800' : 'text-red-800'
                            }`}>
                              {post.platform}: {post.success ? 'Posted successfully' : post.error}
                            </p>
                            {post.post_url && (
                              <a
                                href={post.post_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:underline"
                              >
                                View post
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="flex gap-3">
                    <button
                      onClick={handlePost}
                      disabled={posting || selectedConnections.length === 0}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {posting ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Posting...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          Post Video
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => {
                        setShowModal(false)
                        setSelectedConnections([])
                        setResult(null)
                        setError('')
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default PostVideoButton
























