import asyncio
import os
import sys
from pathlib import Path
import base64
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_env = Path(__file__).parent / "backend" / ".env"
if backend_env.exists():
    load_dotenv(backend_env)
    print(f"✓ Loaded environment from {backend_env}")
else:
    # Try root .env
    root_env = Path(__file__).parent / ".env"
    if root_env.exists():
        load_dotenv(root_env)
        print(f"✓ Loaded environment from {root_env}")
    else:
        print("⚠️ No .env file found. Make sure GOOGLE_CLOUD_PROJECT_ID is set.")

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.image_generation_service import ImageGenerationService

# Marketing post topics for image generation
MARKETING_TOPICS = [
    "E-commerce growth - online shopping platform interface, modern design, vibrant product displays, professional photography",
    "Social media engagement - creative social media dashboard, colorful analytics, engaging content visuals, Instagram-ready",
    "Content creation tips - professional content creator workspace, modern equipment, inspiring creative environment",
    "Business automation - automated workflow visualization, sleek technology, professional office setting, modern aesthetic",
    "Creative design inspiration - artistic workspace with design tools, colorful creative elements, professional studio lighting"
]

async def generate_marketing_images():
    """Generate 5 marketing post images using Imagen"""
    
    # Create output directory
    output_dir = Path("frontend/public/static-posts/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check existing images to determine starting number
    existing_images = list(output_dir.glob("marketing-post-*.png"))
    if existing_images:
        # Get the highest number
        numbers = [int(f.stem.split("-")[-1]) for f in existing_images if f.stem.split("-")[-1].isdigit()]
        start_number = max(numbers) + 1 if numbers else 1
    else:
        start_number = 1
    
    print(f"🎨 Generating 5 more marketing post images with Imagen...")
    print(f"   Starting from image number {start_number}\n")
    
    # Initialize image generation service
    image_service = ImageGenerationService()
    
    if not image_service.project_id:
        print("❌ Error: GOOGLE_CLOUD_PROJECT_ID not set in environment")
        print("   Please set GOOGLE_CLOUD_PROJECT_ID in your .env file")
        return
    
    print(f"✓ Image service initialized")
    print(f"  Project ID: {image_service.project_id}")
    print(f"  Location: {image_service.location}\n")
    
    generated_images = []
    
    for i, topic in enumerate(MARKETING_TOPICS, 0):
        image_number = start_number + i
        print(f"{'='*60}")
        print(f"Generating image {i + 1}/5 (will be saved as marketing-post-{image_number}.png)")
        print(f"Topic: {topic[:60]}...")
        print(f"{'='*60}")
        
        try:
            # Generate image using Imagen
            result = await image_service.generate_image(
                prompt=topic,
                model="imagen",  # Use Imagen via Vertex AI
                size="1024x1024",
                quality="high",
                aspect_ratio="1:1"
            )
            
            # Save image
            if result.get("image_base64"):
                image_filename = f"marketing-post-{image_number}.png"
                image_path = output_dir / image_filename
                
                # Decode and save
                image_data = base64.b64decode(result["image_base64"])
                image_path.write_bytes(image_data)
                
                print(f"✅ Image {image_number} saved: {image_path}")
                generated_images.append({
                    "number": image_number,
                    "topic": topic,
                    "filename": image_filename,
                    "path": str(image_path),
                    "relative_path": f"static-posts/images/{image_filename}"
                })
            else:
                print(f"❌ No image data returned for image {image_number}")
                
        except Exception as e:
            print(f"❌ Error generating image {i}: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Small delay between requests
        if i < len(MARKETING_TOPICS):
            print(f"\n⏳ Waiting 2 seconds before next image...\n")
            await asyncio.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Image Generation Complete!")
    print(f"{'='*60}")
    print(f"Total images generated: {len(generated_images)}")
    print(f"Output directory: {output_dir}")
    print(f"\nGenerated images:")
    for img in generated_images:
        print(f"  {img['number']}. {img['filename']}")
        print(f"     Path: {img['relative_path']}")
    
    return generated_images

if __name__ == "__main__":
    asyncio.run(generate_marketing_images())

