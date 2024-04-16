# Models by task
MODELS = {
    'chat': ["databricks/dbrx-instruct",
             "meta-llama/Llama-2-70b-chat-hf",
             "mistralai/Mixtral-8x7B-Instruct-v0.1", 
             "mistralai/Mistral-7B-Instruct-v0.2",
             "google/gemma-2b-it"],

    'code': ["databricks/dbrx-instruct",
             "codellama/CodeLlama-70b-Instruct-hf",
             "codellama/CodeLlama-34b-Instruct-hf",
             "codellama/CodeLlama-7b-Instruct-hf",],

    'summarization': ["mistralai/Mixtral-8x7B-Instruct-v0.1",
                      "meta-llama/Llama-2-13b-chat-hf",
                      "meta-llama/Llama-2-7b-chat-hf",
                      "google/gemma-2b-it",
                      "microsoft/phi-2"],

    'math': ["databricks/dbrx-instruct",
             "meta-llama/Llama-2-70b-chat-hf",
             "mistralai/Mixtral-8x7B-Instruct-v0.1",
             "mistralai/Mistral-7B-Instruct-v0.2",
             "google/gemma-2b-it"],

    'XL': ["databricks/dbrx-instruct"],

    'L': ["meta-llama/Llama-2-70b-chat-hf",
          "codellama/CodeLlama-70b-Instruct-hf"],

    'M': ["mistralai/Mixtral-8x7B-Instruct-v0.1",
          "codellama/CodeLlama-34b-Instruct-hf"],

    'S': ["mistralai/Mistral-7B-Instruct-v0.2",
          "codellama/CodeLlama-7b-Instruct-hf",
          "meta-llama/Llama-2-7b-chat-hf"],

    'XS': ["google/gemma-2b-it",
           "microsoft/phi-2"],
}

def best_fit_model_for_spec(spec, models=MODELS):
    """
    Finds the resource that satisfies all given spec with the lowest aggregated score based on its indices in the lists.

    :param spec: A list of spec to satisfy.
    :param models=MODELS: A dictionary where keys are spec and values are ordered lists of resources.
    :return: The resource with the lowest score from the intersection of lists for the given spec, or None if no common resource is found.
    """

    # If spec doesn't have one of ["XL", "L", "M", "S", "XS"], add 'M' as default
    if not any(size in spec for size in ["XL", "L", "M", "S", "XS"]):
        spec.append("M")

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
        raise ValueError(f"Task {task} not found in MODELS keys")
    
    # Find the resource with the lowest score
    model_name = min(common_resources, key=common_resources.get)
    
    return model_name