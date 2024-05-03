# OS, utils
import json
import requests
import sseclient
from utils.utils import chat_completion_to_dict
import warnings
warnings.filterwarnings('ignore')
from starlette.responses import StreamingResponse


# Providers
from providers.together.config import get_together_client, get_together_url, get_together_api_key


# Models by task
from inference.models import best_fit_model_for_spec


class InferenceEngine:
    def __init__(self):
        self.url = get_together_url()
        self.api_key = get_together_api_key()
        self.client = get_together_client()


    def generate_completion(self,request):
        spec=request.model
        prompt = request.prompt

        # Select model
        model = self.select_model(prompt, spec)

        # Replace model in request
        request.model = model
        
        response = self.client.completions.create(**request.dict())

        return response
    

    async def generate_completion_stream(self,request):
        prompt = request.prompt
        spec = request.model
        model = self.select_model(prompt, spec)
        request.model = model

        stream = self.client.completions.create(**request.dict())

        for chunk in stream:
            data = json.dumps(chunk.dict())
            if data == "[DONE]":
                yield "data: [DONE]\n\n"
                break

            yield f"data: {data}\n\n"


    def generate_chat_completion(self,request):
        messages=request.messages
        spec=request.model
        prompt = messages[-1].content
        
        # Select model
        model_name = self.select_model(prompt, spec)

        # Replace model_name in request
        request.model = model_name
                
        response = self.client.chat.completions.create(**request.dict())

        return response
    

    async def generate_chat_completion_stream(self,request):
        prompt = request.messages[-1].content
        spec = request.model
        model = self.select_model(prompt, spec)
        request.model = model

        stream = self.client.chat.completions.create(**request.dict())

        for chunk in stream:
            data = json.dumps(chunk.dict())
            if data == "[DONE]":
                yield "data: [DONE]\n\n"
                break

            yield f"data: {data}\n\n"

    
    async def generate_embeddings(self, input, model):

        response = self.client.embeddings.create(input=input, model=model)

        return response


    def select_model(self, text, spec):
        # If task is not specified, 
        if spec == "":
            # Infer intent
            spec_object = chat_completion_to_dict(self.predict_task(text))
            spec = spec_object['choices'][0]['message']['content'].strip()
            print(spec)

        model_name = best_fit_model_for_spec(spec.split())

        return model_name

    
    def predict_task(self, input_text):
        spec = self.client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": f"""
        You are a prompt intent classifier. Classify the following prompt according to one of these categories:
                    
        - chat
        - code
        - summarization
        - text_to_sql
        - math
        - translation
                    
        Classify the following prompt:
                    
        ---               
        {input_text}
        ---
                    
        Return only the class selected from above and nothing else.
        """}],
            stream=False,
        )

        return spec