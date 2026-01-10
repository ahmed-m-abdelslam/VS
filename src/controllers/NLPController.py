from .BaseController import BaseController

class NLPController(BaseController):
    def __init__(self , vector_db_client, generation_client,embedding_client):
        super().__init__()  

        self.vector_db_client = vector_db_client
        self.generation_client = generation_client  
        self.embedding_client = embedding_client
