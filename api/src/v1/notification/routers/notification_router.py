from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.core.api_key import APIKey
from api.src.v1.core.language import get_language
from shared.src.core.database import get_async_db
from shared.src.core.exceptions import NotFoundError
from shared.src.core.logging import get_notification_logger
from shared.src.enums.language_enums import LanguageEnum
from shared.src.tables.user_table import UserTable

from ..schemas.notification_schema import (
    DeviceTokenCreate,
    DeviceTokenResponse,
    NotificationCreate,
    NotificationResponse,
    NotificationSendResponse,
    NotificationSendToTopicRequest,
    TopicSubscriptionRequest,
    TopicSubscriptionResponse,
)
from ..services.notification_service import NotificationService

router = APIRouter()
logger = get_notification_logger(__name__)


@router.post(
    "",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new notification",
    description="Create a new notification to be sent to users with optional translations.",
)
async def create_notification(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_async_db),
    authorized: bool = Depends(APIKey.verify_admin_api_key),
):
    """Create a new notification with optional translations."""
    service = NotificationService(db)

    # Extract translations if provided
    translations = None
    if notification.translations:
        translations = [
            {"language": trans.language, "title": trans.title, "body": trans.body}
            for trans in notification.translations
        ]

    result = await service.create_notification(
        title=notification.title,
        body=notification.body,
        image_url=notification.image_url,
        data=notification.data,
        base_topic=notification.base_topic,
        language=notification.language,
        translations=translations,
    )

    # Fetch the notification with translations to return
    return await service.get_notification_with_translations(result.id)


@router.get(
    "",
    response_model=List[NotificationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get notifications",
)
async def get_notifications(
    notification_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_async_db),
):
    """Get all notifications."""
    service = NotificationService(db)
    result = await service.get_notifications(limit=limit, offset=offset, notification_id=notification_id)
    return result


@router.post(
    "/send",
    response_model=NotificationSendResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a notification",
    description="Send a notification to all registered devices respecting their language preferences.",
)
async def send_notification(
    notification_id: str = Query(None),
    db: AsyncSession = Depends(get_async_db),
    authorized: bool = Depends(APIKey.verify_admin_api_key),
):
    """Send a notification to all registered devices respecting their language preferences."""
    service = NotificationService(db)
    try:
        result = await service.send_notification(notification_id)
        return result
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/send/topic",
    response_model=NotificationSendResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a notification to a topic",
    description="Send a notification to a language-specific topic.",
)
async def send_notification_to_topic(
    request: NotificationSendToTopicRequest,
    db: AsyncSession = Depends(get_async_db),
    language: LanguageEnum = Depends(get_language),
    authorized: bool = Depends(APIKey.verify_admin_api_key),
):
    """Send a notification to a language-specific topic."""
    service = NotificationService(db)
    try:
        result = await service.send_notification_to_topic(
            notification_id=request.notification_id,
            base_topic=request.base_topic,
            language=language.value,
        )
        return result
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/device-token",
    response_model=DeviceTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a device token",
    description="Register a device token for push notifications with language preference.",
)
async def register_device_token(
    device_token: DeviceTokenCreate,
    user: UserTable = Depends(APIKey.verify_user_api_key),
    language: LanguageEnum = Depends(get_language),
    db: AsyncSession = Depends(get_async_db),
):
    """Register a device token for push notifications with language preference."""
    service = NotificationService(db)
    result = await service.register_device_token(
        token=device_token.token,
        device_type=device_token.device_type,
        user_id=user.id,
        language=language.value,
    )
    return result


@router.post(
    "/topics/subscribe",
    response_model=TopicSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Subscribe to a topic",
    description="Subscribe device tokens to a language-specific topic for targeted notifications.",
)
async def subscribe_to_topic(
    subscription: TopicSubscriptionRequest,
    user: UserTable = Depends(APIKey.verify_user_api_key),
    language: LanguageEnum = Depends(get_language),
    db: AsyncSession = Depends(get_async_db),
):
    """Subscribe device tokens to a language-specific topic."""
    service = NotificationService(db)
    result = await service.subscribe_to_topic(
        tokens=subscription.tokens,
        base_topic=subscription.topic,
        language=language.value,
    )
    return result


@router.post(
    "/topics/unsubscribe",
    response_model=TopicSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Unsubscribe from a topic",
    description="Unsubscribe device tokens from a language-specific topic.",
)
async def unsubscribe_from_topic(
    subscription: TopicSubscriptionRequest,
    user: UserTable = Depends(APIKey.verify_user_api_key),
    language: LanguageEnum = Depends(get_language),
    db: AsyncSession = Depends(get_async_db),
):
    """Unsubscribe device tokens from a language-specific topic."""
    service = NotificationService(db)
    result = await service.unsubscribe_from_topic(
        tokens=subscription.tokens,
        base_topic=subscription.topic,
        language=language.value,
    )
    return result
