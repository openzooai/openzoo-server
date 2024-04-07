# Classifier
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, TensorDataset


# OS, utils
import os
import time
import asyncio
import json
import requests
import sseclient
import warnings
warnings.filterwarnings('ignore')
import dotenv
dotenv.load_dotenv()


# OpenAI for Together
from openai import OpenAI

TOGETHER_URL = os.environ.get("TOGETHER_URL")
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
client = OpenAI(
  api_key=TOGETHER_API_KEY,
  base_url='https://api.together.xyz/v1',
)


MODELS = {
    'chat': "meta-llama/Llama-2-7b-chat-hf",
    'summarization': "meta-llama/Llama-2-7b-chat-hf",
    'math': "meta-llama/Llama-2-13b-chat-hf",
    'text_to_sql': "meta-llama/Llama-2-13b-chat-hf"
}


class Router:
    def __init__(self):
        self.model_name = "models/intent_classifier"
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        self.Bert_Tokenizer = BertTokenizer.from_pretrained(self.model_name)
        self.Bert_Model = BertForSequenceClassification.from_pretrained(self.model_name).to(self.device)
        self.chat_llm = None
        self.summarization_llm = None
        self.math_llm = None
        self.texttosql_llm = None


    def generate(self,request):
        messages=request.messages
        task=request.model
        text = messages[-1].content
        
        # Select model
        model_name = self.select_model(text, task)
                
        response = client.chat.completions.create(
            messages=messages,
            model=model_name
        )

        return response
    

    async def generate_stream(self,request):
        url = TOGETHER_URL
        model = request.model
        prompt = request.messages[-1].content

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
            "Authorization": f"Bearer {os.environ['TOGETHER_API_KEY']}",
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
        
        # If task is specified, 
        if task is not None:
            # Check if query type is in MODELS keys
            if task not in MODELS.keys(): raise ValueError(f"Task {task} not found in MODELS keys")

            query_type = task
        else:
            # Infer intent
            matches = self.predict_model(text)
            print(matches)
            query_type = [key for key, value in matches.items() if value == 1][0]

        # Select model
        model_name = MODELS[query_type]

        return model_name
    

    def predict_model(self, input_text):
        model=self.Bert_Model
        tokenizer=self.Bert_Tokenizer
        device=self.device

        user_input = [input_text]

        user_encodings = tokenizer(
            user_input, truncation=True, padding=True, return_tensors="pt")

        user_dataset = TensorDataset(
            user_encodings['input_ids'], user_encodings['attention_mask'])

        user_loader = DataLoader(user_dataset, batch_size=1, shuffle=False)

        model.eval()
        with torch.no_grad():
            for batch in user_loader:
                input_ids, attention_mask = [t.to(device) for t in batch]
                outputs = model(input_ids, attention_mask=attention_mask)
                logits = outputs.logits
                predictions = torch.sigmoid(logits)

        predicted_labels = (predictions.cpu().numpy() > 0.5).astype(int)
        labels_list = ['chat', 'summarization', 'math', 'text_to_sql']
        result = dict(zip(labels_list, predicted_labels[0]))
        return result


def flatten_dicts_to_string(dict_list):
    """
    Flattens a list of dictionaries into a string, assuming all values are strings.
    
    :param dict_list: List of dictionaries to be flattened.
    :return: A single string representation of all dictionaries.
    """
    # Flatten each dictionary into a list of 'key: value' strings
    flattened_list = [f"{key}: {value}" for d in dict_list for key, value in d.items()]
    
    # Join the list into a single string, separated by ', '
    flattened_string = ', '.join(flattened_list)
    
    return flattened_string