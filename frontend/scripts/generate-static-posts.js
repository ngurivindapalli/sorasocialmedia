import axios from 'axios'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000'

// Sample topics for generating posts
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

async function generateStaticPosts() {
  const postsDir = path.join(__dirname, '../public/static-posts')
  
  // Create directory if it doesn't exist
  if (!fs.existsSync(postsDir)) {
    fs.mkdirSync(postsDir, { recursive: true })
  }

  const posts = []
  
  console.log('🎨 Generating marketing posts...\n')
  
  for (let i = 0; i < SAMPLE_TOPICS.length; i++) {
    const topic = SAMPLE_TOPICS[i]
    console.log(`Generating post ${i + 1}/${SAMPLE_TOPICS.length}: ${topic}`)
    
    try {
      const response = await axios.post(
        `${API_URL}/api/marketing-post/create`,
        {
          topic,
          caption_style: 'engaging',
          aspect_ratio: '1:1',
          include_hashtags: true,
          post_to_instagram: false
        },
        { timeout: 60000 } // 60 second timeout
      )
      
      const postData = response.data
      
      // Save image
      let imagePath = null
      if (postData.image_base64) {
        const imageBuffer = Buffer.from(postData.image_base64, 'base64')
        imagePath = `static-posts/post-${i + 1}.png`
        const fullImagePath = path.join(postsDir, `post-${i + 1}.png`)
        fs.writeFileSync(fullImagePath, imageBuffer)
        console.log(`  ✓ Image saved: ${imagePath}`)
      } else if (postData.image_url) {
        // Download image from URL
        const imageResponse = await axios.get(postData.image_url, { responseType: 'arraybuffer' })
        imagePath = `static-posts/post-${i + 1}.png`
        const fullImagePath = path.join(postsDir, `post-${i + 1}.png`)
        fs.writeFileSync(fullImagePath, imageResponse.data)
        console.log(`  ✓ Image saved: ${imagePath}`)
      }
      
      // Create post metadata
      const postMetadata = {
        id: i,
        topic,
        caption: postData.full_caption || postData.caption,
        image: imagePath,
        hashtags: postData.hashtags || [],
        image_prompt: postData.image_prompt || null
      }
      
      posts.push(postMetadata)
      console.log(`  ✓ Post ${i + 1} complete\n`)
      
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000))
      
    } catch (error) {
      console.error(`  ✗ Error generating post ${i + 1}:`, error.message)
      // Create a placeholder post
      const postMetadata = {
        id: i,
        topic,
        caption: `Engaging content about ${topic}. Discover how this topic can transform your business and drive results.`,
        image: null, // Will use gradient
        hashtags: [],
        image_prompt: null
      }
      posts.push(postMetadata)
    }
  }
  
  // Save posts metadata as JSON
  const metadataPath = path.join(postsDir, 'posts.json')
  fs.writeFileSync(metadataPath, JSON.stringify(posts, null, 2))
  console.log(`\n✅ All posts generated!`)
  console.log(`📁 Posts saved to: ${postsDir}`)
  console.log(`📄 Metadata saved to: ${metadataPath}`)
  console.log(`\nTotal posts: ${posts.length}`)
}

generateStaticPosts().catch(console.error)


