from enum import Enum

class LLMEnums(Enum):
    OPENAI = "openai"
    COHERE = "cohere"

class OpenAIENUMs(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"