import firebase_admin
from firebase_admin import credentials, auth, db, firestore
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class FirebaseConfig:
    def __init__(self):
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "blink2-c6aae")
        self.api_key = os.getenv("FIREBASE_API_KEY", "AIzaSyDScQZuqfUj3i8RGbjj0FkeYYsiibowgrU")
        self.database_url = f"https://{self.project_id}-default-rtdb.firebaseio.com/"
        
        # Initialize Firebase Admin
        self._init_admin()
    
    def _init_admin(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            if not firebase_admin._apps:
                # Service Account credentials
                cred_dict = {
                    "type": os.getenv("FIREBASE_TYPE", "service_account"),
                    "project_id": self.project_id,
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
                }
                
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(
                    cred, 
                    {
                        'databaseURL': self.database_url,
                        'projectId': self.project_id
                    }
                )
                logger.info("✅ Firebase Admin initialized successfully")
            else:
                logger.info("✅ Firebase Admin already initialized")
                
        except Exception as e:
            logger.error(f"❌ Firebase Admin init failed: {e}")
            raise
    
    @property
    def auth(self):
        """Firebase Authentication"""
        return auth
    
    @property
    def realtime_db(self):
        """Realtime Database references"""
        return {
            'tenders': db.reference('tenders'),
            'users': db.reference('users'),
            'subscriptions': db.reference('subscriptions'),
            'stats': db.reference('stats')
        }
    
    @property
    def firestore(self):
        """Firestore client (if needed)"""
        try:
            from firebase_admin import firestore
            return firestore.client()
        except:
            return None
    
    def verify_id_token(self, id_token: str):
        """Verify Firebase ID token"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

# Global Firebase instance
firebase_config = FirebaseConfig()

# Convenience references
tenders_ref = firebase_config.realtime_db['tenders']
users_ref = firebase_config.realtime_db['users']
subscriptions_ref = firebase_config.realtime_db['subscriptions']
stats_ref = firebase_config.realtime_db['stats']

# Web Client Config (for frontend)
WEB_FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDScQZuqfUj3i8RGbjj0FkeYYsiibowgrU",
    "authDomain": "blink2-c6aae.firebaseapp.com",
    "projectId": "blink2-c6aae",
    "storageBucket": "blink2-c6aae.appspot.com",
    "messagingSenderId": "620469418767",
    "appId": "1:620469418767:web:11b28102a4804178819c7a"
}
