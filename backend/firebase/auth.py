from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import firebase_admin.auth as auth
from ..firebase.config import firebase_config
from datetime import datetime

security = HTTPBearer()

class User(BaseModel):
    uid: str
    email: str
    is_premium: bool = False
    subscription_end: Optional[datetime] = None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user with premium status"""
    try:
        # Verify Firebase ID token
        decoded_token = firebase_config.verify_id_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        
        # Check premium status
        from ..firebase.config import subscriptions_ref, users_ref
        subscription = subscriptions_ref.child(uid).get()
        user_data = users_ref.child(uid).get()
        
        is_premium = False
        subscription_end = None
        
        if subscription and subscription.get('is_premium'):
            is_premium = True
            subscription_end = subscription.get('subscription_end')
        
        elif user_data and user_data.get('is_premium'):
            is_premium = True
        
        return User(
            uid=uid,
            email=email,
            is_premium=is_premium,
            subscription_end=subscription_end
        )
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")
