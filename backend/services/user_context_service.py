"""
User Context Service - Builds comprehensive user profiles for better content generation
Collects and analyzes user behavior, preferences, and content history to enhance AI outputs
Now enhanced with Hyperspell for persistent memory and context
"""

import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class UserContextService:
    """Service for building and managing comprehensive user context profiles"""
    
    def __init__(self, hyperspell_service=None):
        # Context storage directory (can be migrated to database later)
        self.context_dir = os.path.join(os.path.dirname(__file__), '..', 'user_contexts')
        os.makedirs(self.context_dir, exist_ok=True)
        
        # Hyperspell integration for enhanced memory
        self.hyperspell_service = hyperspell_service
        if self.hyperspell_service and self.hyperspell_service.is_available():
            print("[UserContext] OK User context service initialized with Hyperspell")
        else:
            print("[UserContext] OK User context service initialized")
    
    def _get_user_context_path(self, user_id: str) -> str:
        """Get path to user's context file"""
        return os.path.join(self.context_dir, f"user_{user_id}.json")
    
    def _load_user_context(self, user_id: str) -> Dict:
        """Load user context from file"""
        try:
            context_path = self._get_user_context_path(user_id)
            if os.path.exists(context_path):
                with open(context_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[UserContext] Error loading context for {user_id}: {e}")
        return self._get_default_context()
    
    def _save_user_context(self, user_id: str, context: Dict):
        """Save user context to file"""
        try:
            context_path = self._get_user_context_path(user_id)
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[UserContext] Error saving context for {user_id}: {e}")
    
    def _get_default_context(self) -> Dict:
        """Get default empty context structure"""
        return {
            "user_id": None,
            "preferences": {
                "brand_voice": None,
                "content_style": None,
                "target_audience": None,
                "preferred_video_length": None,
                "video_model_preference": None,
                "platform_preferences": {},
                "content_themes": [],
                "brand_colors": [],
                "tone_preferences": []
            },
            "content_history": {
                "generated_videos": [],
                "approved_scripts": [],
                "rejected_scripts": [],
                "edited_scripts": [],
                "successful_topics": [],
                "failed_topics": []
            },
            "behavioral_patterns": {
                "most_used_platforms": [],
                "average_video_duration": None,
                "preferred_video_model": None,
                "content_generation_frequency": None,
                "editing_patterns": []
            },
            "brand_insights": {
                "extracted_brand_voice": None,
                "content_themes": [],
                "visual_style_preferences": [],
                "messaging_patterns": []
            },
            "performance_data": {
                "high_performing_content": [],
                "low_performing_content": [],
                "engagement_patterns": {}
            },
            "social_profiles": {
                "instagram_profiles_analyzed": [],
                "linkedin_profiles_analyzed": [],
                "extracted_brand_elements": {}
            },
            "document_insights": {
                "uploaded_documents": [],
                "extracted_key_themes": [],
                "brand_guidelines": None,
                "messaging_framework": None
            },
            "metadata": {
                "created_at": None,
                "last_updated": None,
                "total_generations": 0,
                "total_approvals": 0,
                "total_rejections": 0
            }
        }
    
    def get_user_context(self, user_id: str) -> Dict:
        """Get comprehensive user context"""
        return self._load_user_context(user_id)
    
    def update_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences"""
        context = self._load_user_context(user_id)
        context["user_id"] = user_id
        context["preferences"].update(preferences)
        context["metadata"]["last_updated"] = datetime.now().isoformat()
        self._save_user_context(user_id, context)
        print(f"[UserContext] Updated preferences for user {user_id}")
    
    def record_video_generation(self, user_id: str, generation_data: Dict):
        """Record a video generation event"""
        context = self._load_user_context(user_id)
        context["user_id"] = user_id
        
        # Add to content history
        generation_record = {
            "timestamp": datetime.now().isoformat(),
            "topic": generation_data.get("topic"),
            "platform": generation_data.get("platform", "linkedin"),
            "video_model": generation_data.get("video_model", "sora-2"),
            "duration": generation_data.get("duration"),
            "script_preview": generation_data.get("script", "")[:200],  # First 200 chars
            "approved": generation_data.get("approved", False),
            "edited": generation_data.get("edited", False)
        }
        
        context["content_history"]["generated_videos"].append(generation_record)
        
        # Update behavioral patterns
        if generation_data.get("approved"):
            context["content_history"]["approved_scripts"].append({
                "script": generation_data.get("script", "")[:500],
                "topic": generation_data.get("topic"),
                "timestamp": datetime.now().isoformat()
            })
            context["metadata"]["total_approvals"] = context["metadata"].get("total_approvals", 0) + 1
        
        if generation_data.get("rejected"):
            context["metadata"]["total_rejections"] = context["metadata"].get("total_rejections", 0) + 1
        
        # Update statistics
        context["metadata"]["total_generations"] = context["metadata"].get("total_generations", 0) + 1
        context["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Analyze patterns
        self._update_behavioral_patterns(context)
        
        self._save_user_context(user_id, context)
        print(f"[UserContext] Recorded video generation for user {user_id}")
    
    def record_social_profile_analysis(self, user_id: str, platform: str, profile_data: Dict):
        """Record social media profile analysis"""
        context = self._load_user_context(user_id)
        context["user_id"] = user_id
        
        profile_key = f"{platform}_profiles_analyzed"
        if profile_key in context["social_profiles"]:
            context["social_profiles"][profile_key].append({
                "username": profile_data.get("username"),
                "analyzed_at": datetime.now().isoformat(),
                "brand_elements": profile_data.get("brand_elements", {}),
                "content_themes": profile_data.get("content_themes", []),
                "visual_style": profile_data.get("visual_style", {})
            })
        
        # Extract and merge brand insights
        self._extract_brand_insights(context, profile_data)
        
        context["metadata"]["last_updated"] = datetime.now().isoformat()
        self._save_user_context(user_id, context)
        print(f"[UserContext] Recorded {platform} profile analysis for user {user_id}")
    
    def record_document_analysis(self, user_id: str, document_data: Dict):
        """Record document upload and analysis, including web research data"""
        context = self._load_user_context(user_id)
        context["user_id"] = user_id
        
        # Handle both single document and multiple documents
        document_ids = document_data.get("document_ids", [])
        if not document_ids and document_data.get("document_id"):
            document_ids = [document_data.get("document_id")]
        
        doc_record = {
            "document_ids": document_ids,
            "filename": document_data.get("filename"),
            "uploaded_at": datetime.now().isoformat(),
            "extracted_themes": document_data.get("themes", []),
            "key_insights": document_data.get("key_insights", []),
            "companies_found": document_data.get("companies_found", []),
            "web_research": document_data.get("research_data", {})
        }
        
        context["document_insights"]["uploaded_documents"].append(doc_record)
        
        # Merge themes
        existing_themes = set(context["document_insights"]["extracted_key_themes"])
        new_themes = set(document_data.get("themes", []))
        context["document_insights"]["extracted_key_themes"] = list(existing_themes.union(new_themes))
        
        # Store companies found for future reference
        companies_found = document_data.get("companies_found", [])
        if companies_found:
            if "companies_researched" not in context["document_insights"]:
                context["document_insights"]["companies_researched"] = []
            existing_companies = set(context["document_insights"]["companies_researched"])
            context["document_insights"]["companies_researched"] = list(existing_companies.union(set(companies_found)))
        
        context["metadata"]["last_updated"] = datetime.now().isoformat()
        self._save_user_context(user_id, context)
        print(f"[UserContext] Recorded document analysis for user {user_id} (companies: {len(companies_found)})")
    
    def _update_behavioral_patterns(self, context: Dict):
        """Analyze and update behavioral patterns from content history"""
        videos = context["content_history"]["generated_videos"]
        if not videos:
            return
        
        # Calculate average duration
        durations = [v.get("duration") for v in videos if v.get("duration")]
        if durations:
            context["behavioral_patterns"]["average_video_duration"] = sum(durations) / len(durations)
        
        # Find most used video model
        models = [v.get("video_model") for v in videos if v.get("video_model")]
        if models:
            from collections import Counter
            model_counts = Counter(models)
            context["behavioral_patterns"]["preferred_video_model"] = model_counts.most_common(1)[0][0]
        
        # Find most used platforms
        platforms = [v.get("platform") for v in videos if v.get("platform")]
        if platforms:
            from collections import Counter
            platform_counts = Counter(platforms)
            context["behavioral_patterns"]["most_used_platforms"] = [
                {"platform": p, "count": c} 
                for p, c in platform_counts.most_common(5)
            ]
        
        # Extract successful topics
        approved_videos = [v for v in videos if v.get("approved")]
        if approved_videos:
            topics = [v.get("topic") for v in approved_videos if v.get("topic")]
            context["content_history"]["successful_topics"] = list(set(topics))[:10]  # Top 10 unique topics
    
    def _extract_brand_insights(self, context: Dict, profile_data: Dict):
        """Extract and merge brand insights from profile data"""
        # Merge content themes
        existing_themes = set(context["brand_insights"].get("content_themes", []))
        new_themes = set(profile_data.get("content_themes", []))
        context["brand_insights"]["content_themes"] = list(existing_themes.union(new_themes))[:20]
        
        # Update visual style preferences
        visual_style = profile_data.get("visual_style", {})
        if visual_style:
            existing_styles = context["brand_insights"].get("visual_style_preferences", [])
            existing_styles.append(visual_style)
            context["brand_insights"]["visual_style_preferences"] = existing_styles[-10:]  # Keep last 10
    
    async def get_context_summary_for_ai(self, user_id: str, query: Optional[str] = None) -> str:
        """
        Generate a comprehensive context summary for AI prompt injection
        Enhanced with Hyperspell memory queries if available
        
        Args:
            user_id: User identifier
            query: Optional query string to fetch relevant Hyperspell memories
        """
        context = self._load_user_context(user_id)
        
        summary_parts = []
        
        # Hyperspell Memory Context (if available and query provided)
        if self.hyperspell_service and self.hyperspell_service.is_available() and query:
            try:
                hyperspell_context = await self.hyperspell_service.get_context_summary(user_id, query)
                if hyperspell_context:
                    summary_parts.append(hyperspell_context)
                    summary_parts.append("")
            except Exception as e:
                print(f"[UserContext] Error fetching Hyperspell context: {e}")
        
        if not context.get("user_id"):
            # If no local context but we have Hyperspell results, return those
            if summary_parts:
                return "\n".join(summary_parts)
            return ""  # No context available
        
        # User Preferences
        prefs = context.get("preferences", {})
        if any(prefs.values()):
            summary_parts.append("USER PREFERENCES:")
            if prefs.get("brand_voice"):
                summary_parts.append(f"- Brand Voice: {prefs['brand_voice']}")
            if prefs.get("content_style"):
                summary_parts.append(f"- Content Style: {prefs['content_style']}")
            if prefs.get("target_audience"):
                summary_parts.append(f"- Target Audience: {prefs['target_audience']}")
            if prefs.get("preferred_video_length"):
                summary_parts.append(f"- Preferred Video Length: {prefs['preferred_video_length']} seconds")
            if prefs.get("video_model_preference"):
                summary_parts.append(f"- Preferred Video Model: {prefs['video_model_preference']}")
            summary_parts.append("")
        
        # Brand Insights
        brand = context.get("brand_insights", {})
        if brand.get("content_themes"):
            summary_parts.append("BRAND CONTENT THEMES:")
            summary_parts.append(f"- {', '.join(brand['content_themes'][:10])}")
            summary_parts.append("")
        
        if brand.get("extracted_brand_voice"):
            summary_parts.append("BRAND VOICE:")
            summary_parts.append(f"- {brand['extracted_brand_voice']}")
            summary_parts.append("")
        
        # Successful Content Patterns
        successful = context.get("content_history", {}).get("successful_topics", [])
        if successful:
            summary_parts.append("SUCCESSFUL CONTENT TOPICS (based on user approvals):")
            summary_parts.append(f"- {', '.join(successful[:5])}")
            summary_parts.append("")
        
        # Behavioral Patterns
        patterns = context.get("behavioral_patterns", {})
        if patterns.get("average_video_duration"):
            summary_parts.append("USER BEHAVIOR PATTERNS:")
            summary_parts.append(f"- Average Video Duration: {patterns['average_video_duration']:.1f} seconds")
            if patterns.get("preferred_video_model"):
                summary_parts.append(f"- Preferred Video Model: {patterns['preferred_video_model']}")
            if patterns.get("most_used_platforms"):
                platforms = [p["platform"] for p in patterns["most_used_platforms"][:3]]
                summary_parts.append(f"- Most Used Platforms: {', '.join(platforms)}")
            summary_parts.append("")
        
        # Document Insights
        doc_themes = context.get("document_insights", {}).get("extracted_key_themes", [])
        if doc_themes:
            summary_parts.append("DOCUMENT-BASED THEMES:")
            summary_parts.append(f"- {', '.join(doc_themes[:10])}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def get_preferred_settings(self, user_id: str) -> Dict:
        """Get user's preferred settings for auto-filling forms"""
        context = self._load_user_context(user_id)
        patterns = context.get("behavioral_patterns", {})
        prefs = context.get("preferences", {})
        
        return {
            "preferred_video_model": patterns.get("preferred_video_model") or prefs.get("video_model_preference") or "sora-2",
            "preferred_duration": patterns.get("average_video_duration") or prefs.get("preferred_video_length") or 8,
            "preferred_platform": patterns.get("most_used_platforms", [{}])[0].get("platform") if patterns.get("most_used_platforms") else "linkedin",
            "target_audience": prefs.get("target_audience"),
            "content_style": prefs.get("content_style")
        }

