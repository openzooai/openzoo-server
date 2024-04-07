# Models by task
MODELS = {
    'chat': "meta-llama/Llama-2-7b-chat-hf",
    'summarization': "meta-llama/Llama-2-7b-chat-hf",
    'math': "meta-llama/Llama-2-13b-chat-hf",
    'text_to_sql': "meta-llama/Llama-2-13b-chat-hf"
}


def _select_model(text, task):
    if task in MODELS.keys():
        return MODELS[task]
    else:
        raise ValueError(f"Task {task} not found in MODELS keys")