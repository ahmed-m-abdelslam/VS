from stores.llm.LLMInterface import LLMInterface
from stores.llm.LLMEnums import OllamaENUMs
import ollama  # type: ignore
import logging


class OllamaProvider(LLMInterface):

    def __init__(
        self,
        api_key: str = None,  # مش مستخدم في Ollama
        api_url: str = None,
        default_input_max_characters: int = 1000,
        default_generation_output_max_tokens: int = 1000,
        default_generation_temperature: float = 0.1,
    ):
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_output_max_tokens = default_generation_output_max_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embeding_size = None

        self.logger = logging.getLogger(__name__)

        self.enums = OllamaENUMs

    # -------------------------
    # Config
    # -------------------------
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embeding_size = embedding_size

    # -------------------------
    # Utils
    # -------------------------
    def process_text(self, text: str):
        return text[: self.default_input_max_characters].strip()

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": self.process_text(prompt),
        }

    # -------------------------
    # Generation
    # -------------------------
    def generate_text(
        self,
        prompt: str,
        chat_history: list = None,
        max_output_tokens: int = None,
        temperature: float = None,
    ):
        if not self.generation_model_id:
            self.logger.error("Generation model ID is not set.")
            return None

        chat_history = chat_history or []

        max_output_tokens = (
            max_output_tokens
            if max_output_tokens
            else self.default_generation_output_max_tokens
        )
        temperature = (
            temperature
            if temperature is not None
            else self.default_generation_temperature
        )

        messages = chat_history + [
            self.construct_prompt(prompt, role=OllamaENUMs.USER)
        ]

        try:
            response = ollama.chat(
                model=self.generation_model_id,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_output_tokens,
                },
            )
        except Exception:
            self.logger.exception("Ollama generation failed.")
            return None

        return response["message"]["content"]

    # -------------------------
    # Embeddings
    # -------------------------
    def embed_text(self, text: str, document_type: str = None):
        if not self.embedding_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None

        try:
            response = ollama.embeddings(
                model=self.embedding_model_id,
                prompt=text,
            )
        except Exception:
            self.logger.exception("Ollama embedding failed.")
            return None

        return response["embedding"]
    

