# OS, utils
import json
import requests
import sseclient
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
            matches = self.predict_model(text)
            task = [key for key, value in matches.items() if value == 1][0]

        model_name = _select_model(text, task)

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