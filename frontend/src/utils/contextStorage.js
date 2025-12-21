// Local context storage utilities - saves user context linked to user ID

export const contextStorage = {
  // Get current user ID from auth, or use guest session ID
  getCurrentUserId() {
    try {
      const userStr = localStorage.getItem('videohook_current_user')
      if (userStr) {
        const user = JSON.parse(userStr)
        return user.id || user.username || this.getGuestSessionId()
      }
      // Guest mode: use session-based ID (not persistent)
      return this.getGuestSessionId()
    } catch (error) {
      return this.getGuestSessionId()
    }
  },

  // Get or create guest session ID (session-only, not persistent)
  getGuestSessionId() {
    let guestId = sessionStorage.getItem('guest_session_id')
    if (!guestId) {
      // Generate a unique guest session ID
      guestId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      sessionStorage.setItem('guest_session_id', guestId)
    }
    return guestId
  },

  // Save context for current user (or guest session)
  saveContext(key, data) {
    try {
      const userId = this.getCurrentUserId()
      const isGuest = userId.startsWith('guest_')
      
      // For guests, use sessionStorage (cleared when browser closes)
      // For authenticated users, use localStorage (persistent)
      const storage = isGuest ? sessionStorage : localStorage
      const storageKey = `user_context_${userId}_${key}`
      
      const contextData = {
        userId,
        key,
        data,
        timestamp: new Date().toISOString(),
        isGuest
      }
      
      storage.setItem(storageKey, JSON.stringify(contextData))
      console.log(`[ContextStorage] Saved context for ${isGuest ? 'guest' : 'user'} ${userId}: ${key}`)
      return true
    } catch (error) {
      console.error('[ContextStorage] Error saving context:', error)
      return false
    }
  },

  // Get context for current user (or guest session)
  getContext(key) {
    try {
      const userId = this.getCurrentUserId()
      const isGuest = userId.startsWith('guest_')
      
      // Check both sessionStorage (for guests) and localStorage (for users)
      const storage = isGuest ? sessionStorage : localStorage
      const storageKey = `user_context_${userId}_${key}`
      
      const contextStr = storage.getItem(storageKey)
      if (contextStr) {
        const contextData = JSON.parse(contextStr)
        // Verify it belongs to current user/guest
        if (contextData.userId === userId) {
          return contextData.data
        }
      }
      return null
    } catch (error) {
      console.error('[ContextStorage] Error getting context:', error)
      return null
    }
  },

  // Get all contexts for current user (or guest session)
  getAllContexts() {
    try {
      const userId = this.getCurrentUserId()
      const isGuest = userId.startsWith('guest_')
      const storage = isGuest ? sessionStorage : localStorage
      const contexts = {}
      const prefix = `user_context_${userId}_`
      
      for (let i = 0; i < storage.length; i++) {
        const key = storage.key(i)
        if (key && key.startsWith(prefix)) {
          try {
            const contextStr = storage.getItem(key)
            const contextData = JSON.parse(contextStr)
            if (contextData.userId === userId) {
              const contextKey = key.replace(prefix, '')
              contexts[contextKey] = contextData.data
            }
          } catch (e) {
            // Skip invalid entries
          }
        }
      }
      
      return contexts
    } catch (error) {
      console.error('[ContextStorage] Error getting all contexts:', error)
      return {}
    }
  },

  // Clear context for current user (or guest session)
  clearContext(key) {
    try {
      const userId = this.getCurrentUserId()
      const isGuest = userId.startsWith('guest_')
      const storage = isGuest ? sessionStorage : localStorage
      const storageKey = `user_context_${userId}_${key}`
      storage.removeItem(storageKey)
      return true
    } catch (error) {
      console.error('[ContextStorage] Error clearing context:', error)
      return false
    }
  },

  // Clear all contexts for current user (or guest session)
  clearAllContexts() {
    try {
      const userId = this.getCurrentUserId()
      const isGuest = userId.startsWith('guest_')
      const storage = isGuest ? sessionStorage : localStorage
      const prefix = `user_context_${userId}_`
      
      const keysToRemove = []
      for (let i = 0; i < storage.length; i++) {
        const key = storage.key(i)
        if (key && key.startsWith(prefix)) {
          keysToRemove.push(key)
        }
      }
      
      keysToRemove.forEach(key => storage.removeItem(key))
      console.log(`[ContextStorage] Cleared ${keysToRemove.length} contexts for ${isGuest ? 'guest' : 'user'} ${userId}`)
      return true
    } catch (error) {
      console.error('[ContextStorage] Error clearing all contexts:', error)
      return false
    }
  }
}

