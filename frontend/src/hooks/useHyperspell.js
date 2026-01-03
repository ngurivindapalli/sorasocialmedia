/**
 * useMemory - React hook for integrating memory context (S3 + Mem0)
 * Replaces useHyperspell - uses MemoryService directly
 */
import { useState, useCallback } from 'react'
import { api } from '../utils/api'
import { authUtils } from '../utils/auth'

export function useHyperspell() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  /**
   * Query memory layer for relevant context
   * @param {string} query - The query to search memories
   * @returns {Promise<string>} - Context string from memory
   */
  const getContext = useCallback(async (query) => {
    if (!query || !query.trim()) {
      return ''
    }

    setLoading(true)
    setError(null)

    try {
      const response = await api.post('/api/memory/query', {
        query: query.trim(),
        max_results: 5
      })

      if (response.data && response.data.answer) {
        return response.data.answer
      } else if (response.data && response.data.results) {
        // Format results if no answer provided
        const results = Array.isArray(response.data.results) 
          ? response.data.results 
          : [response.data.results]
        
        return results
          .map((r, i) => {
            const content = r.content || r.text || r.snippet || JSON.stringify(r)
            return `${i + 1}. ${content.substring(0, 200)}...`
          })
          .join('\n')
      }

      return ''
    } catch (err) {
      console.error('[Hyperspell] Error querying memories:', err)
      setError(err.message || 'Failed to query Hyperspell memories')
      return '' // Return empty on error - don't block functionality
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Add a text memory to memory layer
   * @param {string} text - Text to store
   * @param {string} collection - Optional collection name
   * @returns {Promise<boolean>} - Success status
   */
  const addMemory = useCallback(async (text, collection = 'user_memories') => {
    if (!text || !text.trim()) {
      setError('Text is required')
      return false
    }

    setLoading(true)
    setError(null)

    try {
      const response = await api.post('/api/memory/add-memory', {
        text: text.trim(),
        collection: collection.trim() || 'user_memories'
      })

      return response.data.success === true
    } catch (err) {
      console.error('[Hyperspell] Error adding memory:', err)
      
      let errorMessage = 'Failed to add memory'
      if (err.response?.data) {
        const errorData = err.response.data
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
      }
      
      setError(errorMessage)
      return false
    } finally {
      setLoading(false)
    }
  }, [])

  /**
   * Check if memory service is available
   * @returns {Promise<boolean>}
   */
  const checkAvailability = useCallback(async () => {
    try {
      const response = await api.get('/api/memory/status')
      return response.data.available === true
    } catch (err) {
      return false
    }
  }, [])

  return {
    getContext,
    addMemory,
    checkAvailability,
    loading,
    error
  }
}














