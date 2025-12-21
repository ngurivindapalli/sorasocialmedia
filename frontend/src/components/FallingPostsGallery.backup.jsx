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
  const containerRef = useRef(null)

  // Load static posts from JSON file
  useEffect(() => {
    const loadStaticPosts = async () => {
      try {
        // Try to load from static posts file
        const response = await fetch('/static-posts/posts.json')
        if (response.ok) {
          const staticPosts = await response.json()
          
          // Transform static posts to gallery format
          const galleryPosts = staticPosts.map((post, i) => {
            const hue1 = (i * 36) % 360 // Distribute hues evenly
            const hue2 = (hue1 + 60) % 360
            // Handle image path - if it's a relative path, make it absolute from /static-posts/
            let imagePath = null
            if (post.image) {
              if (post.image.startsWith('images/')) {
                imagePath = `/static-posts/${post.image}`
              } else if (post.image.startsWith('/')) {
                imagePath = post.image
              } else {
                imagePath = `/static-posts/${post.image}`
              }
            }
            return {
              id: post.id || i,
              image: imagePath,
              caption: post.caption || `Engaging content about ${post.topic}`,
              topic: post.topic,
              zIndex: Math.floor(Math.random() * 5) + 1,
              left: Math.random() * 100,
              delay: Math.random() * 5,
              scale: 0.6 + Math.random() * 0.4,
              gradientHue1: hue1,
              gradientHue2: hue2,
            }
          })
          
          // Use 4 posts to fill space better - prevent overlap, more professional
          // Only use the actual posts, don't duplicate
          const spacedPosts = galleryPosts.map((post, i) => {
            // Space out horizontally - push everything LEFT to be closer to text
            // Use lower percentage values to prevent cutoff on the right
            const positions = [0, 25, 50, 65] // Max 65% to prevent cutoff with 300px images
            // Space out delays - each post starts further apart
            const baseDelay = i * 7 // 7 seconds between each post
            const randomDelay = Math.random() * 2 // Small random variation
            
            // Distribute initial positions throughout the animation cycle
            // This prevents all posts from stacking at the top on page load
            const animationDuration = 20 // Faster animation
            // Better distribution - spread posts across the full animation cycle
            const totalPosts = 4
            const initialProgress = (i / totalPosts) * 100 // Distribute across 4 posts
            const initialDelay = -(initialProgress / 100) * animationDuration // Negative delay to start at different points
            
            return {
              ...post,
              id: post.id || i,
              left: positions[i % positions.length],
              delay: initialDelay + randomDelay, // Use initial delay for distribution, add small random
              scale: 0.8 + Math.random() * 0.1, // Consistent scale (0.8-0.9) to reduce overlap
              zIndex: Math.floor(Math.random() * 2) + 1, // Even fewer depth layers
            }
          })
          
          // Show 4 posts to fill the space better, including left side
          setPosts(spacedPosts.slice(0, 4))
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
            zIndex: Math.floor(Math.random() * 5) + 1,
            left: Math.random() * 100,
            delay: Math.random() * 5,
            scale: 0.6 + Math.random() * 0.4,
            gradientHue1: hue1,
            gradientHue2: hue2,
          }
        })
        setPosts(mockPosts)
      } finally {
        setLoading(false)
      }
    }

    loadStaticPosts()
  }, [])

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
      {posts.map((post) => {
        const zTranslate = (post.zIndex - 1.5) * 40 // Less depth separation to reduce overlap
        // Faster animation - base 20 seconds (reduced from 25)
        const animationDuration = 20 + (Math.abs(post.delay) % 1.5) // Faster, smoother speed
        return (
        <div
          key={post.id}
          className="absolute"
          style={{
            left: `${post.left}%`,
            top: '-30%', // Start higher to match animation
            width: '300px', // Slightly smaller for more professional look
            height: '300px',
            zIndex: post.zIndex,
            transform: `scale(${post.scale}) translateZ(${zTranslate}px)`,
            transformStyle: 'preserve-3d',
            maxWidth: 'none', // Remove maxWidth restriction
            right: 'auto', // Ensure left positioning works
          }}
        >
          <div
            className="falling-post w-full h-full"
            style={{
              animation: `fall ${animationDuration}s linear infinite`,
              animationDelay: `${post.delay}s`,
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
              opacity: 0.95 - (post.zIndex - 1) * 0.08, // Higher opacity for professional look
              boxShadow: `0 8px 32px rgba(0, 0, 0, ${0.15 + post.zIndex * 0.05}), 0 2px 8px rgba(0, 0, 0, 0.1)`, // Professional layered shadow
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


