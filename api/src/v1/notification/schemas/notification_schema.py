from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from shared.src.enums.language_enums import LanguageEnum


class NotificationTranslationBase(BaseModel):
    """Base schema for notification translation data."""

    language: LanguageEnum = Field(..., description="Language of the translation")
    title: str = Field(..., description="Notification title")
    body: str = Field(..., description="Notification body")


class NotificationTranslationCreate(NotificationTranslationBase):
    """Schema for creating a notification translation."""

    pass


class NotificationTranslationResponse(NotificationTranslationBase):
    """Schema for notification translation response."""

    notification_id: str = Field(..., description="ID of the notification this translation belongs to")
    created_at: datetime = Field(..., description="When the translation was created")
    updated_at: datetime = Field(..., description="When the translation was last updated")

    class Config:
        from_attributes = True


class NotificationBase(BaseModel):
    """Base schema for notification data."""

    image_url: Optional[str] = Field(None, description="URL of an image to include in the notification")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data to send with the notification")
    base_topic: Optional[str] = Field(None, description="Base topic name for localized notifications")


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""

    # Default translation in the primary language
    title: str = Field(..., description="Notification title (default language)")
    body: str = Field(..., description="Notification body (default language)")
    language: LanguageEnum = Field(default=LanguageEnum.GERMAN, description="Language for the default translation")
    # Optional additional translations
    translations: Optional[List[NotificationTranslationCreate]] = Field(
        None, description="Additional translations for the notification"
    )


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    id: str = Field(..., description="Notification ID")
    is_sent: bool = Field(..., description="Whether the notification has been sent")
    sent_at: Optional[datetime] = Field(None, description="When the notification was sent")
    created_at: datetime = Field(..., description="When the notification was created")
    updated_at: datetime = Field(..., description="When the notification was last updated")
    translations: List[NotificationTranslationResponse] = Field(
        default_factory=list, description="Translations of this notification"
    )

    class Config:
        from_attributes = True


class NotificationSendResponse(BaseModel):
    """Schema for notification send response."""

    success: int = Field(..., description="Number of successful notifications")
    failure: int = Field(..., description="Number of failed notifications")
    error: Optional[str] = Field(None, description="Error message if any")


class NotificationSendToTopicRequest(BaseModel):
    """Schema for sending a notification to a topic."""

    notification_id: str = Field(..., description="Notification ID")
    base_topic: str = Field(..., description="Base topic name")


class DeviceTokenBase(BaseModel):
    """Base schema for device token data."""

    token: str = Field(..., description="Device token for push notifications")
    device_type: str = Field(..., description="Device type (android, ios, web)")
    preferred_language: Optional[LanguageEnum] = Field(None, description="User's preferred language for notifications")


class DeviceTokenCreate(DeviceTokenBase):
    """Schema for creating a device token."""

    pass


class DeviceTokenResponse(DeviceTokenBase):
    """Schema for device token response."""

    id: str = Field(..., description="Device token ID")
    user_id: Optional[str] = Field(None, description="User ID")
    created_at: datetime = Field(..., description="When the device token was created")
    updated_at: datetime = Field(..., description="When the device token was last updated")

    class Config:
        from_attributes = True


class TopicSubscriptionRequest(BaseModel):
    """Schema for topic subscription request."""

    tokens: List[str] = Field(..., description="Device tokens to subscribe/unsubscribe")
    topic: str = Field(..., description="Base topic name")


class TopicSubscriptionResponse(BaseModel):
    """Schema for topic subscription response."""

    success: int = Field(..., description="Number of successful subscriptions/unsubscriptions")
    failure: int = Field(..., description="Number of failed subscriptions/unsubscriptions")
    error: Optional[str] = Field(None, description="Error message if any")
