import { useState, useEffect } from 'react'
import { FileText, Upload, X, Search, Plus, AlertCircle, ChevronDown, ChevronUp, Link2, CheckCircle2, Loader2, BookOpen, Users, TrendingUp, BarChart3 } from 'lucide-react'
import { api } from '../utils/api'
import { authUtils } from '../utils/auth'

function BrandContext() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeSummaryTab, setActiveSummaryTab] = useState('overall')
  
  // Brand context and competitors state
  const [uploadedDoc, setUploadedDoc] = useState(null)
  const [uploadedDocName, setUploadedDocName] = useState('')
  const [uploadedDocId, setUploadedDocId] = useState(null)
  const [uploadingDoc, setUploadingDoc] = useState(false)
  const [sendingDoc, setSendingDoc] = useState(false)
  const [sentDocuments, setSentDocuments] = useState([])
  const [documentsDropdownOpen, setDocumentsDropdownOpen] = useState(false)
  const [competitors, setCompetitors] = useState([])
  const [newCompetitor, setNewCompetitor] = useState('')
  const [findingCompetitors, setFindingCompetitors] = useState(false)
  const [error, setError] = useState('')
  const [foundCompetitors, setFoundCompetitors] = useState([])
  const [showFoundCompetitors, setShowFoundCompetitors] = useState(false)
  const [competitorsDropdownOpen, setCompetitorsDropdownOpen] = useState(false)
  
  // Integration state
  const [integrations, setIntegrations] = useState([])
  const [notionPages, setNotionPages] = useState([])
  const [googleDriveFiles, setGoogleDriveFiles] = useState([])
  const [selectedNotionPages, setSelectedNotionPages] = useState([])
  const [selectedDriveFiles, setSelectedDriveFiles] = useState([])
  const [importing, setImporting] = useState(false)
  const [loadingIntegrations, setLoadingIntegrations] = useState(false)
  
  // Summary data state
  const [brandContextSummary, setBrandContextSummary] = useState('')
  const [competitorContextSummary, setCompetitorContextSummary] = useState('')
  const [marketContextSummary, setMarketContextSummary] = useState('')
  const [overallSummary, setOverallSummary] = useState('')
  const [loadingSummaries, setLoadingSummaries] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState('')

  useEffect(() => {
    loadUserSettings()
    loadBrandContextAndCompetitors()
    loadIntegrations()
  }, [])

  useEffect(() => {
    if (user) {
      loadSummaries()
    }
  }, [user])

  // Automatically upload document when one is selected
  useEffect(() => {
    if (uploadedDoc && !uploadingDoc && !sendingDoc) {
      console.log('[BrandContext] Document selected, automatically starting upload...')
      handleDocumentUpload()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uploadedDoc]) // Only trigger when uploadedDoc changes (handleDocumentUpload is stable)

  const loadUserSettings = async () => {
    try {
      const userData = await authUtils.getCurrentUserFromAPI()
      if (userData) {
        setUser(userData)
      }
    } catch (err) {
      console.error('Failed to load user settings:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadBrandContextAndCompetitors = async () => {
    try {
      const savedSentDocuments = localStorage.getItem('videohook_sent_documents')
      if (savedSentDocuments) {
        setSentDocuments(JSON.parse(savedSentDocuments))
      }
      
      const savedCompetitors = localStorage.getItem('videohook_competitors')
      if (savedCompetitors) {
        setCompetitors(JSON.parse(savedCompetitors))
      }
    } catch (err) {
      console.error('Failed to load brand context and competitors:', err)
    }
  }

  const loadIntegrations = async () => {
    try {
      setLoadingIntegrations(true)
      const response = await api.get('/api/integrations')
      setIntegrations(response.data || [])
      
      for (const integration of response.data || []) {
        if (integration.platform === 'notion' && integration.is_active) {
          try {
            const pagesResponse = await api.get('/api/integrations/notion/pages')
            setNotionPages(pagesResponse.data || [])
          } catch (err) {
            console.error('Failed to load Notion pages:', err)
          }
        } else if (integration.platform === 'google_drive' && integration.is_active) {
          try {
            const filesResponse = await api.get('/api/integrations/google-drive/files')
            setGoogleDriveFiles(filesResponse.data || [])
          } catch (err) {
            console.error('Failed to load Google Drive files:', err)
          }
        }
      }
    } catch (err) {
      console.error('Failed to load integrations:', err)
    } finally {
      setLoadingIntegrations(false)
    }
  }

  const loadSummaries = async () => {
    try {
      setLoadingSummaries(true)
      const user_id = user?.email?.toLowerCase().trim() || ''
      
      if (!user_id) {
        setLoadingSummaries(false)
        return
      }

      // Use the new summaries endpoint that uses get_all_memories_context + GPT (same as marketing posts)
      try {
        const summariesResponse = await api.post('/api/hyperspell/summaries')
        console.log('[BrandContext] Summaries response:', summariesResponse.data)
        
        // Set all summaries from the response
        if (summariesResponse.data?.overall_summary) {
          setOverallSummary(summariesResponse.data.overall_summary)
        }
        if (summariesResponse.data?.brand_context) {
          setBrandContextSummary(summariesResponse.data.brand_context)
        }
        if (summariesResponse.data?.competitor_context) {
          setCompetitorContextSummary(summariesResponse.data.competitor_context)
        }
        if (summariesResponse.data?.market_context) {
          setMarketContextSummary(summariesResponse.data.market_context)
        }
        
        setLoadingSummaries(false)
      } catch (err) {
        console.error('Failed to load summaries:', err)
        setLoadingSummaries(false)
      }
    } catch (err) {
      console.error('Failed to load summaries:', err)
      setLoadingSummaries(false)
    }
  }
  
  // OLD CODE - keeping commented for reference
  /*
  const loadSummaries_OLD = async () => {
    try {
      const brandResponse = await api.post('/api/hyperspell/query', {
          query: 'brand guidelines, company information, business context, products, services, company values, brand identity',
          max_results: 10
        })
        console.log('[BrandContext] Brand response:', brandResponse.data)
        
        let content = ''
        // Prioritize answer field - it contains the actual summarized content from Hyperspell
        if (brandResponse.data?.answer && String(brandResponse.data.answer).trim().length > 20) {
          content = String(brandResponse.data.answer).trim()
          console.log('[BrandContext] Using answer field for brand context:', content.substring(0, 100))
        } else {
          // Try both documents and results fields
          const docs = brandResponse.data?.documents || brandResponse.data?.results || []
          if (docs && docs.length > 0) {
            console.log('[BrandContext] Found documents:', docs.length, 'First doc structure:', docs[0])
            // Extract content from documents - handle both objects and dicts
            const docContents = docs.map((doc, idx) => {
              if (typeof doc === 'string') {
                // Skip if it looks like just an ID (short alphanumeric)
                if (doc.length < 30 && /^[a-zA-Z0-9_-]+$/.test(doc)) {
                  return null
                }
                return doc.trim()
              }
              if (typeof doc === 'object' && doc !== null) {
                // Skip if this looks like just an ID
                const docId = doc.id || doc.resource_id || doc.memory_id || String(doc)
                if (docId && docId.length < 30 && /^[a-zA-Z0-9_-]+$/.test(String(docId)) && 
                    !doc._extracted_text && !doc.content && !doc.text && !doc.snippet) {
                  return null
                }
                
                // First check for pre-extracted text from backend
                if (doc._extracted_text && typeof doc._extracted_text === 'string' && doc._extracted_text.trim().length > 10) {
                  return doc._extracted_text.trim()
                }
                
                // Try various field names
                let text = doc.content || doc.text || doc.snippet || doc.document || doc.memory || 
                           doc.body || doc.data || doc.page_content || doc.pageContent ||
                           doc.value || doc.message || doc.description
                
                // If still no text, try accessing nested properties
                if (!text && doc.metadata) {
                  text = doc.metadata.content || doc.metadata.text || doc.metadata.snippet
                }
                
                // If we found text, return it
                if (text && typeof text === 'string' && text.trim().length > 10) {
                  return text.trim()
                }
                
                // Last resort: try to extract any string values from the object
                if (!text) {
                  for (const key in doc) {
                    if (key !== '_extracted_text' && key !== 'id' && key !== 'resource_id' && key !== 'memory_id' &&
                        typeof doc[key] === 'string' && doc[key].trim().length > 10) {
                      text = doc[key]
                      break
                    }
                  }
                }
                
                if (text && typeof text === 'string' && text.trim().length > 10) {
                  return text.trim()
                }
              }
              return null
            }).filter(Boolean)
            content = docContents.join('\n\n')
            console.log('[BrandContext] Extracted content length:', content.length, 'Preview:', content.substring(0, 100))
          }
        }
        
        if (content) {
          setBrandContextSummary(content.substring(0, 500) + (content.length > 500 ? '...' : ''))
        }
      } catch (err) {
        console.error('Failed to load brand context summary:', err)
      }

      // Competitor context summary
      try {
        const competitorResponse = await api.post('/api/hyperspell/query', {
          query: 'competitors, competitive analysis, competitor information',
          max_results: 10
        })
        console.log('[BrandContext] Competitor response:', competitorResponse.data)
        
        let content = ''
        if (competitorResponse.data?.answer && String(competitorResponse.data.answer).trim().length > 20) {
          content = String(competitorResponse.data.answer).trim()
          console.log('[BrandContext] Using answer field for competitor context')
        } else {
          const docs = competitorResponse.data?.documents || competitorResponse.data?.results || []
          if (docs && docs.length > 0) {
            const docContents = docs.map((doc, idx) => {
              if (typeof doc === 'string') {
                // Skip if it looks like just an ID (short alphanumeric)
                if (doc.length < 30 && /^[a-zA-Z0-9_-]+$/.test(doc)) {
                  return null
                }
                return doc.trim()
              }
              if (typeof doc === 'object' && doc !== null) {
                // Skip if this looks like just an ID
                const docId = doc.id || doc.resource_id || doc.memory_id || String(doc)
                if (docId && docId.length < 30 && /^[a-zA-Z0-9_-]+$/.test(String(docId)) && 
                    !doc._extracted_text && !doc.content && !doc.text && !doc.snippet) {
                  return null
                }
                
                // First check for pre-extracted text from backend
                if (doc._extracted_text && typeof doc._extracted_text === 'string' && doc._extracted_text.trim().length > 10) {
                  return doc._extracted_text.trim()
                }
                
                let text = doc.content || doc.text || doc.snippet || doc.document || doc.memory || 
                           doc.body || doc.data || doc.page_content || doc.pageContent ||
                           doc.value || doc.message || doc.description
                if (!text && doc.metadata) {
                  text = doc.metadata.content || doc.metadata.text || doc.metadata.snippet
                }
                if (!text) {
                  for (const key in doc) {
                    if (key !== '_extracted_text' && typeof doc[key] === 'string' && doc[key].trim().length > 10) {
                      text = doc[key]
                      break
                    }
                  }
                }
                if (text && typeof text === 'string') {
                  return text.trim()
                }
              }
              return null
            }).filter(Boolean)
            content = docContents.join('\n\n')
          }
        }
        
        if (content) {
          setCompetitorContextSummary(content.substring(0, 500) + (content.length > 500 ? '...' : ''))
        }
      } catch (err) {
        console.error('Failed to load competitor context summary:', err)
      }

      // Market context summary
      try {
        const marketResponse = await api.post('/api/hyperspell/query', {
          query: 'market trends, industry analysis, market research, target audience',
          max_results: 10
        })
        console.log('[BrandContext] Market response:', marketResponse.data)
        
        let content = ''
        if (marketResponse.data?.answer && String(marketResponse.data.answer).trim().length > 20) {
          content = String(marketResponse.data.answer).trim()
          console.log('[BrandContext] Using answer field for market context')
        } else {
          const docs = marketResponse.data?.documents || marketResponse.data?.results || []
          if (docs && docs.length > 0) {
            const docContents = docs.map((doc, idx) => {
              if (typeof doc === 'string') {
                // Skip if it looks like just an ID (short alphanumeric)
                if (doc.length < 30 && /^[a-zA-Z0-9_-]+$/.test(doc)) {
                  return null
                }
                return doc.trim()
              }
              if (typeof doc === 'object' && doc !== null) {
                // Skip if this looks like just an ID
                const docId = doc.id || doc.resource_id || doc.memory_id || String(doc)
                if (docId && docId.length < 30 && /^[a-zA-Z0-9_-]+$/.test(String(docId)) && 
                    !doc._extracted_text && !doc.content && !doc.text && !doc.snippet) {
                  return null
                }
                
                // First check for pre-extracted text from backend
                if (doc._extracted_text && typeof doc._extracted_text === 'string' && doc._extracted_text.trim().length > 10) {
                  return doc._extracted_text.trim()
                }
                
                let text = doc.content || doc.text || doc.snippet || doc.document || doc.memory || 
                           doc.body || doc.data || doc.page_content || doc.pageContent ||
                           doc.value || doc.message || doc.description
                if (!text && doc.metadata) {
                  text = doc.metadata.content || doc.metadata.text || doc.metadata.snippet
                }
                if (!text) {
                  for (const key in doc) {
                    if (key !== '_extracted_text' && typeof doc[key] === 'string' && doc[key].trim().length > 10) {
                      text = doc[key]
                      break
                    }
                  }
                }
                if (text && typeof text === 'string') {
                  return text.trim()
                }
              }
              return null
            }).filter(Boolean)
            content = docContents.join('\n\n')
          }
        }
        
        if (content) {
          setMarketContextSummary(content.substring(0, 500) + (content.length > 500 ? '...' : ''))
        }
      } catch (err) {
        console.error('Failed to load market context summary:', err)
      }

      // Overall summary - use get_all_memories_context endpoint if available, otherwise query with *
      try {
        const overallResponse = await api.post('/api/hyperspell/query', {
          query: 'brand context, competitors, market trends, company information, business context',
          max_results: 20
        })
        console.log('[BrandContext] Overall response:', overallResponse.data)
        
        let content = ''
        if (overallResponse.data?.answer && String(overallResponse.data.answer).trim().length > 20) {
          content = String(overallResponse.data.answer).trim()
          console.log('[BrandContext] Using answer field for overall summary')
        } else {
          const docs = overallResponse.data?.documents || overallResponse.data?.results || []
          if (docs && docs.length > 0) {
            const docContents = docs.map((doc, idx) => {
              if (typeof doc === 'string') {
                // Skip if it looks like just an ID (short alphanumeric)
                if (doc.length < 30 && /^[a-zA-Z0-9_-]+$/.test(doc)) {
                  return null
                }
                return doc.trim()
              }
              if (typeof doc === 'object' && doc !== null) {
                // Skip if this looks like just an ID
                const docId = doc.id || doc.resource_id || doc.memory_id || String(doc)
                if (docId && docId.length < 30 && /^[a-zA-Z0-9_-]+$/.test(String(docId)) && 
                    !doc._extracted_text && !doc.content && !doc.text && !doc.snippet) {
                  return null
                }
                
                // First check for pre-extracted text from backend
                if (doc._extracted_text && typeof doc._extracted_text === 'string' && doc._extracted_text.trim().length > 10) {
                  return doc._extracted_text.trim()
                }
                
                let text = doc.content || doc.text || doc.snippet || doc.document || doc.memory || 
                           doc.body || doc.data || doc.page_content || doc.pageContent ||
                           doc.value || doc.message || doc.description
                if (!text && doc.metadata) {
                  text = doc.metadata.content || doc.metadata.text || doc.metadata.snippet
                }
                if (!text) {
                  for (const key in doc) {
                    if (key !== '_extracted_text' && typeof doc[key] === 'string' && doc[key].trim().length > 10) {
                      text = doc[key]
                      break
                    }
                  }
                }
                if (text && typeof text === 'string') {
                  return text.trim()
                }
              }
              return null
            }).filter(Boolean)
            content = docContents.join('\n\n')
          }
        }
        
        if (content) {
          setOverallSummary(content.substring(0, 800) + (content.length > 800 ? '...' : ''))
        }
      } catch (err) {
        console.error('Failed to load overall summary:', err)
      }
    } catch (err) {
      console.error('Failed to load summaries:', err)
    } finally {
      setLoadingSummaries(false)
    }
  }
  */

  // All the handler functions from Settings (handleDocumentUpload, handleSendDocument, etc.)
  // ... (I'll include the key ones, but you may want to copy all handlers from Settings.jsx)
  
  const handleDocumentSelect = (e) => {
    const file = e.target.files[0]
    if (!file) return

    const allowedTypes = ['application/pdf', 'application/msword', 
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    if (!allowedTypes.includes(file.type)) {
      setError('File type not supported. Please upload PDF, DOC, DOCX, or TXT files.')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('File size exceeds 10MB limit.')
      return
    }

    // Just set the file - don't upload yet
    setUploadedDoc(file)
    setUploadedDocName(file.name)
    setError('')
  }

  const handleDocumentUpload = async () => {
    if (!uploadedDoc) return

    const file = uploadedDoc // Use the uploadedDoc state
    try {
      setUploadingDoc(true)
      setError('')
      setUploadSuccess('') // Clear any previous success message
      
      // Step 1: Upload to local document storage
      const fileBuffer = await file.arrayBuffer()
      const fileBlob = new Blob([fileBuffer], { type: file.type })
      const fileForDocument = new File([fileBlob], file.name, { type: file.type })
      
      const formData = new FormData()
      formData.append('file', fileForDocument)

      const uploadResponse = await api.post('/api/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (!uploadResponse.data?.document_id) {
        throw new Error('Failed to upload document to local storage')
      }

      const documentId = uploadResponse.data.document_id
      setUploadedDocId(documentId)
      console.log('[BrandContext] Document uploaded locally:', documentId)
      
      // Step 2: Immediately save to Hyperspell (user's specific memory account)
      setSendingDoc(true)
      try {
        const fileForHyperspell = new File([fileBlob], file.name, { type: file.type })
        const hyperspellFormData = new FormData()
        hyperspellFormData.append('file', fileForHyperspell)
        
        const hyperspellResponse = await api.post('/api/hyperspell/upload', hyperspellFormData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        
        // Verify response has resource_id and verified flag
        if (!hyperspellResponse.data?.resource_id) {
          throw new Error('Failed to save document to Hyperspell: No resource_id returned')
        }
        
        const verified = hyperspellResponse.data?.verified !== false // Default to true if not specified
        const resourceId = hyperspellResponse.data.resource_id
        
        if (!verified) {
          console.warn('[BrandContext] Document saved but verification incomplete. Resource ID:', resourceId)
        }
        
        console.log('[BrandContext] Document saved to Hyperspell:', resourceId, verified ? '(verified)' : '(verification pending)')
        
        // Save filename before clearing state
        const fileName = uploadedDocName || file.name
        
        // Step 3: Save to sent documents list
        const newDoc = {
          id: documentId,
          name: file.name,
          sentAt: new Date().toISOString(),
          resourceId: resourceId
        }
        const updated = [...sentDocuments, newDoc]
        setSentDocuments(updated)
        localStorage.setItem('videohook_sent_documents', JSON.stringify(updated))
        
        // Step 4: Now remove the document from upload state (after successful save)
        setUploadedDoc(null)
        setUploadedDocName('')
        setUploadedDocId(null)
        
        // Show success notification with verification status (do this before setTimeout)
        const successMessage = verified 
          ? `Document "${fileName}" uploaded successfully and verified in unified brand context!`
          : `Document "${fileName}" uploaded (verification pending)`
        setUploadSuccess(successMessage)
        console.log('[BrandContext] Success message set:', successMessage)
        
        // Clear success message after 5 seconds
        setTimeout(() => {
          setUploadSuccess('')
        }, 5000)
        
        // Reload summaries after adding document (wait a moment for Hyperspell to process)
        setTimeout(async () => {
          await loadSummaries()
        }, 2000)
        
        console.log('[BrandContext] Document successfully saved to unified brand context and removed from upload state')
      } catch (hyperspellErr) {
        console.error('Failed to save document to Hyperspell:', hyperspellErr)
        // Keep the document in state so user can retry
        setUploadedDoc(file)
        setUploadedDocName(file.name)
        setUploadedDocId(documentId)
        const errorMsg = hyperspellErr.response?.data?.detail || hyperspellErr.message || 'Failed to save document to Hyperspell. The document is still available - please try uploading again.'
        setError(errorMsg)
        setUploadSuccess('') // Clear any success message
        throw hyperspellErr
      } finally {
        setSendingDoc(false)
      }
    } catch (err) {
      console.error('Failed to upload document:', err)
      const errorMsg = err.response?.data?.detail || err.message || 'Failed to upload document. Please try again.'
      setError(errorMsg)
      setUploadSuccess('') // Clear any success message on error
    } finally {
      setUploadingDoc(false)
    }
  }

  const handleSendDocument = async () => {
    if (!uploadedDoc || !uploadedDocId) return

    try {
      setSendingDoc(true)
      setError('')
      
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
      
      // Verify response has resource_id
      if (!response.data?.resource_id) {
        throw new Error('Failed to save document to Hyperspell: No resource_id returned')
      }
      
      const verified = response.data?.verified !== false // Default to true if not specified
      const resourceId = response.data.resource_id
      
      if (!verified) {
        console.warn('[BrandContext] Document saved but verification incomplete. Resource ID:', resourceId)
      }
      
      const newDoc = {
        id: uploadedDocId,
        name: uploadedDocName,
        sentAt: new Date().toISOString(),
        resourceId: resourceId
      }
      const updated = [...sentDocuments, newDoc]
      setSentDocuments(updated)
      localStorage.setItem('videohook_sent_documents', JSON.stringify(updated))
      
      setUploadedDoc(null)
      setUploadedDocName('')
      setUploadedDocId(null)
      
      // Reload summaries after adding document (wait a moment for Hyperspell to process)
      setTimeout(async () => {
        await loadSummaries()
      }, 2000)
      
      // Show success notification
      const successMessage = verified 
        ? `Document "${uploadedDocName}" saved and verified in Hyperspell!`
        : `Document "${uploadedDocName}" saved (verification pending)`
      setUploadSuccess(successMessage)
      setTimeout(() => setUploadSuccess(''), 5000)
    } catch (err) {
      console.error('Failed to send document:', err)
      setError(err.response?.data?.detail || 'Failed to send document to Hyperspell')
    } finally {
      setSendingDoc(false)
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
      
      await saveCompetitorsToHyperspell(updated)
      // Reload summaries after adding competitor (wait a moment for Hyperspell to process)
      setTimeout(async () => {
        await loadSummaries()
      }, 2000)
    }
  }

  const saveCompetitorsToHyperspell = async (competitorsList) => {
    if (competitorsList.length === 0) return
    
    try {
      const competitorsText = competitorsList.map(c => `- ${c}`).join('\n')
      const memoryText = `Competitors:\n${competitorsText}`
      
      await api.post('/api/hyperspell/add-memory', {
        text: memoryText,
        collection: 'competitors'
      })
    } catch (err) {
      console.error('Failed to save competitors to Hyperspell:', err)
    }
  }

  const handleFindCompetitors = async () => {
    if (sentDocuments.length === 0) {
      setError('Please upload and send a brand context document first to find competitors.')
      return
    }

    try {
      setFindingCompetitors(true)
      setError('')
      
      const mostRecentDoc = sentDocuments[sentDocuments.length - 1]
      const response = await api.post('/api/competitors/find', {
        document_id: mostRecentDoc.id
      })
      
      if (response.data?.competitors && response.data.competitors.length > 0) {
        setFoundCompetitors(response.data.competitors)
        setShowFoundCompetitors(true)
        setError('')
        
        // Automatically save found competitors to Hyperspell
        const competitorNames = response.data.competitors.map(c => c.name || c).filter(Boolean)
        if (competitorNames.length > 0) {
          const competitorsText = competitorNames.map(c => `- ${c}`).join('\n')
          const memoryText = `Competitors found via AI analysis:\n${competitorsText}`
          
          try {
            await api.post('/api/hyperspell/add-memory', {
              text: memoryText,
              collection: 'competitors'
            })
            console.log('[BrandContext] Saved found competitors to Hyperspell')
          } catch (err) {
            console.error('Failed to save found competitors to Hyperspell:', err)
          }
        }
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

  const handleConnectIntegration = async (platform) => {
    try {
      const response = await api.get(`/api/integrations/${platform}/authorize`)
      if (response.data?.auth_url) {
        window.location.href = response.data.auth_url
      } else if (response.data?.success || response.data?.connected) {
        await loadIntegrations()
        await loadSummaries()
        setError('')
      }
    } catch (err) {
      console.error(`Failed to connect ${platform}:`, err)
      setError(err.response?.data?.detail || `Failed to connect ${platform}`)
    }
  }

  const handleDisconnectIntegration = async (integrationId) => {
    try {
      await api.delete(`/api/integrations/${integrationId}`)
      await loadIntegrations()
      await loadSummaries()
      setNotionPages([])
      setGoogleDriveFiles([])
      setSelectedNotionPages([])
      setSelectedDriveFiles([])
    } catch (err) {
      console.error('Failed to disconnect integration:', err)
      setError('Failed to disconnect integration')
    }
  }

  const handleImportContent = async (platform, integrationId) => {
    try {
      setImporting(true)
      setError('')
      
      const itemIds = platform === 'notion' ? selectedNotionPages : selectedDriveFiles
      if (itemIds.length === 0) {
        setError('Please select at least one item to import')
        return
      }
      
      const response = await api.post('/api/integrations/import', {
        integration_id: integrationId,
        item_ids: itemIds,
        collection: 'documents'
      })
      
      if (response.data?.success) {
        if (platform === 'notion') {
          setSelectedNotionPages([])
        } else {
          setSelectedDriveFiles([])
        }
        alert(`Successfully imported ${response.data.imported?.length || 0} item(s)`)
        await loadSummaries()
      } else {
        setError('Failed to import some items')
      }
    } catch (err) {
      console.error('Failed to import content:', err)
      setError(err.response?.data?.detail || 'Failed to import content')
    } finally {
      setImporting(false)
    }
  }

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">Loading brand context...</div>
      </div>
    )
  }

  const summaryTabs = [
    { id: 'overall', label: 'Overall Summary', icon: BarChart3 },
    { id: 'brand', label: 'Brand Context', icon: BookOpen },
    { id: 'competitor', label: 'Competitor Context', icon: Users },
    { id: 'market', label: 'Market Context', icon: TrendingUp },
  ]

  return (
    <div className="p-6 max-w-6xl mx-auto bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-[#111827] mb-2 flex items-center gap-3">
          <FileText className="w-8 h-8 text-[#1e293b]" />
          Brand Context
        </h1>
        <p className="text-[#4b5563]">Manage your brand context, competitors, and integrations</p>
      </div>

      {/* Summary Tabs */}
      <div className="mb-8 bg-white rounded-lg border border-[#e5e7eb] p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-[#111827]">Context Summary</h2>
          <button
            onClick={loadSummaries}
            disabled={loadingSummaries}
            className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center gap-2 text-sm font-medium"
          >
            {loadingSummaries ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Updating...</span>
              </>
            ) : (
              <>
                <BarChart3 className="w-4 h-4" />
                <span>Update Summaries</span>
              </>
            )}
          </button>
        </div>
        
        {/* Tab Navigation */}
        <div className="flex space-x-1 border-b border-[#e5e7eb] mb-4">
          {summaryTabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSummaryTab(tab.id)}
                className={`px-4 py-2 flex items-center gap-2 text-sm font-medium transition-colors border-b-2 ${
                  activeSummaryTab === tab.id
                    ? 'border-[#1e293b] text-[#1e293b]'
                    : 'border-transparent text-[#4b5563] hover:text-[#111827]'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            )
          })}
        </div>

        {/* Tab Content */}
        <div className="min-h-[200px]">
          {loadingSummaries ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-[#1e293b]" />
              <span className="ml-2 text-[#4b5563]">Loading summary...</span>
            </div>
          ) : (
            <>
              {activeSummaryTab === 'overall' && (
                <div>
                  <p className="text-[#111827] whitespace-pre-wrap">
                    {overallSummary || 'No overall context available. Add documents, competitors, or connect integrations to build your context.'}
                  </p>
                </div>
              )}
              {activeSummaryTab === 'brand' && (
                <div>
                  <p className="text-[#111827] whitespace-pre-wrap">
                    {brandContextSummary || 'No brand context available. Upload brand documents or connect Notion/Google Drive to add context.'}
                  </p>
                </div>
              )}
              {activeSummaryTab === 'competitor' && (
                <div>
                  <p className="text-[#111827] whitespace-pre-wrap">
                    {competitorContextSummary || 'No competitor context available. Add competitors or upload competitor analysis documents.'}
                  </p>
                </div>
              )}
              {activeSummaryTab === 'market' && (
                <div>
                  <p className="text-[#111827] whitespace-pre-wrap">
                    {marketContextSummary || 'No market context available. Add market research documents or connect integrations.'}
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Success Message */}
      {uploadSuccess && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2">
          <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-green-700 flex-1">{uploadSuccess}</p>
          <button
            onClick={() => setUploadSuccess('')}
            className="ml-auto text-green-600 hover:text-green-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

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

      <div className="space-y-8">
        {/* Brand Context Document Upload */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-6">Brand Context Document</h2>
          
          {uploadedDoc ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-[#f5f5f5] border border-[#e5e7eb] rounded-lg">
                <div className="flex items-center gap-2">
                  <FileText className="w-5 h-5 text-[#1e293b]" />
                  <span className="text-sm text-[#111827] font-medium">{uploadedDocName}</span>
                  {sendingDoc && (
                    <span className="text-xs text-[#6b7280] ml-2">Saving to Hyperspell...</span>
                  )}
                </div>
                <button
                  onClick={() => {
                    setUploadedDoc(null)
                    setUploadedDocName('')
                    setUploadedDocId(null)
                  }}
                  className="text-[#4b5563] hover:text-[#111827] transition-colors"
                  disabled={sendingDoc}
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              {sendingDoc && (
                <div className="flex items-center justify-center gap-2 text-sm text-[#4b5563]">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Automatically saving to Hyperspell...</span>
                </div>
              )}
            </div>
          ) : (
            <div className="border-2 border-dashed border-[#e5e7eb] rounded-lg p-6 text-center hover:border-[#1e293b] transition-colors">
              <input
                type="file"
                id="brand-context-upload"
                onChange={handleDocumentSelect}
                accept=".pdf,.doc,.docx,.txt"
                className="hidden"
                disabled={uploadingDoc || sendingDoc}
              />
              <label htmlFor="brand-context-upload" className="cursor-pointer">
                <div className="flex flex-col items-center gap-2">
                  <Upload className="w-8 h-8 text-[#4b5563]" />
                  <div>
                    <span className="text-sm text-[#111827] font-medium">Click to select file</span>
                    <p className="text-xs text-[#4b5563] mt-1">
                      PDF, DOC, DOCX, or TXT (max 10MB)
                    </p>
                  </div>
                </div>
              </label>
            </div>
          )}
        </div>

        {/* Competitors Section */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-6">Competitors</h2>
          
          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={newCompetitor}
                onChange={(e) => setNewCompetitor(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddCompetitor()}
                placeholder="Enter competitor name or handle"
                className="flex-1 px-3 py-2 border border-[#e5e7eb] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#1e293b] focus:border-transparent"
              />
              <button
                onClick={() => handleAddCompetitor()}
                className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-colors flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </div>

            {competitors.length > 0 && (
              <div className="space-y-2">
                {competitors.map((competitor, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-[#f9fafb] border border-[#e5e7eb] rounded-lg"
                  >
                    <span className="text-sm text-[#111827]">{competitor}</span>
                    <button
                      onClick={() => {
                        const updated = competitors.filter(c => c !== competitor)
                        setCompetitors(updated)
                        localStorage.setItem('videohook_competitors', JSON.stringify(updated))
                        saveCompetitorsToHyperspell(updated)
                        loadSummaries()
                      }}
                      className="text-[#4b5563] hover:text-[#dc2626] transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

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

            {showFoundCompetitors && foundCompetitors.length > 0 && (
              <div className="mt-4 p-4 bg-[#f0f9ff] border border-[#1e293b] rounded-lg">
                <h3 className="text-sm font-semibold text-[#111827] mb-3">Found Competitors:</h3>
                <div className="space-y-2">
                  {foundCompetitors.map((competitor, idx) => {
                    const competitorName = competitor.name || competitor
                    const competitorReason = competitor.reason || ''
                    const isAlreadyAdded = competitors.includes(competitorName)
                    
                    return (
                      <div
                        key={idx}
                        className="flex items-start justify-between p-3 bg-white border border-[#e5e7eb] rounded-lg"
                      >
                        <div className="flex-1">
                          <div className="font-medium text-sm text-[#111827]">{competitorName}</div>
                          {competitorReason && (
                            <div className="text-xs text-[#4b5563] mt-1">{competitorReason}</div>
                          )}
                        </div>
                        {!isAlreadyAdded ? (
                          <button
                            onClick={() => handleAddCompetitor(competitorName)}
                            className="ml-3 px-3 py-1 bg-[#1e293b] hover:bg-[#334155] text-white text-xs rounded transition-colors"
                          >
                            Add
                          </button>
                        ) : (
                          <span className="ml-3 px-3 py-1 bg-gray-200 text-gray-600 text-xs rounded">
                            Added
                          </span>
                        )}
                      </div>
                    )
                  })}
                </div>
                <button
                  onClick={() => {
                    setShowFoundCompetitors(false)
                    setFoundCompetitors([])
                  }}
                  className="mt-3 text-sm text-[#4b5563] hover:text-[#111827]"
                >
                  Dismiss
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Integrations Section */}
        <div className="bg-white rounded-lg border border-[#e5e7eb] p-6">
          <h2 className="text-xl font-semibold text-[#111827] mb-6 flex items-center gap-2">
            <Link2 className="w-5 h-5 text-[#1e293b]" />
            Integrations
          </h2>
          <p className="text-sm text-[#4b5563] mb-6">
            Connect Notion or Google Drive to import your brand context and documents automatically
          </p>

          <div className="space-y-4">
            {/* Notion Integration */}
            <div className="border border-[#e5e7eb] rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-[#111827]">Notion</h3>
                  <p className="text-sm text-[#4b5563] mt-1">
                    Import pages from your Notion workspace as brand context
                  </p>
                </div>
                {integrations.find(i => i.platform === 'notion' && i.is_active) ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">Connected</span>
                  </div>
                ) : (
                  <button
                    onClick={() => handleConnectIntegration('notion')}
                    className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-colors text-sm font-medium"
                  >
                    Connect Notion
                  </button>
                )}
              </div>

              {integrations.find(i => i.platform === 'notion' && i.is_active) && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[#4b5563]">
                      {notionPages.length} page{notionPages.length !== 1 ? 's' : ''} available
                    </span>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={async () => {
                          try {
                            setLoadingIntegrations(true)
                            const pagesResponse = await api.get('/api/integrations/notion/pages')
                            setNotionPages(pagesResponse.data || [])
                            if (pagesResponse.data && pagesResponse.data.length === 0) {
                              setError('No Notion pages found. Make sure you have pages in your Notion workspace that the integration can access.')
                            } else {
                              setError('')
                            }
                          } catch (err) {
                            console.error('Failed to load Notion pages:', err)
                            setError(err.response?.data?.detail || 'Failed to load Notion pages. Please try again.')
                          } finally {
                            setLoadingIntegrations(false)
                          }
                        }}
                        disabled={loadingIntegrations}
                        className="text-sm text-[#1e293b] hover:text-[#334155] font-medium disabled:text-gray-400 disabled:cursor-not-allowed flex items-center gap-1"
                      >
                        {loadingIntegrations ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            Loading...
                          </>
                        ) : (
                          <>
                            <Search className="w-3 h-3" />
                            Refresh Pages
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleDisconnectIntegration(integrations.find(i => i.platform === 'notion')?.id)}
                        className="text-sm text-red-600 hover:text-red-800"
                      >
                        Disconnect
                      </button>
                    </div>
                  </div>

                  {notionPages.length > 0 ? (
                    <div className="max-h-48 overflow-y-auto border border-[#e5e7eb] rounded-lg">
                      {notionPages.map((page) => (
                        <label
                          key={page.id}
                          className="flex items-center gap-2 p-2 hover:bg-[#f9fafb] cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedNotionPages.includes(page.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedNotionPages([...selectedNotionPages, page.id])
                              } else {
                                setSelectedNotionPages(selectedNotionPages.filter(id => id !== page.id))
                              }
                            }}
                            className="rounded border-[#e5e7eb]"
                          />
                          <span className="text-sm text-[#111827] flex-1">{page.title}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 bg-[#f9fafb] border border-[#e5e7eb] rounded-lg text-center">
                      <p className="text-sm text-[#4b5563] mb-2">No pages found</p>
                      <p className="text-xs text-[#6b7280]">
                        Click "Refresh Pages" to load pages from your Notion workspace, or make sure the integration has access to your pages.
                      </p>
                    </div>
                  )}

                  {selectedNotionPages.length > 0 && (
                    <button
                      onClick={() => handleImportContent('notion', integrations.find(i => i.platform === 'notion')?.id)}
                      disabled={importing}
                      className="w-full px-4 py-2 bg-[#1e293b] hover:bg-[#334155] disabled:bg-gray-300 text-white rounded-lg transition-colors text-sm font-medium flex items-center justify-center gap-2"
                    >
                      {importing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Importing...</span>
                        </>
                      ) : (
                        <span>Import Selected ({selectedNotionPages.length})</span>
                      )}
                    </button>
                  )}
                </div>
              )}
            </div>

            {/* Google Drive Integration */}
            <div className="border border-[#e5e7eb] rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-[#111827]">Google Drive</h3>
                  <p className="text-sm text-[#4b5563] mt-1">
                    Import documents from your Google Drive as brand context
                  </p>
                </div>
                {integrations.find(i => i.platform === 'google_drive' && i.is_active) ? (
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span className="text-sm text-green-600 font-medium">Connected</span>
                  </div>
                ) : (
                  <button
                    onClick={() => handleConnectIntegration('google_drive')}
                    className="px-4 py-2 bg-[#1e293b] hover:bg-[#334155] text-white rounded-lg transition-colors text-sm font-medium"
                  >
                    Connect Google Drive
                  </button>
                )}
              </div>

              {integrations.find(i => i.platform === 'google_drive' && i.is_active) && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-[#4b5563]">
                      {googleDriveFiles.length} file{googleDriveFiles.length !== 1 ? 's' : ''} available
                    </span>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={async () => {
                          try {
                            setLoadingIntegrations(true)
                            const filesResponse = await api.get('/api/integrations/google-drive/files')
                            setGoogleDriveFiles(filesResponse.data || [])
                            if (filesResponse.data && filesResponse.data.length === 0) {
                              setError('No Google Drive files found. Make sure you have files in your Google Drive that the integration can access.')
                            } else {
                              setError('')
                            }
                          } catch (err) {
                            console.error('Failed to load Google Drive files:', err)
                            setError(err.response?.data?.detail || 'Failed to load Google Drive files. Please try again.')
                          } finally {
                            setLoadingIntegrations(false)
                          }
                        }}
                        disabled={loadingIntegrations}
                        className="text-sm text-[#1e293b] hover:text-[#334155] font-medium disabled:text-gray-400 disabled:cursor-not-allowed flex items-center gap-1"
                      >
                        {loadingIntegrations ? (
                          <>
                            <Loader2 className="w-3 h-3 animate-spin" />
                            Loading...
                          </>
                        ) : (
                          <>
                            <Search className="w-3 h-3" />
                            Refresh Files
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleDisconnectIntegration(integrations.find(i => i.platform === 'google_drive')?.id)}
                        className="text-sm text-red-600 hover:text-red-800"
                      >
                        Disconnect
                      </button>
                    </div>
                  </div>

                  {googleDriveFiles.length > 0 ? (
                    <div className="max-h-48 overflow-y-auto border border-[#e5e7eb] rounded-lg">
                      {googleDriveFiles.map((file) => (
                        <label
                          key={file.id}
                          className="flex items-center gap-2 p-2 hover:bg-[#f9fafb] cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedDriveFiles.includes(file.id)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedDriveFiles([...selectedDriveFiles, file.id])
                              } else {
                                setSelectedDriveFiles(selectedDriveFiles.filter(id => id !== file.id))
                              }
                            }}
                            className="rounded border-[#e5e7eb]"
                          />
                          <FileText className="w-4 h-4 text-[#1e293b]" />
                          <span className="text-sm text-[#111827] flex-1">{file.name}</span>
                          <span className="text-xs text-[#9ca3af]">{file.mime_type}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 bg-[#f9fafb] border border-[#e5e7eb] rounded-lg text-center">
                      <p className="text-sm text-[#4b5563] mb-2">No files found</p>
                      <p className="text-xs text-[#6b7280]">
                        Click "Refresh Files" to load files from your Google Drive, or make sure the integration has access to your files.
                      </p>
                    </div>
                  )}

                  {selectedDriveFiles.length > 0 && (
                    <button
                      onClick={() => handleImportContent('google_drive', integrations.find(i => i.platform === 'google_drive')?.id)}
                      disabled={importing}
                      className="w-full px-4 py-2 bg-[#1e293b] hover:bg-[#334155] disabled:bg-gray-300 text-white rounded-lg transition-colors text-sm font-medium flex items-center justify-center gap-2"
                    >
                      {importing ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span>Importing...</span>
                        </>
                      ) : (
                        <span>Import Selected ({selectedDriveFiles.length})</span>
                      )}
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BrandContext

