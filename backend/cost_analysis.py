"""
Cost Analysis Tool for Marketing Post Feature
Analyzes token usage and costs for concurrent users
"""

# OpenAI Pricing (as of Dec 2024)
# GPT-4o: $2.50 per 1M input tokens, $10.00 per 1M output tokens
# GPT-4o-mini: $0.150 per 1M input tokens, $0.600 per 1M output tokens
# DALL-E 3: $0.040 per image (1024x1024)

# Estimated token usage per marketing post request:
# 1. Image prompt generation: ~800 input tokens, ~150 output tokens
# 2. Caption generation: ~1200 input tokens, ~200 output tokens
# 3. Context retrieval: ~500 tokens (from Mem0, but uses embeddings - minimal cost)

# Note: Currently using static images (no image generation cost)
# If using Imagen/DALL-E: +$0.04-0.20 per image

def calculate_marketing_post_costs(num_users: int, model: str = "gpt-4o-2024-08-06"):
    """
    Calculate costs for marketing post generation at scale
    
    Args:
        num_users: Number of concurrent users
        model: OpenAI model being used
    """
    
    # Token estimates per request (based on code analysis)
    IMAGE_PROMPT_INPUT_TOKENS = 800  # Topic + brand context + user context
    IMAGE_PROMPT_OUTPUT_TOKENS = 150  # Generated image prompt
    CAPTION_INPUT_TOKENS = 1200  # Topic + brand context + user context + performance context
    CAPTION_OUTPUT_TOKENS = 200  # Generated caption + hashtags
    
    # Pricing per 1M tokens
    if "mini" in model.lower():
        INPUT_COST_PER_M = 0.150
        OUTPUT_COST_PER_M = 0.600
    else:  # GPT-4o
        INPUT_COST_PER_M = 2.50
        OUTPUT_COST_PER_M = 10.00
    
    # Calculate per-request costs
    image_prompt_cost = (
        (IMAGE_PROMPT_INPUT_TOKENS / 1_000_000) * INPUT_COST_PER_M +
        (IMAGE_PROMPT_OUTPUT_TOKENS / 1_000_000) * OUTPUT_COST_PER_M
    )
    
    caption_cost = (
        (CAPTION_INPUT_TOKENS / 1_000_000) * INPUT_COST_PER_M +
        (CAPTION_OUTPUT_TOKENS / 1_000_000) * OUTPUT_COST_PER_M
    )
    
    total_per_request = image_prompt_cost + caption_cost
    
    # Calculate for N users
    total_input_tokens = num_users * (IMAGE_PROMPT_INPUT_TOKENS + CAPTION_INPUT_TOKENS)
    total_output_tokens = num_users * (IMAGE_PROMPT_OUTPUT_TOKENS + CAPTION_OUTPUT_TOKENS)
    
    total_cost = num_users * total_per_request
    
    # Add image generation cost if using API (currently using static images = $0)
    image_gen_cost_per_image = 0.00  # Static images = free
    # If using DALL-E: 0.04, If using Imagen: ~0.20 (varies)
    total_image_cost = num_users * image_gen_cost_per_image
    
    total_cost_with_images = total_cost + total_image_cost
    
    return {
        "num_users": num_users,
        "model": model,
        "per_request": {
            "image_prompt_tokens": IMAGE_PROMPT_INPUT_TOKENS + IMAGE_PROMPT_OUTPUT_TOKENS,
            "caption_tokens": CAPTION_INPUT_TOKENS + CAPTION_OUTPUT_TOKENS,
            "total_tokens": IMAGE_PROMPT_INPUT_TOKENS + IMAGE_PROMPT_OUTPUT_TOKENS + CAPTION_INPUT_TOKENS + CAPTION_OUTPUT_TOKENS,
            "cost": total_per_request,
            "image_prompt_cost": image_prompt_cost,
            "caption_cost": caption_cost
        },
        "total": {
            "input_tokens": total_input_tokens,
            "output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "cost": total_cost,
            "image_generation_cost": total_image_cost,
            "total_cost_with_images": total_cost_with_images
        },
        "pricing": {
            "input_cost_per_m": INPUT_COST_PER_M,
            "output_cost_per_m": OUTPUT_COST_PER_M,
            "image_cost_per_image": image_gen_cost_per_image
        }
    }

def format_cost_analysis(results: dict):
    """Format cost analysis results for display"""
    print("=" * 80)
    print("MARKETING POST COST ANALYSIS")
    print("=" * 80)
    print(f"\nModel: {results['model']}")
    print(f"Number of Concurrent Users: {results['num_users']}")
    print(f"\n{'─' * 80}")
    print("PER REQUEST BREAKDOWN:")
    print(f"  Image Prompt Generation:")
    print(f"    - Tokens: {results['per_request']['image_prompt_tokens']:,}")
    print(f"    - Cost: ${results['per_request']['image_prompt_cost']:.6f}")
    print(f"  Caption Generation:")
    print(f"    - Tokens: {results['per_request']['caption_tokens']:,}")
    print(f"    - Cost: ${results['per_request']['caption_cost']:.6f}")
    print(f"  Total per Request:")
    print(f"    - Tokens: {results['per_request']['total_tokens']:,}")
    print(f"    - Cost: ${results['per_request']['cost']:.6f}")
    print(f"\n{'─' * 80}")
    print("TOTAL FOR ALL USERS:")
    print(f"  Input Tokens: {results['total']['input_tokens']:,}")
    print(f"  Output Tokens: {results['total']['output_tokens']:,}")
    print(f"  Total Tokens: {results['total']['total_tokens']:,}")
    print(f"  API Cost: ${results['total']['cost']:.4f}")
    print(f"  Image Generation Cost: ${results['total']['image_generation_cost']:.4f} (static images = free)")
    print(f"  TOTAL COST: ${results['total']['total_cost_with_images']:.4f}")
    print(f"\n{'─' * 80}")
    print("PRICING REFERENCE:")
    print(f"  Input: ${results['pricing']['input_cost_per_m']:.3f} per 1M tokens")
    print(f"  Output: ${results['pricing']['output_cost_per_m']:.3f} per 1M tokens")
    print(f"  Images: ${results['pricing']['image_cost_per_image']:.4f} per image (currently using static)")
    print("=" * 80)
    
    # Calculate realistic usage projections
    print("\nPROJECTIONS (Realistic Usage Patterns):")
    per_request_cost = results['total']['total_cost_with_images'] / results['num_users']
    
    # Scenario 1: Each user generates 1 post per day
    daily_cost_1_post_per_user = per_request_cost * results['num_users'] * 1
    monthly_cost_1_post_per_user = daily_cost_1_post_per_user * 30
    
    # Scenario 2: Active users generate 5 posts per day
    daily_cost_5_posts_per_user = per_request_cost * results['num_users'] * 5
    monthly_cost_5_posts_per_user = daily_cost_5_posts_per_user * 30
    
    # Scenario 3: Very active users generate 20 posts per day
    daily_cost_20_posts_per_user = per_request_cost * results['num_users'] * 20
    monthly_cost_20_posts_per_user = daily_cost_20_posts_per_user * 30
    
    print(f"  Per Request: ${per_request_cost:.6f}")
    print(f"  1 post/user/day: ${daily_cost_1_post_per_user:.2f}/day | ${monthly_cost_1_post_per_user:.2f}/month")
    print(f"  5 posts/user/day: ${daily_cost_5_posts_per_user:.2f}/day | ${monthly_cost_5_posts_per_user:.2f}/month")
    print(f"  20 posts/user/day: ${daily_cost_20_posts_per_user:.2f}/day | ${monthly_cost_20_posts_per_user:.2f}/month")
    print("=" * 80)

if __name__ == "__main__":
    import sys
    
    # Default to gpt-4o-2024-08-06 (from openai_service.py)
    model = "gpt-4o-2024-08-06"
    
    # Test scenarios
    scenarios = [50, 100]
    
    print("\n" + "=" * 80)
    print("MARKETING POST COST ANALYSIS - MULTIPLE SCENARIOS")
    print("=" * 80 + "\n")
    
    for num_users in scenarios:
        results = calculate_marketing_post_costs(num_users, model)
        format_cost_analysis(results)
        print("\n")
    
    # Also calculate with GPT-4o-mini for comparison
    print("\n" + "=" * 80)
    print("COMPARISON: GPT-4o-mini (Cheaper Alternative)")
    print("=" * 80 + "\n")
    
    for num_users in scenarios:
        results = calculate_marketing_post_costs(num_users, "gpt-4o-mini")
        format_cost_analysis(results)
        print("\n")

