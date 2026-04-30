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
firebase_cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")

if not firebase_admin._apps:
    if firebase_cred_json:
        # Use JSON string directly from env variable (Good for Render)
        import json
        try:
            cred_dict = json.loads(firebase_cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("🔐 Initialized Firebase using FIREBASE_CREDENTIALS_JSON")
            firebase_cred_path = "env_json" # Mark as configured
        except Exception as e:
            print(f"❌ Error parsing FIREBASE_CREDENTIALS_JSON: {e}")
    
    elif firebase_cred_path:
        # Resolve path
        if not os.path.isabs(firebase_cred_path):
            # Try root of project first
            root_path = Path(__file__).resolve().parents[2]
            possible_path = root_path / firebase_cred_path
            if possible_path.exists():
                firebase_cred_path = str(possible_path)
            else:
                # Try relative to current file's parent's parent (backend/)
                firebase_cred_path = os.path.join(root_path, firebase_cred_path)
        
        if os.path.exists(firebase_cred_path):
            print(f"🔐 Initializing Firebase with file: {firebase_cred_path}")
            cred = credentials.Certificate(firebase_cred_path)
            firebase_admin.initialize_app(cred)
        else:
            print(f"⚠️ WARNING: Firebase credentials file NOT found at: {firebase_cred_path}")
            firebase_cred_path = None
    else:
        print("⚠️ WARNING: No Firebase configuration found (Path or JSON)")

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    
    # Check if Firebase is initialized
    is_configured = firebase_admin._apps or (firebase_cred_path and os.path.exists(firebase_cred_path))
    
    # Development bypass if no Firebase configured
    if not is_configured:
        if token == "dummy-dev-token":
            uid = "dev-user-123"
            user = vector_db.get_user_profile(uid)
            if not user:
                user = vector_db.save_user_profile(uid, {"email": "dev@example.com", "name": "Dev User"})
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials (Firebase not configured on server)",
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
