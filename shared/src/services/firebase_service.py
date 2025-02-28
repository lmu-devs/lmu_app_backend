import json
import os
from typing import Dict, List, Optional, Union

import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from shared.src.core.logging import get_main_logger
from shared.src.core.settings import get_settings


logger = get_main_logger(__name__)
settings = get_settings()


class FirebaseService:
    """Service for handling Firebase Cloud Messaging (FCM) notifications."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not FirebaseService._initialized:
            self._initialize_firebase()
            FirebaseService._initialized = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with service account credentials."""
        try:
            # Check if Firebase credentials are provided as environment variable
            firebase_credentials_json = settings.FIREBASE_CREDENTIALS
            
            if firebase_credentials_json:
                # Use credentials from environment variable
                cred_dict = json.loads(firebase_credentials_json)
                cred = credentials.Certificate(cred_dict)
            else:
                # Use credentials from file
                cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "/env/firebaseServiceAccountKey.json")
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    logger.error(f"Firebase credentials file not found at {cred_path}")
                    return
            
            # Initialize the app
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
    
    def send_notification(
        self,
        tokens: Union[str, List[str]],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        topic: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> Dict:
        """
        Send a notification to one or multiple devices using FCM.
        
        Args:
            tokens: Device token(s) to send the notification to
            title: Notification title
            body: Notification body
            data: Additional data to send with the notification
            topic: Topic to send the notification to (instead of tokens)
            image_url: URL of an image to include in the notification
            
        Returns:
            Dict containing success and failure counts
        """
        if not firebase_admin._apps:
            logger.error("Firebase Admin SDK not initialized")
            return {"success": 0, "failure": 1, "error": "Firebase Admin SDK not initialized"}
        
        # Create notification
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url,
        )
        
        # Create message
        message = messaging.MulticastMessage(
            notification=notification,
            data=data or {},
            tokens=tokens if isinstance(tokens, list) else [tokens],
        ) if tokens else messaging.Message(
            notification=notification,
            data=data or {},
            topic=topic,
        )
        
        try:
            # Send message
            if tokens:
                response = messaging.send_multicast(message)
                logger.info(f"Successfully sent message: {response}")
                return {
                    "success": response.success_count,
                    "failure": response.failure_count,
                }
            else:
                response = messaging.send(message)
                logger.info(f"Successfully sent message to topic: {response}")
                return {"success": 1, "failure": 0}
        except FirebaseError as e:
            logger.error(f"Error sending message: {e}")
            return {"success": 0, "failure": 1, "error": str(e)}
    
    def subscribe_to_topic(self, tokens: Union[str, List[str]], topic: str) -> Dict:
        """
        Subscribe device(s) to a topic.
        
        Args:
            tokens: Device token(s) to subscribe
            topic: Topic to subscribe to
            
        Returns:
            Dict containing success and failure counts
        """
        if not firebase_admin._apps:
            logger.error("Firebase Admin SDK not initialized")
            return {"success": 0, "failure": 1, "error": "Firebase Admin SDK not initialized"}
        
        try:
            tokens_list = tokens if isinstance(tokens, list) else [tokens]
            response = messaging.subscribe_to_topic(tokens_list, topic)
            logger.info(f"Successfully subscribed to topic: {response}")
            return {
                "success": response.success_count,
                "failure": response.failure_count,
            }
        except FirebaseError as e:
            logger.error(f"Error subscribing to topic: {e}")
            return {"success": 0, "failure": 1, "error": str(e)}
    
    def unsubscribe_from_topic(self, tokens: Union[str, List[str]], topic: str) -> Dict:
        """
        Unsubscribe device(s) from a topic.
        
        Args:
            tokens: Device token(s) to unsubscribe
            topic: Topic to unsubscribe from
            
        Returns:
            Dict containing success and failure counts
        """
        if not firebase_admin._apps:
            logger.error("Firebase Admin SDK not initialized")
            return {"success": 0, "failure": 1, "error": "Firebase Admin SDK not initialized"}
        
        try:
            tokens_list = tokens if isinstance(tokens, list) else [tokens]
            response = messaging.unsubscribe_from_topic(tokens_list, topic)
            logger.info(f"Successfully unsubscribed from topic: {response}")
            return {
                "success": response.success_count,
                "failure": response.failure_count,
            }
        except FirebaseError as e:
            logger.error(f"Error unsubscribing from topic: {e}")
            return {"success": 0, "failure": 1, "error": str(e)} 