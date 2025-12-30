import { useState, useEffect, useRef } from 'react'
import { Sparkles, Loader2, Send, MessageSquare, Edit2, Check, X, ArrowRight, Image as ImageIcon } from 'lucide-react'
import { api } from '../utils/api'

function AigisMarketing() {
  const [messages, setMessages] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [welcomeMessage, setWelcomeMessage] = useState('')
  const [loadingSuggestions, setLoadingSuggestions] = useState(true)
  const [topic, setTopic] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Step-by-step state
  const [currentStep, setCurrentStep] = useState(0) // 0 = initial, 1 = brainstorm, 2 = outline, 3 = draft, 4 = review, 5 = image, 6 = post
  const [brainstormedTopics, setBrainstormedTopics] = useState([])
  const [selectedTopic, setSelectedTopic] = useState('')
  const [outline, setOutline] = useState([])
  const [draft, setDraft] = useState('')
  const [reviewedDraft, setReviewedDraft] = useState('')
  const [imagePrompt, setImagePrompt] = useState('')
  const [generatedImage, setGeneratedImage] = useState(null)
  const [excerpt, setExcerpt] = useState('')
  const [tags, setTags] = useState([])
  
  // Editing states
  const [editingOutline, setEditingOutline] = useState(false)
  const [editingDraft, setEditingDraft] = useState(false)
  const [editingReviewedDraft, setEditingReviewedDraft] = useState(false)
  
  const messagesEndRef = useRef(null)
  const contentStyle = 'thought-leadership'

  useEffect(() => {
    loadSuggestions()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, currentStep])

  const loadSuggestions = async () => {
    setLoadingSuggestions(true)
    setError(null)
    
    try {
      const response = await api.post('/api/aigis-marketing/suggestions', {
        style: contentStyle
      })

      if (response.data.success && response.data.suggestions) {
        setSuggestions(response.data.suggestions)
        const welcome = response.data.welcomeMessage || "Here are some content ideas tailored for you:"
        setWelcomeMessage(welcome)
        
        setMessages([
          {
            role: 'assistant',
            content: welcome,
            suggestions: response.data.suggestions
          }
        ])
      } else {
        setError(response.data.error || 'Failed to generate suggestions')
        setMessages([
          {
            role: 'assistant',
            content: "Welcome to Aigis Marketing! I can help you create content. However, I wasn't able to load personalized suggestions at the moment. You can still enter a topic below to get started."
          }
        ])
      }
    } catch (err) {
      console.error('Error loading suggestions:', err)
      setError(err.response?.data?.detail || 'Failed to load suggestions. Please try again.')
      setMessages([
        {
          role: 'assistant',
          content: "Welcome to Aigis Marketing! I can help you create content. You can enter a topic below to get started."
        }
      ])
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setTopic(suggestion)
    setSelectedTopic(suggestion)
    setMessages(prev => [...prev, {
      role: 'user',
      content: `I'd like to create content about: ${suggestion}`
    }])
    startBrainstorming(suggestion)
  }

  const startBrainstorming = async (topicValue = null) => {
    const topicToUse = topicValue || topic
    if (!topicToUse.trim()) {
      setError('Please enter a topic')
      return
    }

    setLoading(true)
    setError(null)
    setCurrentStep(1)
    setSelectedTopic(topicToUse)

    setMessages(prev => [...prev, {
      role: 'assistant',
      content: `Great! Let's start by brainstorming some ideas for "${topicToUse}". I'll generate several topic variations you can choose from or edit.`
    }])

    try {
      const response = await api.post('/api/aigis-marketing/brainstorm', {
        style: contentStyle,
        topic: topicToUse
      })

      if (response.data.success && response.data.topics) {
        setBrainstormedTopics(response.data.topics)
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Here are some brainstormed topic ideas. Select one or edit to customize:`,
          brainstormedTopics: response.data.topics
        }])
      } else {
        setError(response.data.error || 'Failed to brainstorm topics')
      }
    } catch (err) {
      console.error('Error brainstorming:', err)
      setError(err.response?.data?.detail || 'Failed to brainstorm topics')
    } finally {
      setLoading(false)
    }
  }

  const handleTopicSelect = (selected) => {
    setSelectedTopic(selected)
    setCurrentStep(2)
    generateOutline(selected)
  }

  const generateOutline = async (topicToUse = null) => {
    const topicValue = topicToUse || selectedTopic
    if (!topicValue.trim()) {
      setError('Please select a topic')
      return
    }

    setLoading(true)
    setError(null)

    setMessages(prev => [...prev, {
      role: 'assistant',
      content: `Now let's create an outline for "${topicValue}". I'll generate key points that you can review and edit.`
    }])

    try {
      const response = await api.post('/api/aigis-marketing/outline', {
        style: contentStyle,
        topic: topicValue
      })

      if (response.data.success && response.data.outline) {
        setOutline(response.data.outline)
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Here's the outline with key points. Review and edit as needed:`,
          outline: response.data.outline
        }])
      } else {
        setError(response.data.error || 'Failed to generate outline')
      }
    } catch (err) {
      console.error('Error generating outline:', err)
      setError(err.response?.data?.detail || 'Failed to generate outline')
    } finally {
      setLoading(false)
    }
  }

  const handleOutlineEdit = (index, newValue) => {
    const newOutline = [...outline]
    newOutline[index] = newValue
    setOutline(newOutline)
  }

  const handleOutlineAdd = () => {
    setOutline([...outline, ''])
  }

  const handleOutlineRemove = (index) => {
    setOutline(outline.filter((_, i) => i !== index))
  }

  const proceedToDraft = () => {
    setCurrentStep(3)
    generateDraft()
  }

  const generateDraft = async () => {
    setLoading(true)
    setError(null)

    setMessages(prev => [...prev, {
      role: 'assistant',
      content: `Writing the draft based on your outline. This may take a moment...`
    }])

    try {
      const response = await api.post('/api/aigis-marketing/draft', {
        style: contentStyle,
        topic: selectedTopic,
        outline: outline
      })

      if (response.data.success && response.data.draft) {
        setDraft(response.data.draft)
        setImagePrompt(response.data.imagePrompt || '')
        setExcerpt(response.data.excerpt || '')
        setTags(response.data.tags || [])
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Draft completed! Review and edit as needed:`,
          draft: response.data.draft
        }])
      } else {
        setError(response.data.error || 'Failed to generate draft')
      }
    } catch (err) {
      console.error('Error generating draft:', err)
      setError(err.response?.data?.detail || 'Failed to generate draft')
    } finally {
      setLoading(false)
    }
  }

  const proceedToReview = () => {
    setCurrentStep(4)
    setReviewedDraft(draft)
  }

  const generateImage = async () => {
    if (!imagePrompt) {
      setError('Image prompt is required')
      return
    }

    setLoading(true)
    setError(null)
    setCurrentStep(5)

    setMessages(prev => [...prev, {
      role: 'assistant',
      content: `Generating image based on: "${imagePrompt}"...`
    }])

    try {
      const response = await api.post('/api/image/generate', {
        prompt: imagePrompt,
        model: 'nanobanana',
        size: '1024x1024'
      })

      if (response.data.image_url || response.data.image_base64) {
        setGeneratedImage(response.data.image_url || `data:image/png;base64,${response.data.image_base64}`)
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Image generated successfully!`,
          image: response.data.image_url || `data:image/png;base64,${response.data.image_base64}`
        }])
      } else {
        setError(response.data.error || 'Failed to generate image')
      }
    } catch (err) {
      console.error('Error generating image:', err)
      setError(err.response?.data?.detail || 'Failed to generate image')
    } finally {
      setLoading(false)
    }
  }

  const proceedToPosting = () => {
    setCurrentStep(6)
  }

  const handlePost = async () => {
    setLoading(true)
    try {
      const response = await api.post('/api/aigis-marketing/post', {
        content: reviewedDraft || draft,
        style: contentStyle,
        topic: selectedTopic,
        platforms: ['linkedin', 'blog'],
        excerpt: excerpt,
        tags: tags,
        image_url: generatedImage
      })

      if (response.data.success) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: '✅ Content posted successfully to LinkedIn and your blog!'
        }])
      } else {
        setError(response.data.error || 'Failed to post content')
      }
    } catch (err) {
      console.error('Error posting content:', err)
      setError(err.response?.data?.detail || 'Failed to post content. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetWorkflow = () => {
    setCurrentStep(0)
    setBrainstormedTopics([])
    setSelectedTopic('')
    setOutline([])
    setDraft('')
    setReviewedDraft('')
    setImagePrompt('')
    setGeneratedImage(null)
    setExcerpt('')
    setTags([])
    setTopic('')
    setMessages([{
      role: 'assistant',
      content: welcomeMessage || "Here are some content ideas tailored for you:",
      suggestions: suggestions
    }])
  }

  return (
    <div className="min-h-screen bg-white" style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-[#111827]">Aigis Marketing</h1>
      </div>

      {/* Step Progress Indicator */}
      {currentStep > 0 && (
        <div className="mb-6 bg-[#f9fafb] border border-[#e5e7eb] rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-semibold text-[#374151]">Content Creation Workflow</h3>
            <button
              onClick={resetWorkflow}
              className="text-xs text-[#6b7280] hover:text-[#374151]"
            >
              Start Over
            </button>
          </div>
          <div className="flex items-center gap-2">
            {['Brainstorm', 'Outline', 'Draft', 'Review', 'Image', 'Post'].map((stepName, idx) => {
              const stepNum = idx + 1
              const isActive = currentStep === stepNum
              const isCompleted = currentStep > stepNum
              return (
                <div key={idx} className="flex items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-semibold text-xs ${
                      isActive
                        ? 'bg-[#1e293b] text-white'
                        : isCompleted
                        ? 'bg-green-600 text-white'
                        : 'bg-[#e5e7eb] text-[#9ca3af]'
                    }`}
                  >
                    {isCompleted ? '✓' : stepNum}
                  </div>
                  <span className={`ml-2 text-xs ${isActive ? 'font-semibold text-[#1e293b]' : 'text-[#6b7280]'}`}>
                    {stepName}
                  </span>
                  {idx < 5 && <div className={`w-4 h-1 mx-2 ${isCompleted ? 'bg-green-600' : 'bg-[#e5e7eb]'}`} />}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Chat Interface */}
      <div className="bg-white border border-[#e5e7eb] rounded-lg overflow-hidden" style={{ height: 'calc(100vh - 300px)', display: 'flex', flexDirection: 'column' }}>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {loadingSuggestions ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin text-[#1e293b] mx-auto mb-4" />
                <p className="text-[#6b7280]">Analyzing your context and generating personalized suggestions...</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      msg.role === 'user'
                        ? 'bg-[#1e293b] text-white'
                        : 'bg-[#f9fafb] border border-[#e5e7eb] text-[#111827]'
                    }`}
                  >
                    <p className="whitespace-pre-wrap text-sm leading-relaxed mb-3">{msg.content}</p>
                    
                    {/* Suggestions */}
                    {msg.suggestions && msg.suggestions.length > 0 && (
                      <div className="mt-4 space-y-2">
                        {msg.suggestions.map((suggestion, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSuggestionClick(suggestion)}
                            disabled={loading || currentStep > 0}
                            className="w-full text-left px-4 py-3 bg-white border border-[#e5e7eb] rounded-lg hover:border-[#1e293b] hover:bg-[#f9fafb] transition-all text-sm text-[#374151] disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            💡 {suggestion}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Brainstormed Topics */}
                    {msg.brainstormedTopics && (
                      <div className="mt-4 space-y-2">
                        {msg.brainstormedTopics.map((topicOption, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleTopicSelect(topicOption)}
                            disabled={loading}
                            className="w-full text-left px-4 py-3 bg-white border border-[#e5e7eb] rounded-lg hover:border-[#1e293b] hover:bg-[#f9fafb] transition-all text-sm text-[#374151] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-between"
                          >
                            <span>{topicOption}</span>
                            <ArrowRight className="w-4 h-4" />
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Outline */}
                    {msg.outline && (
                      <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-[#374151]">Key Points:</h4>
                          {!editingOutline && (
                            <button
                              onClick={() => setEditingOutline(true)}
                              className="text-xs text-[#1e293b] hover:underline flex items-center gap-1"
                            >
                              <Edit2 className="w-3 h-3" />
                              Edit
                            </button>
                          )}
                        </div>
                        {editingOutline ? (
                          <div className="space-y-2">
                            {outline.map((point, idx) => (
                              <div key={idx} className="flex gap-2">
                                <input
                                  type="text"
                                  value={point}
                                  onChange={(e) => handleOutlineEdit(idx, e.target.value)}
                                  className="flex-1 px-3 py-2 border border-[#e5e7eb] rounded text-sm"
                                />
                                <button
                                  onClick={() => handleOutlineRemove(idx)}
                                  className="px-2 text-red-600 hover:bg-red-50 rounded"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </div>
                            ))}
                            <div className="flex gap-2">
                              <button
                                onClick={handleOutlineAdd}
                                className="px-3 py-2 text-sm border border-[#e5e7eb] rounded hover:bg-[#f9fafb]"
                              >
                                + Add Point
                              </button>
                              <button
                                onClick={() => {
                                  setEditingOutline(false)
                                  setMessages(prev => {
                                    const newMsgs = [...prev]
                                    newMsgs[index].outline = outline
                                    return newMsgs
                                  })
                                }}
                                className="px-3 py-2 text-sm bg-[#1e293b] text-white rounded hover:bg-[#334155] flex items-center gap-1"
                              >
                                <Check className="w-4 h-4" />
                                Done
                              </button>
                            </div>
                          </div>
                        ) : (
                          <ul className="list-disc list-inside space-y-1 text-[#6b7280] text-sm">
                            {outline.map((point, idx) => (
                              <li key={idx}>{point}</li>
                            ))}
                          </ul>
                        )}
                        {!editingOutline && (
                          <button
                            onClick={proceedToDraft}
                            disabled={loading}
                            className="mt-4 px-4 py-2 bg-[#1e293b] text-white rounded-lg text-sm hover:bg-[#334155] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                          >
                            Proceed to Draft
                            <ArrowRight className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    )}

                    {/* Draft */}
                    {msg.draft && (
                      <div className="mt-4">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-semibold text-[#374151]">Article Draft:</h4>
                          {!editingDraft && (
                            <button
                              onClick={() => {
                                setEditingDraft(true)
                                setReviewedDraft(draft)
                              }}
                              className="text-xs text-[#1e293b] hover:underline flex items-center gap-1"
                            >
                              <Edit2 className="w-3 h-3" />
                              Edit
                            </button>
                          )}
                        </div>
                        {editingDraft ? (
                          <div>
                            <textarea
                              value={reviewedDraft}
                              onChange={(e) => setReviewedDraft(e.target.value)}
                              className="w-full px-3 py-2 border border-[#e5e7eb] rounded text-sm min-h-[300px]"
                              rows={15}
                            />
                            <button
                              onClick={() => {
                                setEditingDraft(false)
                                setDraft(reviewedDraft)
                                setMessages(prev => {
                                  const newMsgs = [...prev]
                                  newMsgs[index].draft = reviewedDraft
                                  return newMsgs
                                })
                              }}
                              className="mt-2 px-3 py-2 text-sm bg-[#1e293b] text-white rounded hover:bg-[#334155] flex items-center gap-1"
                            >
                              <Check className="w-4 h-4" />
                              Save Changes
                            </button>
                          </div>
                        ) : (
                          <div className="prose max-w-none text-[#374151] text-sm whitespace-pre-wrap max-h-96 overflow-y-auto bg-white p-4 rounded border border-[#e5e7eb]">
                            {draft}
                          </div>
                        )}
                        {!editingDraft && (
                          <button
                            onClick={proceedToReview}
                            disabled={loading}
                            className="mt-4 px-4 py-2 bg-[#1e293b] text-white rounded-lg text-sm hover:bg-[#334155] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                          >
                            Review & Finalize
                            <ArrowRight className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    )}

                    {/* Review Step */}
                    {currentStep === 4 && !msg.draft && (
                      <div className="mt-4">
                        <h4 className="font-semibold text-[#374151] mb-2">Final Review:</h4>
                        <textarea
                          value={reviewedDraft}
                          onChange={(e) => setReviewedDraft(e.target.value)}
                          className="w-full px-3 py-2 border border-[#e5e7eb] rounded text-sm min-h-[300px] mb-4"
                          rows={15}
                          placeholder="Review and edit your draft..."
                        />
                        <div className="space-y-3">
                          <div>
                            <label className="block text-sm font-medium text-[#374151] mb-1">Image Prompt:</label>
                            <input
                              type="text"
                              value={imagePrompt}
                              onChange={(e) => setImagePrompt(e.target.value)}
                              className="w-full px-3 py-2 border border-[#e5e7eb] rounded text-sm"
                              placeholder="Describe the image you want for this article..."
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-[#374151] mb-1">Excerpt (for blog preview):</label>
                            <textarea
                              value={excerpt}
                              onChange={(e) => setExcerpt(e.target.value)}
                              className="w-full px-3 py-2 border border-[#e5e7eb] rounded text-sm"
                              rows={2}
                              placeholder="Brief excerpt for blog preview..."
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-[#374151] mb-1">Tags (comma-separated):</label>
                            <input
                              type="text"
                              value={tags.join(', ')}
                              onChange={(e) => setTags(e.target.value.split(',').map(t => t.trim()).filter(t => t))}
                              className="w-full px-3 py-2 border border-[#e5e7eb] rounded text-sm"
                              placeholder="tag1, tag2, tag3..."
                            />
                          </div>
                          <button
                            onClick={generateImage}
                            disabled={loading || !imagePrompt}
                            className="px-4 py-2 bg-[#1e293b] text-white rounded-lg text-sm hover:bg-[#334155] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                          >
                            <ImageIcon className="w-4 h-4" />
                            Generate Image
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Generated Image */}
                    {msg.image && (
                      <div className="mt-4">
                        <h4 className="font-semibold text-[#374151] mb-2">Generated Image:</h4>
                        <img src={msg.image} alt="Generated content image" className="max-w-full rounded border border-[#e5e7eb]" />
                        <button
                          onClick={proceedToPosting}
                          disabled={loading}
                          className="mt-4 px-4 py-2 bg-[#1e293b] text-white rounded-lg text-sm hover:bg-[#334155] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                          Proceed to Posting
                          <ArrowRight className="w-4 h-4" />
                        </button>
                      </div>
                    )}

                    {/* Posting Step */}
                    {currentStep === 6 && (
                      <div className="mt-4">
                        <h4 className="font-semibold text-[#374151] mb-4">Ready to Post:</h4>
                        <div className="space-y-3 mb-4">
                          <p className="text-sm text-[#6b7280]"><strong>Topic:</strong> {selectedTopic}</p>
                          <p className="text-sm text-[#6b7280]"><strong>Excerpt:</strong> {excerpt || 'None'}</p>
                          <p className="text-sm text-[#6b7280]"><strong>Tags:</strong> {tags.length > 0 ? tags.join(', ') : 'None'}</p>
                          {generatedImage && (
                            <div>
                              <p className="text-sm text-[#6b7280] mb-2"><strong>Image:</strong></p>
                              <img src={generatedImage} alt="Content image" className="max-w-xs rounded border border-[#e5e7eb]" />
                            </div>
                          )}
                        </div>
                        <button
                          onClick={handlePost}
                          disabled={loading}
                          className="px-4 py-2 bg-[#1e293b] text-white rounded-lg text-sm hover:bg-[#334155] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                          <Send className="w-4 h-4" />
                          Post to LinkedIn & Blog
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-[#f9fafb] border border-[#e5e7eb] rounded-lg p-4">
                    <Loader2 className="w-5 h-5 animate-spin text-[#1e293b]" />
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-[#e5e7eb] p-4 bg-white">
          <div className="flex gap-3">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey && !loading && currentStep === 0) {
                  e.preventDefault()
                  startBrainstorming()
                }
              }}
              placeholder={currentStep === 0 ? "Enter a topic or click a suggestion above..." : "Workflow in progress..."}
              className="flex-1 px-4 py-3 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1e293b] focus:border-transparent"
              disabled={loading || loadingSuggestions || currentStep > 0}
            />
            {currentStep === 0 && (
              <button
                onClick={() => startBrainstorming()}
                disabled={loading || !topic.trim() || loadingSuggestions}
                className="px-6 py-3 bg-[#1e293b] text-white rounded-lg font-medium hover:bg-[#334155] transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Start
                  </>
                )}
              </button>
            )}
          </div>
          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AigisMarketing
