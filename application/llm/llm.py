import json
import logging
from typing import Type, Any

from pydantic import ValidationError, BaseModel

from aiogram.types import Message
from aiogram import Bot

from application.models.message import Message as LLMMessage

import google.generativeai as genai
from google.generativeai.types import (
    HarmBlockThreshold, HarmCategory, BlockedPromptException,
    StopCandidateException
)

from application.utils.config import settings
from application.utils.utils import Utils
from application.models.message import ResponseLLM


class LLM:
    """
    A class to interact with Google's Generative AI for LLM-based conversations
    within an Aiogram bot context.

    Attributes:
    - API_KEY (str): API key for authenticating Google Generative AI.
    - bot (Bot): Instance of the bot for sending messages and errors.
    - chat_session (GenerativeModel.ChatSession): Active chat session with LLM.
    """

    API_KEY: str = settings.GEMINI_API_KEY

    def __init__(self, bot: Bot) -> None:
        """
        Initialize the LLM instance with the bot and configure the generative model.
        
        Args:
        - bot (Bot): The bot instance to handle messaging.
        """
        self.bot: Bot = bot

        # Load system prompt and generation configuration from external files
        sys_prompt = Utils.read_file("../prompts/sys_prompt.txt")
        generation_config = Utils.read_file("generation_config.json", json.loads)

        # Configure the generative AI model with custom settings
        genai.configure(api_key=self.API_KEY)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=sys_prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        self.session = model.start_chat()

    @staticmethod
    def prepare_data(message: Message, model: Type[BaseModel]) -> str:
        """
        Prepare and serialize the message data into JSON format suitable for LLM input.

        Args:
        - message (Message): The incoming message to be processed.
        - model (BaseModel): Pydantic BaseModel for data validation and serialization.

        Returns:
        - str: The serialized message data in JSON format.
        """
        return model(**message.model_dump()).model_dump_json()

    @staticmethod
    async def prepare_response(message: Message, response_llm: str) -> ResponseLLM | None:
        """
        Parse and validate the LLM's response. Handle potential JSON errors and
        model validation issues.

        Args:
        - message (Message): The original message triggering the response.
        - response_llm (str): The raw response received from LLM.

        Returns:
        - ResponseLLM | None: A validated ResponseLLM instance or None if there's an error.
        """
        clear_string = response_llm.replace("```json", "").replace("```", "")
        try:
            _json = json.loads(clear_string)
        except json.decoder.JSONDecodeError as e:
            await Utils.error_display(message, f"Error parsing JSON response from LLM. Details: {e}")
            return None

        try:
            return ResponseLLM(**_json)
        except ValidationError as e:
            await Utils.error_display(message, f"Error validating JSON response from LLM. Details: {e}")
            return None

    async def response_process(self, message: Message, additional_input: tuple[Any] = None) -> dict | None:
        """
        Handle the entire flow from preparing the input, sending it to the LLM,
        and processing the response.

        Args:
        - message (Message): The message that triggered the process.
        - additional_input (ContentType | list): Optional additional input for LLM.

        Returns:
        - dict | None: The final processed response as a dictionary or None in case of errors.
        """
        if additional_input is None:
            additional_input: tuple = ()

        input_data = self.prepare_data(message, LLMMessage)

        try:
            response = await self.session.send_message_async((input_data, *additional_input,))
        except (StopCandidateException, BlockedPromptException) as e:
            await Utils.error_display(message, f"Error LLM: {e}")
            return None

        finish_resp = await self.prepare_response(message, response.text)
        logging.info(finish_resp)

        if not finish_resp or finish_resp.skip:
            return None

        # Send the LLM response to the user
        await message.answer(finish_resp.text, reply_to_message_id=finish_resp.reply_to)
        return finish_resp
