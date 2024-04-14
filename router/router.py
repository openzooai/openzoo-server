# OS, utils
import json
import requests
import sseclient
from utils.utils import chat_completion_to_dict
import warnings
warnings.filterwarnings('ignore')


# Classifier
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, TensorDataset


# Providers
from providers.together.config import get_together_client, get_together_url, get_together_api_key
client = get_together_client()


# Models by task
from router.models import _select_model


class Router:
    def __init__(self):
        pass


    def generate(self,request):
        messages=request.messages
        task=request.model
        prompt = messages[-1].content
        
        # Select model
        model_name = self.select_model(prompt, task)
                
        response = client.chat.completions.create(
            messages=messages,
            model=model_name
        )

        return response
    

    async def generate_stream(self,request):
        url = get_together_url()
        api_key = get_together_api_key()
        prompt = request.messages[-1].content
        task = request.model
        model = self.select_model(prompt, task)

        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "repetition_penalty": 1,
            "stream_tokens": True,
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()

        client = sseclient.SSEClient(response)
        for event in client.events():
            if event.data == "[DONE]":
                yield "data: [DONE]\n\n"
                break

            partial_result = json.loads(event.data)
            yield f"data: {event.data}\n\n"


    def select_model(self, text, task):
        # If task is not specified, 
        if task is None:
            # Infer intent
            task_object = chat_completion_to_dict(self.predict_task(text))
            task = task_object['choices'][0]['message']['content'].strip()

        model_name = _select_model(text, task)

        return model_name

    
    def predict_task(self, input_text):
        task = client.chat.completions.create(
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

        return task