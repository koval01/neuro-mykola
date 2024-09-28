import asyncio
import logging
import sys

from aiogram import F, Bot, Dispatcher
from aiogram.types import Message

from application.llm.llm import LLM
from application.utils import Utils
from application.utils import settings


WORK_CHAT_ID = settings.WORK_CHAT_ID

# Initialize bot and dispatcher
dp = Dispatcher()
bot = Bot(token=settings.BOT_API_KEY)
llm = LLM(bot)


@dp.message((F.content_type.in_({'text', 'dice'})) & (F.chat.id == WORK_CHAT_ID))
async def text_handler(message: Message) -> None:
    """
    Handles text and dice messages from the specified WORK_CHAT_ID.
    """
    await llm.response_process(message=message)


@dp.message((F.content_type.in_({'photo', 'sticker', 'voice', 'audio'})) & (F.chat.id == WORK_CHAT_ID))
async def media_handler(message: Message) -> None:
    """
    Handles media messages (photo, sticker, voice) from the specified WORK_CHAT_ID.
    Downloads the media and processes the LLM response.
    """
    try:
        # Extract media from the message based on its content type
        media = getattr(message, message.content_type, None)
        if isinstance(media, list):
            media = media[-1]  # Get the last item in the list if it's a list

        file_id = media.file_id

        # Download media (special handling for voice messages as audio)
        media_file = await Utils.download_media(
            bot,
            file_id,
            mime= \
                "audio/ogg" if message.content_type == "voice" else \
                message.audio.mime_type if message.content_type == "audio" \
                else None
        )

    except Exception as e:
        # Handle errors in downloading media or processing
        await Utils.error_display(message, str(e))
        return None

    # Process the LLM response with the downloaded media as input
    await llm.response_process(message=message, additional_input=(media_file,))


async def main() -> None:
    """
    Entry point of the bot. Starts polling messages from Telegram.
    """
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Set up logging to display info level logs to the console
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Run the main event loop
    asyncio.run(main())
