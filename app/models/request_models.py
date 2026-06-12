from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):

    role: Literal["user", "assistant"]
    content: str


class QuestionRequest(BaseModel):

    question: str
    chat_history: list[ChatMessage] = Field(default_factory=list)
