from typing import Optional, List
from aiogram.types import (
    Audio, Contact, DateTime, Dice, Document, Location,
    PhotoSize, Poll, Sticker, Video, VideoNote, Voice,
    MessageOriginUser, MessageOriginHiddenUser, MessageOriginChat, MessageOriginChannel
)

from pydantic import BaseModel


class Chat(BaseModel):
    """
    Represents a Telegram chat.
    """
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class User(BaseModel):
    """
    Represents a Telegram user or bot.
    """
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None


class Message(BaseModel):
    """
    Represents a message in a Telegram chat.
    """
    message_id: int
    date: DateTime
    chat: Chat
    message_thread_id: Optional[int] = None
    from_user: Optional[User] = None
    reply_to_message: Optional["Message"] = None
    forward_origin: MessageOriginUser | MessageOriginHiddenUser | MessageOriginChat | MessageOriginChannel | None
    text: Optional[str] = None
    audio: Optional[Audio] = None
    # document: Optional[Document] = None
    photo: Optional[List[PhotoSize]] = None
    sticker: Optional[Sticker] = None
    # video: Optional[Video] = None
    # video_note: Optional[VideoNote] = None
    voice: Optional[Voice] = None
    caption: Optional[str] = None
    # contact: Optional[Contact] = None
    dice: Optional[Dice] = None
    # poll: Optional[Poll] = None
    # location: Optional[Location] = None


class ResponseLLM(BaseModel):
    """
    Represents the response from an LLM (Language Learning Model) in a structured format.
    """
    reply_to: Optional[int] = None
    text: Optional[str] = None
    skip: bool
