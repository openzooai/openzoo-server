# Models by task
MODELS = {
    'chat': ["databricks/dbrx-instruct",
             "microsoft/WizardLM-2-8x22B",
             "mistralai/Mixtral-8x22B-Instruct-v0.1",
             "meta-llama/Llama-3-70b-chat-hf",
             "mistralai/Mixtral-8x7B-Instruct-v0.1", 
             "meta-llama/Llama-3-8b-chat-hf",
             "google/gemma-2b-it"],

    'code': ["databricks/dbrx-instruct",
             "codellama/CodeLlama-70b-Instruct-hf",
             "codellama/CodeLlama-34b-Instruct-hf",
             "codellama/CodeLlama-7b-Instruct-hf",],

    'summarization': ["mistralai/Mixtral-8x7B-Instruct-v0.1",
                      "meta-llama/Llama-3-8b-chat-hf",
                      "google/gemma-2b-it",
                      "microsoft/phi-2"],

    'math': ["databricks/dbrx-instruct",
             "meta-llama/Llama-3-70b-chat-hf",
             "mistralai/Mixtral-8x7B-Instruct-v0.1",
             "meta-llama/Llama-3-8b-chat-hf",
             "google/gemma-2b-it"],

    'XL': ["databricks/dbrx-instruct",
           "microsoft/WizardLM-2-8x22B",
           "mistralai/Mixtral-8x22B-Instruct-v0.1",],

    'L': ["meta-llama/Llama-3-70b-chat-hf",
          "codellama/CodeLlama-70b-Instruct-hf"],

    'M': ["mistralai/Mixtral-8x7B-Instruct-v0.1",
          "codellama/CodeLlama-34b-Instruct-hf"],

    'S': ["mistralai/Mistral-7B-Instruct-v0.2",
          "codellama/CodeLlama-7b-Instruct-hf",
          "meta-llama/Llama-2-7b-chat-hf",
          "meta-llama/Llama-3-8b-chat-hf"],

    'XS': ["google/gemma-2b-it",
           "microsoft/phi-2"],

    'XL-context': ["microsoft/WizardLM-2-8x22B",
                   "mistralai/Mixtral-8x22B-Instruct-v0.1",],

    'L-context': ["databricks/dbrx-instruct",
                  "mistralai/Mistral-7B-Instruct-v0.2",
                  "mistralai/Mixtral-8x7B-Instruct-v0.1"],
    
    'M-context': ["codellama/CodeLlama-34b-Instruct-hf",
                  "codellama/CodeLlama-13b-Instruct-hf",
                  "codellama/CodeLlama-7b-Instruct-hf",],

    'S-context': ["meta-llama/Llama-3-70b-chat-hf",
                  "meta-llama/Llama-3-8b-chat-hf",
                  "google/gemma-2b-it",
                  "code-llama/CodeLlama-7ob-Instruct-hf",],                  

    "databricks/dbrx-instruct": ["databricks/dbrx-instruct"],
    "mistralai/Mixtral-8x7B-Instruct-v0.1": ["mistralai/Mixtral-8x7B-Instruct-v0.1"], 
    "mistralai/Mistral-7B-Instruct-v0.2": ["mistralai/Mistral-7B-Instruct-v0.2"],
    "codellama/CodeLlama-70b-Instruct-hf": ["codellama/CodeLlama-70b-Instruct-hf"],
    "codellama/CodeLlama-34b-Instruct-hf": ["codellama/CodeLlama-34b-Instruct-hf"],
    "codellama/CodeLlama-7b-Instruct-hf": ["codellama/CodeLlama-7b-Instruct-hf"],
    "meta-llama/Llama-2-70b-chat-hf": ["meta-llama/Llama-2-70b-chat-hf"],
    "meta-llama/Llama-2-13b-chat-hf": ["meta-llama/Llama-2-13b-chat-hf"],
    "meta-llama/Llama-2-7b-chat-hf": ["meta-llama/Llama-2-7b-chat-hf"],
    "microsoft/phi-2": ["microsoft/phi-2"], 
    "google/gemma-2b-it": ["google/gemma-2b-it"],
    "meta-llama/Llama-3-8b-chat-hf": ["meta-llama/Llama-3-8b-chat-hf"],
    
}

def best_fit_model_for_spec(spec, models=MODELS):
    """
    Finds the resource that satisfies all given spec with the lowest aggregated score based on its indices in the lists.

    :param spec: A list of spec to satisfy.
    :param models=MODELS: A dictionary where keys are spec and values are ordered lists of resources.
    :return: The resource with the lowest score from the intersection of lists for the given spec, or None if no common resource is found.
    """

    # If first element of spec is one of the models, return it
    if spec[0] in ["databricks/dbrx-instruct",
                   "mistralai/Mixtral-8x7B-Instruct-v0.1", 
                   "mistralai/Mistral-7B-Instruct-v0.2",
                   "codellama/CodeLlama-70b-Instruct-hf",
                   "codellama/CodeLlama-34b-Instruct-hf",
                   "codellama/CodeLlama-7b-Instruct-hf",
                   "meta-llama/Llama-2-70b-chat-hf",
                   "meta-llama/Llama-2-13b-chat-hf",
                   "meta-llama/Llama-2-7b-chat-hf",
                   "microsoft/phi-2", 
                   "google/gemma-2b-it"]:
        return spec[0]
    
    if spec[0] == "moderate": 
        return "Meta-Llama/Llama-Guard-7b"

    # If spec doesn't have one of ["XL", "L", "M", "S", "XS"], add 'M' as default
    if not any(size in spec for size in ["XL", "L", "M", "S", "XS"]) and not any(context_length in spec for context_length in ["XL-context", "L-context", "M-context", "S-context"]):
        spec.append("S")

    # Initialize a dictionary to keep track of scores for each resource
    resource_scores = {}

    # Iterate over each tag to calculate scores for resources
    for tag in spec:
        if tag in models:
            for index, resource in enumerate(models[tag]):
                if resource in resource_scores:
                    resource_scores[resource] += index
                else:
                    resource_scores[resource] = index
        else:
            # If any tag is not present, return None as we can't satisfy the requirement
            return None

    # Filter resources that appear in all tag lists
    common_resources = {resource: score for resource, score in resource_scores.items() if all(resource in models[tag] for tag in spec)}
    
    if not common_resources:
        # If there's no common resource across all spec, return None
        raise ValueError(f"No models satisfy the given spec: {spec}")
    
    # Find the resource with the lowest score
    model_name = min(common_resources, key=common_resources.get)
    
    return model_name