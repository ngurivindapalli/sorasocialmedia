import { useState, useEffect, useRef } from 'react'

// Sample topics for generating posts (used as fallback)
const SAMPLE_TOPICS = [
  'AI-powered productivity tools',
  'Sustainable fashion trends',
  'Tech startup innovation',
  'Digital marketing strategies',
  'Remote work culture',
  'E-commerce growth',
  'Social media engagement',
  'Content creation tips',
  'Business automation',
  'Creative design inspiration'
]

function FallingPostsGallery() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeImageNumbers, setActiveImageNumbers] = useState([]) // Track which image numbers (1-10) are currently visible
  const imageStartTimes = useRef(new Map()) // Track when each image number started its animation
  const slotData = useRef(new Map()) // Track position, scale, zIndex, delay for each slot (0-3)
  const isInitialLoad = useRef(true) // Track if this is the initial load
  const containerRef = useRef(null)

  // Load static posts from JSON file
  useEffect(() => {
    const loadStaticPosts = async () => {
      try {
        // Try to load from static posts file
        const response = await fetch('/static-posts/posts.json')
        if (response.ok) {
          const staticPosts = await response.json()
          
          // Transform static posts to gallery format, numbered 1-10
          const galleryPosts = staticPosts.map((post, i) => {
            const hue1 = (i * 36) % 360 // Distribute hues evenly
            const hue2 = (hue1 + 60) % 360
            // Handle image path - ensure consistent path format for both localhost and production
            let imagePath = null
            if (post.image) {
              if (post.image.startsWith('images/')) {
                // Format: "images/marketing-post-1.png" -> "/static-posts/images/marketing-post-1.png"
                imagePath = `/static-posts/${post.image}`
              } else if (post.image.startsWith('/static-posts/')) {
                // Already in correct format: "/static-posts/images/marketing-post-1.png"
                imagePath = post.image
              } else if (post.image.startsWith('/')) {
                // Other absolute paths - keep as is
                imagePath = post.image
              } else {
                // Just filename - assume it's in images folder
                imagePath = `/static-posts/images/${post.image}`
              }
            }
            return {
              id: post.id || i,
              image: imagePath,
              caption: post.caption || `Engaging content about ${post.topic}`,
              topic: post.topic,
              imageNumber: i + 1, // Number images 1-10
              gradientHue1: hue1,
              gradientHue2: hue2,
            }
          })
          
          // Initialize with 4 random images (1-10)
          const initialNumbers = []
          const availableNumbers = Array.from({ length: 10 }, (_, i) => i + 1)
          for (let i = 0; i < 4; i++) {
            const randomIndex = Math.floor(Math.random() * availableNumbers.length)
            initialNumbers.push(availableNumbers.splice(randomIndex, 1)[0])
          }
          setActiveImageNumbers(initialNumbers)
          
          // Store gallery posts for reference
          setPosts(galleryPosts)
          
          // Initialize lastImageNumber for each slot after slots are created
          setTimeout(() => {
            initialNumbers.forEach((imageNum, index) => {
              const slotInfo = slotData.current.get(index)
              if (slotInfo) {
                slotInfo.lastImageNumber = imageNum
              }
            })
          }, 200)
        } else {
          throw new Error('Static posts file not found')
        }
      } catch (error) {
        console.warn('Failed to load static posts, using fallback:', error)
        // Fall back to mock posts with gradient backgrounds
        const mockPosts = SAMPLE_TOPICS.slice(0, 10).map((topic, i) => {
          const hue1 = (i * 36) % 360
          const hue2 = (hue1 + 60) % 360
          return {
            id: i,
            image: null,
            caption: `Engaging content about ${topic}. Discover how this topic can transform your business and drive results.`,
            topic,
            imageNumber: i + 1,
            gradientHue1: hue1,
            gradientHue2: hue2,
          }
        })
        setPosts(mockPosts)
        // Initialize with 4 random numbers
        const initialNumbers = []
        const availableNumbers = Array.from({ length: 10 }, (_, i) => i + 1)
        for (let i = 0; i < 4; i++) {
          const randomIndex = Math.floor(Math.random() * availableNumbers.length)
          initialNumbers.push(availableNumbers.splice(randomIndex, 1)[0])
        }
        setActiveImageNumbers(initialNumbers)
      } finally {
        setLoading(false)
      }
    }

    loadStaticPosts()
  }, [])
  
  // Set up continuous cycling for each slot - runs once when activeImageNumbers is initialized
  useEffect(() => {
    if (posts.length === 0 || activeImageNumbers.length === 0) return
    
    const animationDuration = 20 // Match the CSS animation duration (seconds)
    const fadeStartTime = 18 // Images start fading at 90% (18s into 20s animation) - faster fade
    const imageChangeTime = 20 // Change image at 100% (20s) - AFTER image fully disappears
    const cycleTime = animationDuration * 1000 // Full cycle time in milliseconds
    
    // Set up continuous intervals for each slot (only once per slot)
    const setupSlotCycling = (index) => {
      const slotInfo = slotData.current.get(index)
      if (!slotInfo || slotInfo.intervalId) return // Already set up
      
      // Calculate when this slot's image should be replaced
      // Each slot has its own fixed delay, so we need to calculate when it should change
      const slotDelay = slotInfo.fixedDelay
      
      // Replace the image AFTER it fully disappears (at 100% / 20s)
      // Then the new image will appear at the start of the next cycle based on the slot's delay
      // Time until change = imageChangeTime + slotDelay (accounting for negative delays)
      const timeUntilChange = (imageChangeTime + slotDelay) * 1000
      
      // Function to replace image in THIS SPECIFIC SLOT ONLY
      const replaceImageInSlot = () => {
        setActiveImageNumbers((current) => {
          // Create a new array but only modify this specific slot
          const updated = [...current]
          
          // Get numbers from OTHER slots (not this one)
          const otherSlotsNumbers = current.filter((_, i) => i !== index)
          const allNumbers = Array.from({ length: 10 }, (_, i) => i + 1)
          
          // Get the last image number for this slot to prevent repeats
          const lastImage = slotInfo.lastImageNumber
          
          // Available numbers are those not in other slots AND not the last image in this slot
          let available = allNumbers.filter(num => !otherSlotsNumbers.includes(num))
          
          // Exclude the last image number to prevent consecutive repeats
          if (lastImage !== null && available.includes(lastImage)) {
            available = available.filter(num => num !== lastImage)
          }
          
          // Replace only this slot's image with a random available number
          if (available.length > 0) {
            const randomIndex = Math.floor(Math.random() * available.length)
            const newImageNumber = available[randomIndex]
            updated[index] = newImageNumber
            // Store this as the last image for this slot
            slotInfo.lastImageNumber = newImageNumber
          } else {
            // Fallback: if somehow all numbers are taken, pick any random one
            // (This shouldn't happen with 10 numbers and 4 slots, but safety check)
            const fallbackNumber = Math.floor(Math.random() * 10) + 1
            updated[index] = fallbackNumber
            slotInfo.lastImageNumber = fallbackNumber
          }
          
          return updated
        })
      }
      
      // Schedule first replacement AFTER image fully disappears
      const firstTimeout = setTimeout(() => {
        replaceImageInSlot()
        
        // Then set up continuous interval for this slot ONLY
        // Each slot cycles independently every animationDuration
        // This ensures each slot only replaces its own image at the right time
        const intervalId = setInterval(() => {
          replaceImageInSlot()
        }, cycleTime)
        
        // Store interval for cleanup
        slotInfo.intervalId = intervalId
      }, Math.max(100, timeUntilChange))
      
      slotInfo.timeoutId = firstTimeout
    }
    
    // Set up cycling for all 4 slots independently
    for (let i = 0; i < 4; i++) {
      setupSlotCycling(i)
    }
    
    // Cleanup function
    return () => {
      for (let i = 0; i < 4; i++) {
        const slotInfo = slotData.current.get(i)
        if (slotInfo) {
          if (slotInfo.timeoutId) clearTimeout(slotInfo.timeoutId)
          if (slotInfo.intervalId) clearInterval(slotInfo.intervalId)
          slotInfo.timeoutId = null
          slotInfo.intervalId = null
        }
      }
    }
  }, [posts, activeImageNumbers.length]) // Only run when posts are loaded and we have 4 images

  if (loading) {
    return (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-[#111827] text-sm">Generating posts...</div>
        </div>
      </div>
    )
  }

  return (
    <div 
      ref={containerRef}
      className="absolute inset-0"
      style={{
        perspective: '1000px',
        perspectiveOrigin: 'center center',
        background: 'transparent', // No background, let parent gradient show through
        overflow: 'visible', // Allow images to be visible even if slightly outside
        paddingLeft: '0px', // Start from left edge
        paddingRight: '0px', // No right padding, let parent handle it
        width: '100%', // Ensure full width
        right: '0', // Ensure container extends to right
      }}
    >
      {activeImageNumbers.map((imageNumber, index) => {
        // Find the post with this image number
        const post = posts.find(p => p.imageNumber === imageNumber)
        if (!post) return null
        
        const animationDuration = 20
        
        // Get or create slot data to maintain position, properties, and FIXED animation timing
        let slotInfo = slotData.current.get(index)
        if (!slotInfo) {
          // Initialize slot with stable position, properties, and FIXED delay
          const basePositions = [0, 25, 50, 65] // Base positions
          const positionVariation = (Math.random() - 0.5) * 8 // ±4% random variation
          const leftPosition = basePositions[index % basePositions.length] + positionVariation
          
          // Calculate FIXED delay for this slot - this never changes
          // Each slot has its own continuous cycle
          const initialProgress = (index / 4) * 100 // Distribute across 0-100%
          const initialDelay = -(initialProgress / 100) * animationDuration
          const staggerDelay = index * 1.5
          const randomVariation = (Math.random() - 0.5) * 0.5
          const fixedDelay = initialDelay + staggerDelay + randomVariation
          
          slotInfo = {
            leftPosition: Math.max(0, Math.min(65, leftPosition)),
            scale: 0.75 + Math.random() * 0.2,
            zTranslate: (Math.random() * 60) - 30,
            zIndex: Math.floor(Math.random() * 3) + 1,
            fixedDelay: fixedDelay, // FIXED delay - never changes for this slot
            lastImageNumber: null, // Track last image to prevent repeats
          }
          slotData.current.set(index, slotInfo)
          
          if (index === 3) {
            setTimeout(() => {
              isInitialLoad.current = false
            }, 100)
          }
        }
        
        // Use the slot's FIXED delay - this ensures seamless infinite loop
        // The delay never changes, only the image number changes
        const finalDelay = slotInfo.fixedDelay
        
        return (
        <div
          key={`slot-${index}`} // Use stable slot-based key to prevent remounting
          className="absolute"
          style={{
            left: `${slotInfo.leftPosition}%`, // Use stored position
            top: '-30%', // Start higher to match animation
            width: '300px',
            height: '300px',
            zIndex: slotInfo.zIndex, // Use stored z-index
            transform: `scale(${slotInfo.scale}) translateZ(${slotInfo.zTranslate}px)`,
            transformStyle: 'preserve-3d',
            maxWidth: 'none',
            right: 'auto',
          }}
        >
          <div
            className="falling-post w-full h-full"
            style={{
              // Use faster fade animation for first/leftmost image (index 0)
              animation: index === 0 
                ? `fall-fast-fade ${animationDuration}s linear infinite`
                : `fall ${animationDuration}s linear infinite`,
              animationDelay: `${finalDelay}s`,
              animationFillMode: 'both', // Ensure animation applies immediately
            }}
          >
          <div
            className="w-full h-full rounded-xl overflow-hidden"
            style={{
              background: post.image 
                ? 'transparent' 
                : `linear-gradient(135deg, 
                    hsl(${post.gradientHue1 || Math.random() * 360}, 70%, 50%), 
                    hsl(${post.gradientHue2 || Math.random() * 360}, 70%, 40%))`,
              border: 'none', // Remove border for cleaner look
              backdropFilter: 'blur(8px)',
              opacity: 0.95 - (index % 2) * 0.08, // Higher opacity for professional look
              boxShadow: `0 8px 32px rgba(0, 0, 0, ${0.15 + (index % 2) * 0.05}), 0 2px 8px rgba(0, 0, 0, 0.1)`, // Professional layered shadow
              transform: 'translateZ(0)', // Hardware acceleration
            }}
          >
            {post.image ? (
              <img
                src={post.image}
                alt={post.topic}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center p-4">
                <div className="text-white text-center">
                  <div className="text-sm font-semibold mb-2">{post.topic}</div>
                  <div className="text-xs opacity-75">{post.caption.substring(0, 60)}...</div>
                </div>
              </div>
            )}
            {/* Overlay with caption preview */}
            <div 
              className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent"
              style={{
                opacity: 0.7 - (post.zIndex - 1) * 0.1
              }}
            >
              <p className="text-white text-xs line-clamp-2">
                {post.caption.substring(0, 80)}...
              </p>
            </div>
          </div>
          </div>
        </div>
        )
      })}
    </div>
  )
}

export default FallingPostsGallery
