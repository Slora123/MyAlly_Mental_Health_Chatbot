import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from . import vector_db

# Load Firebase credentials
from dotenv import load_dotenv
from pathlib import Path

root_env = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=root_env)

firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
if firebase_cred_path and os.path.exists(firebase_cred_path):
    # If path is relative, make it relative to backend root
    if not os.path.isabs(firebase_cred_path):
        firebase_cred_path = os.path.join(Path(__file__).resolve().parents[2], firebase_cred_path)
    
    print(f"🔐 Initializing Firebase with: {firebase_cred_path}")
    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_cred_path)
        firebase_admin.initialize_app(cred)
else:
    print(f"⚠️ WARNING: Firebase credentials NOT found at: {firebase_cred_path}")

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    
    # Development bypass if no Firebase configured
    if not firebase_cred_path or not os.path.exists(firebase_cred_path):
        if token == "dummy-dev-token":
            uid = "dev-user-123"
            user = vector_db.get_user_profile(uid)
            if not user:
                user = vector_db.save_user_profile(uid, {"email": "dev@example.com", "name": "Dev User"})
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials (Firebase not configured)",
        )

    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        
        user = vector_db.get_user_profile(uid)
        if not user:
            # Create a basic user record if they just signed up
            email = decoded_token.get('email', '')
            name = decoded_token.get('name', 'Anonymous')
            user = vector_db.save_user_profile(uid, {"email": email, "name": name})
            
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
        )
