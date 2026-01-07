from enum import Enum

class LLMEnums(Enum):
    OPENAI = "openai"
    COHERE = "cohere"

class OpenAIENUMs(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CohereENUMs(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"
    DOCUMENT = "search_document"
    QUERY = "search_query"


class DocumentTypeENUMs(Enum):
    DOCUMENT = "document"
    QUERY = "query"