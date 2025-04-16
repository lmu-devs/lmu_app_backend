from typing import List, Optional

import telegram
from telegram.error import TelegramError

from shared.src.core.logging import get_main_logger
from shared.src.core.settings import get_settings

logger = get_main_logger(__name__)


class TelegramService:
    def __init__(self):
        self.settings = get_settings()
        self.bot = telegram.Bot(token=self.settings.TELEGRAM_BOT_TOKEN)
        self.chat_id = self.settings.TELEGRAM_CHAT_ID

    async def send_feedback_notification(
        self,
        feedback_type: str,
        rating: str,
        screen: str,
        message: Optional[str] = None,
        tags: Optional[List[str]] = None,
        app_version: Optional[str] = None,
        system_version: Optional[str] = None,
    ):
        try:
            emoji = self._get_rating_emoji(rating)
            tag_text = f"\nTags: {', '.join(tags)}" if tags else ""
            message_text = f"\nMessage: {message}" if message else ""

            text = (
                f"✉️ New {feedback_type} Feedback ✉️\n\n"
                f"Rated {emoji} on {screen}"
                f"{message_text}"
                f"{tag_text}\n"
                f"App-Version: {app_version} on {system_version}"
            )

            await self.bot.send_message(chat_id=self.chat_id, text=text, parse_mode="HTML")
        except TelegramError as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")

    def _get_rating_emoji(self, rating: str) -> str:
        return {"GOOD": "🥳", "NEUTRAL": "😄", "BAD": "😕"}.get(rating, "❓")
