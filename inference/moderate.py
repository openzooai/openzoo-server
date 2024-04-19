# utils
import pprint
import requests

# OpenZoo
from inference.prompt_templates import format_moderation_prompt
from providers.together.config import get_together_client
from validation.chat import ChatCompletionResponse

class Moderator:
    def __init__(self):
        self.client = get_together_client()
    
    async def moderate(self, prompt):
        completion = self.client.completions.create(
            model= "Meta-Llama/Llama-Guard-7b",
            prompt= format_moderation_prompt('user', prompt),
            stream=False
        )

        return completion