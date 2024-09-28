import os
import logging
import asyncio
from typing import Any, Callable

from PIL import Image
from PIL.Image import Image as ImageObject

from io import BytesIO

from aiogram import Bot
from aiogram.types import Message
from google.generativeai.protos import Blob


class Utils:
    """
    A utility class containing helper functions for file reading, error display,
    and media download within an Aiogram bot context.
    """

    work_path = os.path.dirname(os.path.realpath(__file__))

    @classmethod
    def read_file(cls, file_name: str, post_processor: Callable[[str], Any] = None) -> Any:
        """
        Read a file's content and optionally apply a post-processor function.

        Args:
        - file_name (str): Name of the file to read.
        - post_processor (Callable[[str], Any], optional): A function to process the content
        after reading (e.g., JSON loader). Defaults to None.

        Returns:
        - Any: The file content, processed or unprocessed.
        """
        with open(os.path.join(cls.work_path, file_name), 'r') as file:
            content = file.read()
            if post_processor:
                return post_processor(content)
            return content

    @classmethod
    async def error_display(cls, message: Message, error: str) -> None:
        """
        Display an error message to the user and delete it after 10 seconds.

        Args:
        - bot (Bot): The bot instance for messaging.
        - message (Message): The message where the error occurred.
        - error (str): The error message to display.
        """
        logging.error(error)
        error_msg = await message.reply(error)
        await asyncio.sleep(10)
        await error_msg.delete()

    @staticmethod
    async def download_media(bot: Bot, file_id: str, mime: str = None) -> ImageObject | BytesIO:
        """
        Download and process media from a given file ID. Handles both images and audio.

        Args:
        - bot (Bot): The bot instance for downloading the file.
        - file_id (str): The ID of the file to download.
        - mime (str): Custom mime for raw bytes. Defaults to None.

        Returns:
        - ImageObject | BytesIO: Returns an Image object for images or a BytesIO stream 
        for audio files.
        """
        file = await bot.get_file(file_id)
        file_data = await bot.download_file(file.file_path)

        image_stream = BytesIO(file_data.getvalue())

        if mime:
            return Blob(mime_type=mime, data=image_stream.getvalue())

        return Image.open(image_stream)
