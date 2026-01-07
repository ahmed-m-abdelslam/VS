from stores.LLMInterface import LLMInterface
from stores.LLMEnums import CohereENUMs
import cohere # type: ignore
import logging

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str ,
                 default_input_max_characters: int = 1000,
                 default_generation_output_max_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):
        
        self.api_key = api_key
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_output_max_tokens = default_generation_output_max_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None
        self.embeding_size = None

        self.client = cohere.Client(
            api_key=self.api_key
            )
        
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str) :
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str , embedding_size: int) :
        self.embedding_model_id = model_id
        self.embeding_size = embedding_size

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()
    

    def generate_text(self, prompt: str, chat_history : list= [], max_output_tokens: int = None, temperature: float=None) :
        
        if not self.client:
            self.logger.error("Cohere client is not initialized.")
            return None
        if not self.generation_model_id:
            self.logger.error("Embedding model ID is not set.")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens  else self.default_generation_output_max_tokens
        temperature = temperature if temperature  else self.default_generation_temperature

        chat_history.append(self.construct_prompt(prompt=prompt, role=CohereENUMs.USER.value))

        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message=self.process_text(prompt),
            max_tokens=max_output_tokens,
            temperature=temperature
        )

    
    def construct_prompt(self, prompt: str, role: str) :
        return {
            "role": role,
            "text": self.process_text(prompt)
        }

        
    


