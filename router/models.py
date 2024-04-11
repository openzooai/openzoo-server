# Models by task
MODELS = {
    'chat': "mistralai/Mixtral-8x7B-Instruct-v0.1",
    'summarization': "meta-llama/Llama-2-7b-chat-hf",
    'math': "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
    'text_to_sql': "deepseek-ai/deepseek-coder-33b-instruct",
    'mistralai/Mixtral-8x7B-Instruct-v0.1': "mistralai/Mixtral-8x7B-Instruct-v0.1",
}


def _select_model(text, task):
    if task in MODELS.keys():
        return MODELS[task]
    else:
        raise ValueError(f"Task {task} not found in MODELS keys")