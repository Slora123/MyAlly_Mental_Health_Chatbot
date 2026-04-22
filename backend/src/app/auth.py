import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.app.database import get_db
from src.app.models import User

# Load Firebase credentials
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
if firebase_cred_path and os.path.exists(firebase_cred_path):
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)
else:
    print("⚠️ WARNING: Firebase credentials not found. Authentication will bypass for testing.")
    # For a real production app, you would raise an exception here.
    # We will allow a dummy fallback for development if keys aren't set.

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    
    # Development bypass if no Firebase configured
    if not firebase_cred_path or not os.path.exists(firebase_cred_path):
        if token == "dummy-dev-token":
            user = db.query(User).filter(User.uid == "dev-user-123").first()
            if not user:
                user = User(uid="dev-user-123", email="dev@example.com", name="Dev User")
                db.add(user)
                db.commit()
                db.refresh(user)
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials (Firebase not configured)",
        )

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        user = db.query(User).filter(User.uid == uid).first()
        if not user:
            # Create a basic user record if they just signed up
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', 'Anonymous')
            user = User(uid=uid, email=email, name=name)
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )
