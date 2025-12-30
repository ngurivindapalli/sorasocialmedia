import { useState, useEffect, useRef } from 'react'
import { Download, Loader2, AlertCircle, CheckCircle2, Video } from 'lucide-react'
import axios from 'axios'
import VideoGenerationLoader from './VideoGenerationLoader'
import InstagramManualPostButton from './InstagramManualPostButton.jsx'

// API URL - uses environment variable for production
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function SoraVideoPlayer({ videoJob, onStatusChange }) {
  const [status, setStatus] = useState(videoJob?.status || 'queued')
  const [progress, setProgress] = useState(videoJob?.progress || 0)
  const [videoUrl, setVideoUrl] = useState(null)
  const [error, setError] = useState(null)
  const pollingIntervalRef = useRef(null)

  useEffect(() => {
    if (!videoJob) return
    
    // Update status and progress from videoJob prop
    setStatus(videoJob.status || 'queued')
    setProgress(videoJob.progress || 0)
    
    // Notify parent of initial status
    if (onStatusChange) {
      onStatusChange(videoJob.status, videoJob.progress || 0, videoJob.video_url || null)
    }

    // If video is already completed, set the URL (preserve existing URL if already set)
    if (videoJob.status === 'completed') {
      // Always try to set URL from videoJob if provided, but preserve existing URL if videoUrl is already set
      if (videoJob.video_url) {
        const url = videoJob.video_url.startsWith('http') 
          ? videoJob.video_url 
          : `${API_URL}${videoJob.video_url}`
        // Only update if different to avoid unnecessary re-renders
        if (url !== videoUrl) {
          setVideoUrl(url)
        }
      }
      // Clear any existing polling
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
      return
    }

    // If video is queued or in progress, start polling (only if not already polling)
    if ((videoJob.status === 'queued' || videoJob.status === 'in_progress') && !pollingIntervalRef.current) {
      pollVideoStatus()
    }

    // Cleanup function
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
        pollingIntervalRef.current = null
      }
    }
  }, [videoJob.job_id, videoJob.status, videoJob.progress, videoJob.video_url])

  const pollVideoStatus = async () => {
    const maxAttempts = 120 // 10 minutes max (120 * 5 seconds)
    let attempts = 0
    
    // Determine which API endpoint to use based on model
    const model = videoJob.model || 'sora-2'
    const isVeo3 = model === 'veo-3' || model.startsWith('veo')
    // Veo 3 job_id contains slashes, so we need to encode it
    const encodedJobId = isVeo3 ? encodeURIComponent(videoJob.job_id) : videoJob.job_id
    const statusEndpoint = isVeo3 
      ? `${API_URL}/api/veo3/status/${encodedJobId}`
      : `${API_URL}/api/sora/status/${videoJob.job_id}`

    pollingIntervalRef.current = setInterval(async () => {
      try {
        attempts++
        
        // Recalculate endpoint in case job_id changed (for extensions)
        const currentModel = videoJob.model || 'sora-2'
        const currentIsVeo3 = currentModel === 'veo-3' || currentModel.startsWith('veo')
        const currentEncodedJobId = currentIsVeo3 ? encodeURIComponent(videoJob.job_id) : videoJob.job_id
        const currentStatusEndpoint = currentIsVeo3 
          ? `${API_URL}/api/veo3/status/${currentEncodedJobId}`
          : `${API_URL}/api/sora/status/${videoJob.job_id}`
        
        const response = await axios.get(currentStatusEndpoint)
        
        const data = response.data
        setStatus(data.status)
        setProgress(data.progress || 0)
        
        // Update extension metadata from response - CRITICAL: Always use response data
        if (data.needs_extension !== undefined) {
          videoJob.needs_extension = data.needs_extension
          console.log(`[VideoPlayer] Updated needs_extension from response: ${data.needs_extension}`)
        }
        if (data.extension_count !== undefined) {
          videoJob.extension_count = data.extension_count
          console.log(`[VideoPlayer] Updated extension_count from response: ${data.extension_count}`)
        }
        if (data.extensions_completed !== undefined) {
          videoJob.extensions_completed = data.extensions_completed
          console.log(`[VideoPlayer] Updated extensions_completed from response: ${data.extensions_completed}`)
        }
        
        // If job_id changed (extension started), update it
        if (data.job_id && data.job_id !== videoJob.job_id) {
          console.log(`[VideoPlayer] Job ID changed: ${videoJob.job_id.substring(0, 50)}... -> ${data.job_id.substring(0, 50)}...`)
          videoJob.job_id = data.job_id
        }
        
        // Force re-render if extension status changed
        if (data.needs_extension === false && videoJob.needs_extension !== false) {
          console.log(`[VideoPlayer] Extension disabled - forcing state update`)
          // Trigger a re-render by updating status
          setStatus(data.status)
        }
        
        // Notify parent of status change
        if (onStatusChange) {
          onStatusChange(data.status, data.progress || 0, data.video_url || null)
        }

        if (data.status === 'completed') {
          // Check if this is a Veo 3 video that needs extension
          const isVeo3Video = (videoJob.model === 'veo-3' || videoJob.model?.startsWith('veo'))
          
          // ALWAYS use data from response first (most up-to-date)
          const needsExtension = data.needs_extension !== undefined ? data.needs_extension : (videoJob.needs_extension && videoJob.extension_count > 0)
          const extensionCount = data.extension_count !== undefined ? data.extension_count : (videoJob.extension_count || 0)
          const extensionsCompleted = data.extensions_completed !== undefined ? data.extensions_completed : (videoJob.extensions_completed || 0)
          const isExtensionJob = data.is_extension === true
          
          console.log(`[VideoPlayer] Status: completed, isVeo3: ${isVeo3Video}`)
          console.log(`[VideoPlayer] Extension data from response: needs_extension=${data.needs_extension}, count=${data.extension_count}, completed=${data.extensions_completed}`)
          console.log(`[VideoPlayer] Extension data from videoJob: needs_extension=${videoJob.needs_extension}, count=${videoJob.extension_count}, completed=${videoJob.extensions_completed}`)
          console.log(`[VideoPlayer] Final values: needsExtension=${needsExtension}, extensionCount=${extensionCount}, extensionsCompleted=${extensionsCompleted}`)
          
          // Update videoJob with latest data from response
          if (data.needs_extension !== undefined) videoJob.needs_extension = data.needs_extension
          if (data.extension_count !== undefined) videoJob.extension_count = data.extension_count
          if (data.extensions_completed !== undefined) videoJob.extensions_completed = data.extensions_completed
          
          // If this is an extension job or we still need more extensions, continue polling
          if (isVeo3Video && needsExtension && extensionsCompleted < extensionCount) {
            // More extensions needed - update job_id and continue polling
            console.log(`[VideoPlayer] Veo 3: Extension ${extensionsCompleted}/${extensionCount} completed, continuing...`)
            // Update videoJob with new job_id for next extension
            videoJob.job_id = data.job_id
            // Update status to continue polling the new extension job
            setStatus('queued')  // Reset status to queued for the new extension job
            setProgress(0)
            // Continue polling - backend will automatically trigger next extension
            // DO NOT show video yet - wait for all extensions
            return
          }
          
          // Only show video if all extensions are complete (or no extensions needed, or extension was disabled)
          // Also check if needs_extension was set to false (extension disabled/failed)
          const extensionDisabled = data.needs_extension === false
          const allExtensionsComplete = !needsExtension || (extensionsCompleted >= extensionCount) || extensionDisabled
          
          console.log(`[VideoPlayer] All extensions complete check:`)
          console.log(`  - needsExtension: ${needsExtension}`)
          console.log(`  - extensionsCompleted: ${extensionsCompleted}`)
          console.log(`  - extensionCount: ${extensionCount}`)
          console.log(`  - extensionDisabled: ${extensionDisabled}`)
          console.log(`  - allExtensionsComplete: ${allExtensionsComplete}`)
          
          if (!allExtensionsComplete && !extensionDisabled) {
            // Still extending - continue polling without showing video
            console.log(`[VideoPlayer] Veo 3: Waiting for all extensions to complete (${extensionsCompleted}/${extensionCount})...`)
            return
          }
          
          // All extensions complete OR extension was disabled - now show the video
          if (extensionDisabled) {
            console.log(`[VideoPlayer] Veo 3: Extension disabled/failed. Showing available video.`)
          } else {
            console.log(`[VideoPlayer] Veo 3: All extensions complete! Showing final video.`)
          }
          
          // Handle video URL - could be direct URL or need to construct
          let finalUrl = videoUrl // Preserve existing URL
          if (data.video_url) {
            // If it's already a full URL, use it; otherwise prepend API_URL
            finalUrl = data.video_url.startsWith('http') 
              ? data.video_url 
              : `${API_URL}${data.video_url}`
            setVideoUrl(finalUrl) // Always set when we get a URL from polling
            console.log(`[VideoPlayer] Setting video URL: ${finalUrl}`)
          } else if (videoUrl) {
            // Use existing video URL if available
            finalUrl = videoUrl
            console.log(`[VideoPlayer] Using existing video URL: ${finalUrl}`)
          }
          
          // Notify parent of status change with video URL (only once)
          if (onStatusChange && finalUrl) {
            onStatusChange(data.status, data.progress || 100, finalUrl)
          }
          
          // Stop polling
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
          }
        } else if (data.status === 'queued' || data.status === 'in_progress') {
          // If we get a queued/in_progress status and it's an extension job, update job_id
          if (data.is_extension && data.job_id && data.job_id !== videoJob.job_id) {
            console.log(`[VideoPlayer] Veo 3: Extension job started, updating job_id from ${videoJob.job_id} to ${data.job_id}`)
            videoJob.job_id = data.job_id
            // Update extension metadata
            if (data.needs_extension !== undefined) videoJob.needs_extension = data.needs_extension
            if (data.extension_count !== undefined) videoJob.extension_count = data.extension_count
            if (data.extensions_completed !== undefined) videoJob.extensions_completed = data.extensions_completed
          }
        } else if (data.status === 'failed') {
          setError(data.error || 'Video generation failed')
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
          }
        } else if (attempts >= maxAttempts) {
          setError('Video generation timed out')
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
          }
        }
      } catch (err) {
        console.error('Polling error:', err)
        setError('Failed to check video status')
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
          pollingIntervalRef.current = null
        }
      }
    }, 5000) // Poll every 5 seconds
  }

  const handleDownload = async () => {
    try {
      const response = await axios.get(videoUrl, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `sora_video_${videoJob.job_id}.mp4`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      console.error('Download error:', err)
      alert('Failed to download video')
    }
  }

        // Show loading screen for queued or in_progress videos, or if extensions are still in progress
        const isVeo3Video = (videoJob.model === 'veo-3' || videoJob.model?.startsWith('veo'))
        const needsExtension = videoJob.needs_extension && videoJob.extension_count > 0
        const extensionsCompleted = videoJob.extensions_completed || 0
        const extensionCount = videoJob.extension_count || 0
        // Video should show if: no extension needed, all extensions done, or extension was disabled
        const extensionDisabled = videoJob.needs_extension === false
        const allExtensionsComplete = !needsExtension || (extensionsCompleted >= extensionCount) || extensionDisabled
        const stillExtending = isVeo3Video && needsExtension && !allExtensionsComplete
        
        // Debug logging
        if (isVeo3Video && status === 'completed') {
          console.log(`[VideoPlayer] Render - status: ${status}, needsExtension: ${needsExtension}, completed: ${extensionsCompleted}/${extensionCount}, extensionDisabled: ${extensionDisabled}, allComplete: ${allExtensionsComplete}, stillExtending: ${stillExtending}`)
        }
        
        // Debug logging
        if (isVeo3Video && needsExtension) {
          console.log(`[VideoPlayer] Render check - status: ${status}, needsExtension: ${needsExtension}, completed: ${extensionsCompleted}/${extensionCount}, allComplete: ${allExtensionsComplete}, stillExtending: ${stillExtending}`)
        }
        
        // CRITICAL: If we have a video URL and status is completed, NEVER show loading screen
        if (status === 'completed' && videoUrl) {
          console.log(`[VideoPlayer] Video is completed and URL available - skipping loading screen`)
          // Don't return - let it fall through to show the video
        } else if (status === 'queued' || status === 'in_progress' || stillExtending) {
          const modelName = isVeo3Video ? 'Veo 3' : 'Sora'
          let message = status === 'queued' ? 'Video queued for generation...' : `Generating video with ${modelName} AI...`
          
          if (stillExtending) {
            message = `Extending Veo 3 video... (${extensionsCompleted + 1}/${extensionCount} extensions) ${progress > 0 ? `(${progress}%)` : ''}`
          } else if (progress > 0) {
            message += ` ${progress}%`
          }
          
          return (
            <div className="mt-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Video className="w-5 h-5" />
                {modelName} Generated Video
                <span className="text-xs bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 px-3 py-1 rounded-full border border-purple-200">
                  AI Generated
                </span>
              </h4>
        <VideoGenerationLoader 
          message={message}
          inline={true}
        />
      </div>
    )
  }

  return (
    <div className="mt-6">
      <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
        <Video className="w-5 h-5" />
              {(videoJob.model === 'veo-3' || videoJob.model?.startsWith('veo')) ? 'Veo 3' : 'Sora'} Generated Video
        <span className="text-xs bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 px-3 py-1 rounded-full border border-purple-200">
          AI Generated
        </span>
      </h4>

      <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-6">

        {status === 'failed' && (
          <div className="flex items-center gap-3 text-red-600">
            <AlertCircle className="w-5 h-5" />
            <span>{error || 'Video generation failed'}</span>
          </div>
        )}

        {status === 'completed' && videoUrl && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 text-green-600 mb-4">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-semibold">Video generated successfully!</span>
            </div>

            {/* Video Player */}
            <div className="bg-black rounded-lg overflow-hidden shadow-lg">
              <video 
                controls 
                className="w-full max-h-[500px]"
                src={videoUrl}
                poster="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect fill='%23000' width='100' height='100'/%3E%3C/svg%3E"
              >
                Your browser does not support the video tag.
              </video>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleDownload}
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Download className="w-5 h-5" />
                Download Video
              </button>
              <InstagramManualPostButton
                videoUrl={videoUrl}
                caption="Check out this AI-generated video! 🎬✨"
                onSuccess={(result) => {
                  console.log('[SoraVideoPlayer] Post successful:', result)
                }}
                onError={(error) => {
                  console.error('[SoraVideoPlayer] Post error:', error)
                }}
              />
            </div>

            {/* Video Info */}
            <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 bg-white rounded-lg p-4">
              <div>
                <span className="font-semibold">Model:</span> {videoJob.model}
              </div>
              <div>
                <span className="font-semibold">Job ID:</span> {videoJob.job_id.slice(0, 20)}...
              </div>
            </div>
          </div>
        )}

        {error && status !== 'failed' && (
          <div className="flex items-center gap-3 text-red-600 mt-4">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default SoraVideoPlayer
