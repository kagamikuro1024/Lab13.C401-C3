"""
Authentication Module — API Key validation and user identification
"""

from fastapi import HTTPException, status


class AuthManager:
    """Handle API key authentication"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid format
        """
        if not api_key:
            return False
        # Allow any non-empty string as API key
        # In production, validate against database
        return len(api_key) > 0
    
    @staticmethod
    def extract_user_id(api_key: str = None) -> str:
        """
        Extract user ID from API key or generate anonymous ID.
        
        Args:
            api_key: API key (optional)
            
        Returns:
            User identifier
        """
        if api_key:
            return api_key[:20]  # Use first 20 chars as user ID
        else:
            return "anonymous"
    
    @staticmethod
    def require_auth(api_key: str = None) -> str:
        """
        Middleware to require authentication.
        
        Args:
            api_key: API key from request
            
        Returns:
            User ID if valid
            
        Raises:
            HTTPException: If invalid
        """
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not AuthManager.validate_api_key(api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return AuthManager.extract_user_id(api_key)
