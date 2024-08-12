# New model for creating a message with only required fields
from pydantic import BaseModel


class MessageCreate(BaseModel):
    chat_id: str  # The ID of the chat in which the message is sent
    sender_id: int  # The ID of the sender
    content: str  # The content of the message
    recipient_id: int
    