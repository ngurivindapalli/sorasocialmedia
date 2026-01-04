import { useState, useRef } from 'react'
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const ALLOWED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain'
]

const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt']
const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

function DocumentUpload({ onDocumentsChange, existingDocuments = [] }) {
  const [documents, setDocuments] = useState(existingDocuments || [])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  // Get file extension
  const getFileExtension = (filename) => {
    return filename.slice((filename.lastIndexOf('.') - 1 >>> 0) + 2)
  }

  // Validate file
  const validateFile = (file) => {
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      return { valid: false, error: `File size exceeds ${MAX_FILE_SIZE / (1024 * 1024)}MB limit` }
    }

    // Check file type
    const extension = getFileExtension(file.name).toLowerCase()
    if (!ALLOWED_EXTENSIONS.includes(`.${extension}`)) {
      return { valid: false, error: `File type not supported. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}` }
    }

    return { valid: true }
  }

  // Handle file selection
  const handleFileSelect = async (event) => {
    const files = Array.from(event.target.files || [])
    if (files.length === 0) return

    setError(null)
    setUploading(true)

    try {
      const validFiles = []
      
      // Validate all files first
      for (const file of files) {
        const validation = validateFile(file)
        if (!validation.valid) {
          setError(validation.error)
          setUploading(false)
          return
        }
        validFiles.push(file)
      }

      // Upload each file
      const uploadPromises = validFiles.map(async (file) => {
        const formData = new FormData()
        formData.append('file', file)

        const response = await axios.post(`${API_URL}/api/documents/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 60000 // 60 second timeout for large files
        })

        return {
          id: response.data.document_id,
          filename: file.name,
          size: file.size,
          uploadedAt: new Date().toISOString()
        }
      })

      const uploadedDocs = await Promise.all(uploadPromises)
      const newDocuments = [...documents, ...uploadedDocs]
      
      setDocuments(newDocuments)
      onDocumentsChange?.(newDocuments)
      
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (err) {
      console.error('[DocumentUpload] Upload error:', err)
      setError(
        err.response?.data?.detail || 
        err.message || 
        'Failed to upload document. Please try again.'
      )
    } finally {
      setUploading(false)
    }
  }

  // Remove document
  const handleRemoveDocument = async (documentId) => {
    try {
      await axios.delete(`${API_URL}/api/documents/${documentId}`)
      const newDocuments = documents.filter(doc => doc.id !== documentId)
      setDocuments(newDocuments)
      onDocumentsChange?.(newDocuments)
    } catch (err) {
      console.error('[DocumentUpload] Remove error:', err)
      setError('Failed to remove document. Please try again.')
    }
  }

  // Format file size
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  return (
    <div className="w-full">
      {/* Upload Area */}
      <div
        className="border-2 border-dashed rounded-lg p-6 text-center transition-all cursor-pointer hover:border-blue-400 hover:bg-blue-50/50"
        style={{
          borderColor: uploading ? '#93c5fd' : '#d1d5db',
          backgroundColor: uploading ? '#eff6ff' : 'transparent'
        }}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.doc,.docx,.txt"
          onChange={handleFileSelect}
          className="hidden"
          disabled={uploading}
        />
        
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
            <p className="text-sm text-gray-600">Uploading...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="w-8 h-8 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-700">
                Click to upload documents
              </p>
              <p className="text-xs text-gray-500 mt-1">
                PDF, DOC, DOCX, TXT (max {MAX_FILE_SIZE / (1024 * 1024)}MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mt-3 flex items-center gap-2 text-red-600 text-sm">
          <AlertCircle className="w-4 h-4" />
          <span>{error}</span>
        </div>
      )}

      {/* Uploaded Documents List */}
      {documents.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-sm font-medium text-gray-700 mb-2">
            Uploaded Documents ({documents.length})
          </p>
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <FileText className="w-5 h-5 text-blue-500 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {doc.filename}
                  </p>
                  <p className="text-xs text-gray-500">
                    {formatFileSize(doc.size)}
                  </p>
                </div>
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
              </div>
              <button
                onClick={() => handleRemoveDocument(doc.id)}
                className="ml-3 p-1 hover:bg-red-100 rounded transition-colors"
                title="Remove document"
              >
                <X className="w-4 h-4 text-red-500" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DocumentUpload


























