from langchain_community.llms import Ollama 

class LocalLLM:
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name

    def get_llm(self):
        return Ollama(model = self.model_name)


    
    