import firebase_admin
from firebase_admin import credentials, auth, db
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class FirebaseConfig:
    def __init__(self):
        self.project_id = os.getenv("FIREBASE_PROJECT_ID")
        self.database_url = f"https://{self.project_id}-default-rtdb.firebaseio.com/"
        self._init_admin()
    
    def _init_admin(self):
        try:
            if not firebase_admin._apps:
                # YOUR EXACT service account credentials
                cred_dict = {
                    "type": os.getenv("FIREBASE_TYPE"),
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
                    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
                    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
                }
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(
                    cred, 
                    {'databaseURL': self.database_url}
                )
                logger.info("✅ Firebase Admin initialized - YOUR PROJECT!")
        except Exception as e:
            logger.error(f"❌ Firebase init failed: {e}")

# Initialize
firebase_config = FirebaseConfig()

# Database references
tenders_ref = db.reference('tenders')
users_ref = db.reference('users')
subscriptions_ref = db.reference('subscriptions')

# Web client config (for frontend)
WEB_FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDScQZuqfUj3i8RGbjj0FkeYYsiibowgrU",
    "authDomain": "blink2-c6aae.firebaseapp.com",
    "projectId": "blink2-c6aae",
    "storageBucket": "blink2-c6aae.appspot.com",
    "messagingSenderId": "620469418767",
    "appId": "1:620469418767:web:11b28102a4804178819c7a"
}
