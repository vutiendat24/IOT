

from fastapi import Header, HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify Firebase Auth token from Authorization header
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        User ID from verified token
        
    Raises:
        HTTPException: If token is invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    try:
        # Extract token
        scheme, token = authorization.split()
        
        if scheme.lower() != 'bearer':
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )
        
        # Verify token with Firebase
        # Note: This requires firebase_service to be available
        # In production, you'd import and use firebase_admin.auth.verify_id_token
        
        # For now, return a mock user_id
        # TODO: Implement actual token verification
        logger.warning("Using mock token verification - implement Firebase Auth")
        
        # Mock verification
        if token == "test_token":
            return "test_user_123"
        
        # Actual verification (uncomment when Firebase is configured)
        # from firebase_admin import auth
        # decoded_token = auth.verify_id_token(token)
        # return decoded_token['uid']
        
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
        
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Token verification failed"
        )