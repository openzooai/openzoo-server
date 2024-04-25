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
        url = self.url + "/completions"
        spec=request.model
        prompt = request.prompt
        model = self.select_model(prompt, spec)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": 200,
            "stop": ["<s>", "\n"],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.1
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        print(payload)

        response = requests.post(self.url, json=payload, headers=headers)

        return response.text
    

    async def generate_completion_stream(self,request):
        url = self.url + "/completions"
        prompt = request.prompt
        spec = request.model
        model = self.select_model(prompt, spec)

        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": 128,
            "stop": ["<s>", "\n"],
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "stream_tokens": True,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(self.url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data == "[DONE]":
                yield "data: [DONE]"
                break

            partial_result = json.loads(event.data)
            yield f"data: {event.data}"


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
        spec = client.chat.completions.create(
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