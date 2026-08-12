"""
Initializes the Firebase Admin SDK exactly once. This is the ONLY file
that should call firebase_admin.initialize_app(). Everything else that
needs to verify tokens imports `firebase_auth` from here.
"""
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth as firebase_auth  # real firebase_admin.auth module

from app.core.config import settings

if not firebase_admin._apps:
    cred = credentials.Certificate(settings.firebase_service_account_path)
    firebase_admin.initialize_app(cred)

# Other modules do: from app.firebase.firebase_client import firebase_auth
__all__ = ["firebase_auth"]