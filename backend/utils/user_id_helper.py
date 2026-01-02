"""
User ID Helper - Ensures consistent user_id normalization across the application
CRITICAL: This ensures memories persist across sessions and deployments
"""

from typing import Optional
from database import User


def normalize_user_id(user: Optional[User] = None, user_email: Optional[str] = None, user_id: Optional[str] = None) -> str:
    """
    Normalize user ID for consistent memory storage and retrieval
    
    CRITICAL: This function ensures memories persist across:
    - Backend restarts
    - Deployments
    - User sessions
    - Code changes
    
    Args:
        user: User object from database
        user_email: Email string (alternative to user object)
        user_id: Direct user ID string (alternative)
        
    Returns:
        Normalized user ID (lowercase email, no whitespace)
    """
    # Priority: user object > user_email > user_id > anonymous
    if user and hasattr(user, 'email') and user.email:
        email = user.email
    elif user_email:
        email = user_email
    elif user_id:
        email = user_id
    else:
        return "anonymous_user"
    
    # Normalize: lowercase, strip whitespace, remove any special formatting
    normalized = email.lower().strip()
    # Remove any extra whitespace or special characters
    normalized = normalized.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')
    
    return normalized


def get_user_id_from_request(current_user: Optional[User] = None) -> str:
    """
    Get normalized user ID from FastAPI dependency (get_current_user)
    
    This is the recommended way to get user_id in API endpoints
    
    Args:
        current_user: User object from Depends(get_current_user)
        
    Returns:
        Normalized user ID
    """
    return normalize_user_id(user=current_user)

