import uuid
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.core.exceptions import NotFoundError
from shared.src.core.logging import get_notification_logger
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.firebase_service import FirebaseService
from shared.src.tables import DeviceTokenTable, NotificationTable
from shared.src.tables.notification_table import NotificationTranslationTable

logger = get_notification_logger(__name__)


class NotificationService:
    """Service for handling notifications."""

    def __init__(self, db: AsyncSession, language: LanguageEnum = LanguageEnum.GERMAN):
        """Initialize the NotificationService with a database session."""
        self.db = db
        self.firebase_service = FirebaseService()
        self.language = language

    async def create_notification(
        self,
        title: str,
        body: str,
        image_url: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        base_topic: Optional[str] = None,
        language: LanguageEnum = None,
        translations: Optional[List[Dict[str, Any]]] = None,
    ) -> NotificationTable:
        """
        Create a new notification with translations.

        Args:
            title: Notification title in the default language
            body: Notification body in the default language
            image_url: URL of an image to include in the notification
            data: Additional data to send with the notification
            base_topic: Base topic name for localized topics
            language: Language for the default translation (defaults to service language)
            translations: Additional translations for the notification

        Returns:
            The created notification
        """

        # Use the provided language or fall back to the service language
        default_language = language or self.language

        notification = NotificationTable(
            id=uuid.uuid4(),
            image_url=image_url,
            data=data,
            base_topic=base_topic,
            is_sent=False,
        )

        # Add the default translation
        default_translation = NotificationTranslationTable(
            language=default_language.value,
            notification_id=notification.id,
            title=title,
            body=body,
        )

        self.db.add(notification)
        self.db.add(default_translation)

        # Add additional translations if provided
        if translations:
            for translation_data in translations:
                translation = NotificationTranslationTable(
                    language=translation_data["language"].value,
                    notification_id=notification.id,
                    title=translation_data["title"],
                    body=translation_data["body"],
                )
                self.db.add(translation)

        await self.db.commit()
        await self.db.refresh(notification)

        logger.info(f"Created notification: {notification.id} with translations")
        return notification

    async def get_notification(self, notification_id: str) -> NotificationTable:
        """
        Get a notification by ID.

        Args:
            notification_id: Notification ID

        Returns:
            The notification

        Raises:
            NotFoundError: If the notification is not found
        """
        stmt = select(NotificationTable).where(NotificationTable.id == notification_id)
        result = await self.db.execute(stmt)
        notification = result.scalar_one_or_none()

        if not notification:
            raise NotFoundError(
                detail="Notification not found",
                extra={"notification_id": notification_id},
            )

        return notification

    async def get_notifications(
        self, limit: int = 100, offset: int = 0, notification_id: str | None = None
    ) -> List[Dict]:
        """
        Get all notifications with their translations.

        Args:
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip
            notification_id: Optional notification ID to filter by

        Returns:
            List of notifications with translations
        """
        stmt = (
            select(NotificationTable)
            .order_by(NotificationTable.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if notification_id:
            stmt = stmt.where(NotificationTable.id == notification_id)
            result = await self.db.execute(stmt)
            notification = result.scalar_one_or_none()
            if notification:
                return [
                    await self.get_notification_with_translations(str(notification.id))
                ]
            return []

        result = await self.db.execute(stmt)
        notifications = result.scalars().all()

        # Get translations for all notifications
        notification_responses = []
        for notification in notifications:
            notification_responses.append(
                await self.get_notification_with_translations(str(notification.id))
            )

        return notification_responses

    async def send_notification(self, notification_id: str) -> Dict:
        """
        Send a notification to all registered devices respecting their language preferences.

        Args:
            notification_id: Notification ID

        Returns:
            Dict containing success and failure counts

        Raises:
            NotFoundError: If the notification is not found
        """
        notification = await self.get_notification(notification_id)

        # Get all translations for this notification
        stmt = select(NotificationTranslationTable).where(
            NotificationTranslationTable.notification_id == notification_id
        )
        result = await self.db.execute(stmt)
        translations = result.scalars().all()

        if not translations:
            raise NotFoundError(
                detail="No translations found for notification",
                extra={"notification_id": notification_id},
            )

        # Create a mapping of language to translation
        translation_map = {trans.language: trans for trans in translations}

        # If notification has a topic or base_topic, send to that topic with the default language
        if notification.topic or notification.topic:
            # Use base_topic if available, otherwise use the deprecated topic field
            topic_name = notification.topic or notification.topic

            # Try to get translation in service language
            default_translation = translation_map.get(
                self.language.value,
                next(
                    iter(translation_map.values())
                ),  # First available if service language not found
            )

            # If using base_topic, create a localized topic name
            if notification.topic:
                topic_name = f"{topic_name}_{self.language.value}"

            result = self.firebase_service.send_notification(
                tokens=None,
                title=default_translation.title,
                body=default_translation.body,
                data=notification.data,
                topic=topic_name,
                image_url=notification.image_url,
            )
        else:
            # Get all device tokens with their preferred language
            stmt = select(DeviceTokenTable)
            result_tokens = await self.db.execute(stmt)
            device_tokens = result_tokens.scalars().all()

            if not device_tokens:
                logger.warning("No device tokens found for sending notification")
                return {"success": 0, "failure": 0, "error": "No device tokens found"}

            # Group tokens by preferred language
            tokens_by_language = {}
            default_language_tokens = []

            for token in device_tokens:
                if token.language and token.language in translation_map:
                    if token.language not in tokens_by_language:
                        tokens_by_language[token.language] = []
                    tokens_by_language[token.language].append(token.token)
                else:
                    default_language_tokens.append(token.token)

            # Send notifications to each language group
            success_count = 0
            failure_count = 0

            # Send to language-specific groups
            for language, tokens in tokens_by_language.items():
                translation = translation_map[language]
                result = self.firebase_service.send_notification(
                    tokens=tokens,
                    title=translation.title,
                    body=translation.body,
                    data=notification.data,
                    image_url=notification.image_url,
                )
                success_count += result.get("success", 0)
                failure_count += result.get("failure", 0)

            # Send to default language group using service language or first available
            if default_language_tokens:
                # Try to get translation in service language
                default_translation = translation_map.get(
                    self.language.value,
                    next(
                        iter(translation_map.values())
                    ),  # First available if service language not found
                )

                result = self.firebase_service.send_notification(
                    tokens=default_language_tokens,
                    title=default_translation.title,
                    body=default_translation.body,
                    data=notification.data,
                    image_url=notification.image_url,
                )
                success_count += result.get("success", 0)
                failure_count += result.get("failure", 0)

            result = {"success": success_count, "failure": failure_count}

        # Update notification status
        stmt = (
            update(NotificationTable)
            .where(NotificationTable.id == notification_id)
            .values(is_sent=True, sent_at=func.now())
        )
        await self.db.execute(stmt)
        await self.db.commit()

        logger.info(f"Sent notification: {notification_id}, result: {result}")
        return result

    async def register_device_token(
        self,
        token: str,
        device_type: str,
        user_id: Optional[str] = None,
        language: Optional[LanguageEnum] = None,
    ) -> DeviceTokenTable:
        """
        Register a device token for push notifications.

        Args:
            token: Device token
            device_type: Device type (android, ios, web)
            user_id: User ID
            language: User's preferred language for notifications

        Returns:
            The created device token
        """
        # Check if token already exists
        stmt = select(DeviceTokenTable).where(DeviceTokenTable.token == token)
        result = await self.db.execute(stmt)
        existing_token = result.scalar_one_or_none()

        language_value = language.value if language else None

        if existing_token:
            # Update existing token
            existing_token.device_type = device_type
            existing_token.user_id = user_id
            existing_token.language = language_value
            await self.db.commit()
            await self.db.refresh(existing_token)
            logger.info(f"Updated device token: {existing_token.id}")
            return existing_token

        # Create new token
        device_token = DeviceTokenTable(
            id=str(uuid.uuid4()),
            token=token,
            device_type=device_type,
            user_id=user_id,
            preferred_language=language_value,
        )

        self.db.add(device_token)
        await self.db.commit()
        await self.db.refresh(device_token)

        logger.info(f"Registered device token: {device_token.id}")
        return device_token

    async def get_device_tokens(
        self, user_id: Optional[str] = None
    ) -> List[DeviceTokenTable]:
        """
        Get device tokens.

        Args:
            user_id: User ID to filter by

        Returns:
            List of device tokens
        """
        if user_id:
            stmt = select(DeviceTokenTable).where(DeviceTokenTable.user_id == user_id)
        else:
            stmt = select(DeviceTokenTable)

        result = await self.db.execute(stmt)
        device_tokens = result.scalars().all()

        return list(device_tokens)

    async def subscribe_to_topic(
        self, tokens: List[str], base_topic: str, language: LanguageEnum = None
    ) -> Dict:
        """
        Subscribe device tokens to a language-specific topic.

        Args:
            tokens: Device tokens to subscribe
            base_topic: Base topic name
            language: Language for the topic (defaults to service language)

        Returns:
            Dict containing success and failure counts
        """
        # Use the provided language or fall back to the service language
        topic_language = language or self.language

        # Create the localized topic name
        localized_topic = f"{base_topic}_{topic_language.value}"

        result = self.firebase_service.subscribe_to_topic(tokens, localized_topic)
        logger.info(f"Subscribed to topic: {localized_topic}, result: {result}")
        return result

    async def unsubscribe_from_topic(
        self, tokens: List[str], base_topic: str, language: LanguageEnum = None
    ) -> Dict:
        """
        Unsubscribe device tokens from a language-specific topic.

        Args:
            tokens: Device tokens to unsubscribe
            base_topic: Base topic name
            language: Language for the topic (defaults to service language)

        Returns:
            Dict containing success and failure counts
        """
        # Use the provided language or fall back to the service language
        topic_language = language or self.language

        # Create the localized topic name
        localized_topic = f"{base_topic}_{topic_language.value}"

        result = self.firebase_service.unsubscribe_from_topic(tokens, localized_topic)
        logger.info(f"Unsubscribed from topic: {localized_topic}, result: {result}")
        return result

    async def get_notification_with_translations(self, notification_id: str) -> Dict:
        """
        Get a notification by ID with all its translations.

        Args:
            notification_id: Notification ID

        Returns:
            The notification with translations

        Raises:
            NotFoundError: If the notification is not found
        """
        # Get the notification
        notification = await self.get_notification(notification_id)

        # Get all translations for this notification
        stmt = select(NotificationTranslationTable).where(
            NotificationTranslationTable.notification_id == notification_id
        )
        result = await self.db.execute(stmt)
        translations = result.scalars().all()

        # Convert to response format
        notification_dict = {
            "id": str(notification.id),
            "image_url": notification.image_url,
            "data": notification.data,
            "topic": notification.topic,  # Kept for backward compatibility
            "base_topic": notification.topic,
            "is_sent": notification.is_sent,
            "sent_at": notification.sent_at,
            "created_at": notification.created_at,
            "updated_at": notification.updated_at,
            "translations": [
                {
                    "language": trans.language,
                    "title": trans.title,
                    "body": trans.body,
                    "notification_id": str(trans.notification_id),
                    "created_at": trans.created_at,
                    "updated_at": trans.updated_at,
                }
                for trans in translations
            ],
        }

        return notification_dict

    async def send_notification_to_topic(
        self,
        notification_id: str,
        base_topic: str,
        language: Optional[LanguageEnum] = None,
    ) -> Dict:
        """
        Send a notification to a language-specific topic.

        Args:
            notification_id: Notification ID
            base_topic: Base topic name
            language: Language for the topic (defaults to service language)

        Returns:
            Dict containing success and failure counts

        Raises:
            NotFoundError: If the notification is not found
        """
        notification = await self.get_notification(notification_id)

        # Use the provided language or fall back to the service language
        topic_language = language or self.language

        # Create the localized topic name
        localized_topic = f"{base_topic}_{topic_language.value}"

        # Get the translation for the specified language
        stmt = select(NotificationTranslationTable).where(
            NotificationTranslationTable.notification_id == notification_id,
            NotificationTranslationTable.language == topic_language.value,
        )
        result = await self.db.execute(stmt)
        translation = result.scalar_one_or_none()

        # If no translation in the specified language, get the first available translation
        if not translation:
            stmt = select(NotificationTranslationTable).where(
                NotificationTranslationTable.notification_id == notification_id
            )
            result = await self.db.execute(stmt)
            translation = result.scalar_one_or_none()

            if not translation:
                raise NotFoundError(
                    detail="No translations found for notification",
                    extra={"notification_id": notification_id},
                )

        # Send the notification to the localized topic
        result = self.firebase_service.send_notification(
            tokens=None,
            title=translation.title,
            body=translation.body,
            data=notification.data,
            topic=localized_topic,
            image_url=notification.image_url,
        )

        # Update notification status
        stmt = (
            update(NotificationTable)
            .where(NotificationTable.id == notification_id)
            .values(is_sent=True, sent_at=func.now())
        )
        await self.db.execute(stmt)
        await self.db.commit()

        logger.info(
            f"Sent notification: {notification_id} to topic: {localized_topic}, result: {result}"
        )
        return result
