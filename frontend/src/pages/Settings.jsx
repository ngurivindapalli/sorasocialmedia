import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Mail, Upload, FileText, X, Search, Plus, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react'
import { api } from '../utils/api'
import { authUtils } from '../utils/auth'

function Settings() {
  const [user, setUser] = useState(null)
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  
  // Brand context and competitors state
  const [uploadedDoc, setUploadedDoc] = useState(null) // Document waiting to be sent
  const [uploadedDocName, setUploadedDocName] = useState('')
  const [uploadedDocId, setUploadedDocId] = useState(null)
  const [uploadingDoc, setUploadingDoc] = useState(false)
  const [sendingDoc, setSendingDoc] = useState(false)
  const [sentDocuments, setSentDocuments] = useState([]) // Documents sent to Hyperspell
  const [documentsDropdownOpen, setDocumentsDropdownOpen] = useState(false)
  const [competitors, setCompetitors] = useState([])
  const [newCompetitor, setNewCompetitor] = useState('')
  const [findingCompetitors, setFindingCompetitors] = useState(false)
  const [error, setError] = useState('')
  const [foundCompetitors, setFoundCompetitors] = useState([])
  const [showFoundCompetitors, setShowFoundCompetitors] = useState(false)
  const [competitorsDropdownOpen, setCompetitorsDropdownOpen] = useState(false)

  useEffect(() => {
    loadUserSettings()
    loadBrandContextAndCompetitors()
  }, [])

  const loadUserSettings = async () => {
    try {
      const userData = await authUtils.getCurrentUserFromAPI()
      if (userData) {
        setUser(userData)
        setEmailNotifications(userData.email_notifications_enabled)
      }
    } catch (err) {
      console.error('Failed to load user settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadBrandContextAndCompetitors = async () => {
    try {
      // Load sent documents from localStorage
      const savedSentDocuments = localStorage.getItem('videohook_sent_documents')
      if (savedSentDocuments) {
        setSentDocuments(JSON.parse(savedSentDocuments))
      }
      
      // Load competitors from localStorage
      const savedCompetitors = localStorage.getItem('videohook_competitors')
      if (savedCompetitors) {
        setCompetitors(JSON.parse(savedCompetitors))
      }
    } catch (err) {
      console.error('Failed to load brand context and competitors:', err)
    }
  }

  const handleToggleEmailNotifications = async () => {
    try {
      setSaving(true)
      const newValue = !emailNotifications
      await api.put('/api/user/email-notifications', null, {
        params: { enabled: newValue }
      })
      setEmailNotifications(newValue)
      if (user) {
        setUser({ ...user, email_notifications_enabled: newValue })
      }
    } catch (err) {
      console.error('Failed to update email notifications:', err)
      alert('Failed to update email notification settings')
    } finally {
      setSaving(false)
    }
  }

  const handleDocumentUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    if (!allowedTypes.includes(file.type)) {
      setError('File type not supported. Please upload PDF, DOC, DOCX, or TXT files.')
      return
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit.')
      return
    }

    try {
      setUploadingDoc(true)
      setError('')
      
      // Read file content once to use for both uploads
      const fileBuffer = await file.arrayBuffer()
      const fileBlob = new Blob([fileBuffer], { type: file.type })
      const fileForDocument = new File([fileBlob], file.name, { type: file.type })
      const fileForHyperspell = new File([fileBlob], file.name, { type: file.type })
      
      const formData = new FormData()
      formData.append('file', fileForDocument)

      // First upload to document service
      const response = await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data?.document_id) {
        // Store uploaded document (waiting to be sent)
        setUploadedDoc(file)
        setUploadedDocName(file.name)
        setUploadedDocId(response.data.document_id)
      }
    } catch (err) {
      console.error('Failed to upload document:', err)
      setError(err.response?.data?.detail || 'Failed to upload document. Please try again.')
    } finally {
      setUploadingDoc(false)
    }
  }

  const handleSendDocument = async () => {
    if (!uploadedDoc || !uploadedDocId) return

    try {
      setSendingDoc(true)
      setError('')
      
      // Read file content for Hyperspell upload
      const fileBuffer = await uploadedDoc.arrayBuffer()
      const fileBlob = new Blob([fileBuffer], { type: uploadedDoc.type })
      const fileForHyperspell = new File([fileBlob], uploadedDoc.name, { type: uploadedDoc.type })
      
      const hyperspellFormData = new FormData()
      hyperspellFormData.append('file', fileForHyperspell)
      
      const response = await api.post('/api/hyperspell/upload', hyperspellFormData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      if (response.data?.resource_id) {
        // Add to sent documents list
        const newSentDoc = {
          id: uploadedDocId,
          name: uploadedDocName,
          resourceId: response.data.resource_id,
          sentAt: new Date().toISOString()
        }
        
        const updatedSentDocs = [...sentDocuments, newSentDoc]
        setSentDocuments(updatedSentDocs)
        localStorage.setItem('videohook_sent_documents', JSON.stringify(updatedSentDocs))
        
        // Remove from upload area
        setUploadedDoc(null)
        setUploadedDocName('')
        setUploadedDocId(null)
        
        console.log('Document sent to Hyperspell memories')
      }
    } catch (err) {
      console.error('Failed to send document to Hyperspell:', err)
      setError(err.response?.data?.detail || 'Failed to send document to Hyperspell. Please try again.')
    } finally {
      setSendingDoc(false)
    }
  }

  const handleRemoveUploadedDocument = () => {
    setUploadedDoc(null)
    setUploadedDocName('')
    setUploadedDocId(null)
  }

  const handleRemoveSentDocument = async (docId, resourceId) => {
    try {
      // Remove from sent documents list
      const updated = sentDocuments.filter(doc => doc.id !== docId)
      setSentDocuments(updated)
      localStorage.setItem('videohook_sent_documents', JSON.stringify(updated))
      
      // TODO: If Hyperspell API supports deletion by resource_id, add it here
      // For now, we just remove from localStorage
      console.log(`Document removed (resource_id: ${resourceId})`)
    } catch (err) {
      console.error('Failed to remove document:', err)
      setError('Failed to remove document. Please try again.')
    }
  }

  const handleAddCompetitor = async (competitorName = null) => {
    const competitor = competitorName || newCompetitor.trim()
    if (!competitor) return
    
    if (!competitors.includes(competitor)) {
      const updated = [...competitors, competitor]
      setCompetitors(updated)
      localStorage.setItem('videohook_competitors', JSON.stringify(updated))
      if (!competitorName) {
        setNewCompetitor('')
      }
      
      // Save all competitors to Hyperspell as one memory (will update the memory)
      await saveCompetitorsToHyperspell(updated)
    }
  }

  const saveCompetitorsToHyperspell = async (competitorsList) => {
    if (competitorsList.length === 0) return
    
    try {
      // Create a single memory with all competitors
      const competitorsText = competitorsList.map(c => `- ${c}`).join('\n')
      const memoryText = `Competitors:\n${competitorsText}`
      
      await api.post('/api/hyperspell/add-memory', {
        text: memoryText,
        collection: 'competitors'
      })
      console.log('Competitors saved to Hyperspell memories')
    } catch (err) {
      console.error('Failed to save competitors to Hyperspell:', err)
      // Don't show error to user, just log it - competitors are still saved locally
    }
  }

  const handleAddAllFoundCompetitors = async () => {
    // Add all competitors at once
    const newCompetitors = foundCompetitors
      .map(comp => comp.name || comp)
      .filter(name => !competitors.includes(name))
    
    if (newCompetitors.length > 0) {
      const updated = [...competitors, ...newCompetitors]
      setCompetitors(updated)
      localStorage.setItem('videohook_competitors', JSON.stringify(updated))
      
      // Save all competitors to Hyperspell as one memory
      await saveCompetitorsToHyperspell(updated)
    }
    
    setShowFoundCompetitors(false)
    setFoundCompetitors([])
  }

  const handleRemoveCompetitor = async (competitor) => {
    const updated = competitors.filter(c => c !== competitor)
    setCompetitors(updated)
    localStorage.setItem('videohook_competitors', JSON.stringify(updated))
    
    // Update Hyperspell memory with remaining competitors
    await saveCompetitorsToHyperspell(updated)
  }

  const handleFindCompetitors = async () => {
    if (sentDocuments.length === 0) {
      setError('Please upload and send a brand context document first to find competitors.')
      return
    }

    try {
      setFindingCompetitors(true)
      setError('')
      
      // Use the most recently sent document for competitor finding
      const mostRecentDoc = sentDocuments[sentDocuments.length - 1]
      const response = await api.post('/api/competitors/find', {
        document_id: mostRecentDoc.id
      })
      
      if (response.data?.competitors && response.data.competitors.length > 0) {
        // Store found competitors with their details
        setFoundCompetitors(response.data.competitors)
        setShowFoundCompetitors(true)
        setError('') // Clear any previous errors
      } else {
        setError('No competitors found. Try uploading a more detailed brand context document.')
      }
    } catch (err) {
      console.error('Failed to find competitors:', err)
      setError(err.response?.data?.detail || 'Failed to find competitors. Please try again.')
    } finally {
      setFindingCompetitors(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">Loading settings...</div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-6xl mx-auto bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-[#111827] mb-2 flex items-center gap-3">
          <SettingsIcon className="w-8 h-8 text-[#1e293b]" />
          Settings
        </h1>
        <p className="text-[#4b5563]">Manage your account and preferences</p>
      </div>

      <div className="space-y-8">
        {/* Account Information */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-4">Account Information</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-[#4b5563] mb-1">Username</label>
              <p className="text-[#111827]">{user?.username}</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-[#4b5563] mb-1">Email</label>
              <p className="text-[#111827]">{user?.email}</p>
            </div>
          </div>
        </div>

        {/* Email Notifications */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-[#1e293b]" />
              <div>
                <h2 className="text-xl font-semibold text-[#111827]">Email Notifications</h2>
                <p className="text-sm text-[#4b5563] mt-1">
                  Receive email notifications when your videos are posted to social media
                </p>
              </div>
            </div>
            <button
              onClick={handleToggleEmailNotifications}
              disabled={saving}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                emailNotifications ? 'bg-[#1e293b]' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  emailNotifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Brand Context & Competitors */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-6">Brand Context & Competitors</h2>
          
          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
              <button
                onClick={() => setError('')}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="space-y-6">
            {/* Brand Context Document Upload */}
            <div>
              <label className="block text-sm font-medium text-[#111827] mb-2">
                Brand Context Document
              </label>
              <p className="text-sm text-[#4b5563] mb-3">
                Upload a document containing your brand guidelines, company info, or content style preferences (PDF, DOC, DOCX, TXT)
              </p>
              
              {uploadedDoc ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-[#1e293b]" />
                      <span className="text-sm text-[#111827] font-medium">{uploadedDocName}</span>
                    </div>
                    <button
                      onClick={handleRemoveUploadedDocument}
                      className="text-[#4b5563] hover:text-[#111827] transition-colors"
                      title="Remove"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                  <button
                    onClick={handleSendDocument}
                    disabled={sendingDoc}
                    className="w-full px-4 py-2 bg-[#1e293b] hover:bg-[#334155] disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
                  >
                    {sendingDoc ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span className="text-sm font-medium">Adding...</span>
                      </>
                    ) : (
                      <>
                        <span className="text-sm font-medium">Add to Context</span>
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="border-2 border-dashed border-[#e5e7eb] rounded-lg p-6 text-center hover:border-[#1e293b] transition-colors">
                  <input
                    type="file"
                    id="brand-context-upload"
                    onChange={handleDocumentUpload}
                    accept=".pdf,.doc,.docx,.txt"
                    className="hidden"
                    disabled={uploadingDoc}
                  />
                  <label htmlFor="brand-context-upload" className="cursor-pointer">
                    <div className="flex flex-col items-center gap-2">
                      <Upload className="w-8 h-8 text-[#4b5563]" />
                      <div>
                        <span className="text-sm text-[#111827] font-medium">Click to upload</span>
                        <p className="text-xs text-[#4b5563] mt-1">
                          PDF, DOC, DOCX, or TXT (max 10MB)
                        </p>
                      </div>
                    </div>
                  </label>
                  {uploadingDoc && (
                    <p className="text-sm text-[#4b5563] mt-2">Uploading...</p>
                  )}
                </div>
              )}
            </div>

            {/* Sent Documents Dropdown */}
            {sentDocuments.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-[#111827] mb-2">
                  Sent Documents
                </label>
                <p className="text-sm text-[#4b5563] mb-3">
                  Documents sent to Hyperspell memories
                </p>
                
                <button
                  onClick={() => setDocumentsDropdownOpen(!documentsDropdownOpen)}
                  className="w-full flex items-center justify-between p-3 bg-white border border-[#e5e7eb] rounded-lg hover:border-[#1e293b] transition-colors text-left"
                >
                  <span className="text-sm text-[#111827]">
                    {sentDocuments.length} document{sentDocuments.length !== 1 ? 's' : ''} sent
                  </span>
                  {documentsDropdownOpen ? (
                    <ChevronUp className="w-4 h-4 text-[#4b5563]" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-[#4b5563]" />
                  )}
                </button>

                {documentsDropdownOpen && (
                  <div className="mt-3 border border-[#e5e7eb] rounded-lg bg-white">
                    <div className="max-h-64 overflow-y-auto">
                      <div className="divide-y divide-[#e5e7eb]">
                        {sentDocuments.map((doc) => (
                          <div
                            key={doc.id}
                            className="flex items-center justify-between p-3 hover:bg-[#f9fafb] transition-colors"
                          >
                            <div className="flex items-center gap-2 flex-1 min-w-0">
                              <FileText className="w-4 h-4 text-[#1e293b] flex-shrink-0" />
                              <div className="flex-1 min-w-0">
                                <span className="text-sm text-[#111827] block truncate">{doc.name}</span>
                                <span className="text-xs text-[#9ca3af]">
                                  {new Date(doc.sentAt).toLocaleDateString()}
                                </span>
                              </div>
                            </div>
                            <button
                              onClick={() => handleRemoveSentDocument(doc.id, doc.resourceId)}
                              className="text-[#4b5563] hover:text-[#dc2626] transition-colors ml-2 flex-shrink-0"
                              title="Remove from Hyperspell"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Found Competitors (from AI search) */}
            {showFoundCompetitors && foundCompetitors.length > 0 && (
              <div className="mb-4 p-4 bg-[#f0f9ff] border border-[#1e293b] rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-sm font-semibold text-[#111827] mb-1">
                      Found {foundCompetitors.length} Competitor{foundCompetitors.length !== 1 ? 's' : ''}
                    </h3>
                    <p className="text-xs text-[#4b5563]">
                      Review and add competitors to your list
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setShowFoundCompetitors(false)
                      setFoundCompetitors([])
                    }}
                    className="text-[#4b5563] hover:text-[#111827]"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <div className="space-y-2 mb-3">
                  {foundCompetitors.map((comp, idx) => {
                    const name = comp.name || comp
                    const reason = comp.reason || ''
                    const alreadyAdded = competitors.includes(name)
                    return (
                      <div
                        key={idx}
                        className="p-3 bg-white border border-[#e5e7eb] rounded-lg"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm font-medium text-[#111827]">{name}</span>
                              {alreadyAdded && (
                                <span className="text-xs px-2 py-0.5 bg-green-100 text-green-700 rounded">
                                  Added
                                </span>
                              )}
                            </div>
                            {reason && (
                              <p className="text-xs text-[#4b5563]">{reason}</p>
                            )}
                          </div>
                          {!alreadyAdded && (
                            <button
                              onClick={() => {
                                handleAddCompetitor(name)
                                // Open dropdown to show the added competitor
                                setCompetitorsDropdownOpen(true)
                              }}
                              className="text-[#1e293b] hover:text-[#334155] transition-colors"
                              title="Add to competitors list"
                            >
                              <Plus className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
                <button
                  onClick={handleAddAllFoundCompetitors}
                  className="w-full px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-colors text-sm font-medium"
                >
                  Add All to List
                </button>
              </div>
            )}

            {/* Competitors Dropdown */}
            <div>
              <label className="block text-sm font-medium text-[#111827] mb-2">
                Competitors
              </label>
              <p className="text-sm text-[#4b5563] mb-3">
                Add competitors to analyze and compare against
              </p>
              
              {/* Dropdown Toggle */}
              <button
                onClick={() => setCompetitorsDropdownOpen(!competitorsDropdownOpen)}
                className="w-full flex items-center justify-between p-3 bg-white border border-[#e5e7eb] rounded-lg hover:border-[#1e293b] transition-colors text-left"
              >
                <span className="text-sm text-[#111827]">
                  {competitors.length > 0 
                    ? `${competitors.length} competitor${competitors.length !== 1 ? 's' : ''} added`
                    : 'No competitors added yet'}
                </span>
                {competitorsDropdownOpen ? (
                  <ChevronUp className="w-4 h-4 text-[#4b5563]" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-[#4b5563]" />
                )}
              </button>

              {/* Dropdown Content */}
              {competitorsDropdownOpen && (
                <div className="mt-3 border border-[#e5e7eb] rounded-lg bg-white">
                  {/* Add Competitor Input */}
                  <div className="p-3 border-b border-[#e5e7eb]">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newCompetitor}
                        onChange={(e) => setNewCompetitor(e.target.value)}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            handleAddCompetitor()
                          }
                        }}
                        placeholder="Enter competitor name or handle"
                        className="flex-1 px-3 py-2 border border-[#e5e7eb] rounded-lg focus:ring-2 focus:ring-[#1e293b] focus:border-[#1e293b] text-sm text-[#111827] placeholder-[#9ca3af]"
                      />
                      <button
                        onClick={() => handleAddCompetitor()}
                        className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-colors flex items-center gap-2"
                      >
                        <Plus className="w-4 h-4" />
                        <span className="text-sm font-medium">Add</span>
                      </button>
                    </div>
                  </div>

                  {/* Competitors List */}
                  <div className="max-h-64 overflow-y-auto">
                    {competitors.length > 0 ? (
                      <div className="divide-y divide-[#e5e7eb]">
                        {competitors.map((competitor, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-3 hover:bg-[#f9fafb] transition-colors"
                          >
                            <span className="text-sm text-[#111827]">{competitor}</span>
                            <button
                              onClick={() => handleRemoveCompetitor(competitor)}
                              className="text-[#4b5563] hover:text-[#dc2626] transition-colors"
                              title="Remove competitor"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 text-center">
                        <p className="text-sm text-[#9ca3af] italic">No competitors added yet</p>
                        <p className="text-xs text-[#9ca3af] mt-1">Add competitors above or use "Find Competitors" to discover them</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Find Competitors Button */}
            <div>
              <button
                onClick={handleFindCompetitors}
                disabled={findingCompetitors || sentDocuments.length === 0}
                className="w-full px-4 py-3 bg-[#1e293b] hover:bg-[#334155] disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Search className="w-5 h-5" />
                <span className="text-sm font-medium">
                  {findingCompetitors ? 'Finding Competitors...' : 'Find Competitors'}
                </span>
              </button>
              {sentDocuments.length === 0 && (
                <p className="text-xs text-[#9ca3af] mt-2 text-center">
                  Upload and send a brand context document to enable competitor finding
                </p>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}

export default Settings

