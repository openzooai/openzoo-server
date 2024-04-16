# OS, utils
from utils.utils import chat_completion_to_dict


# FastAPI, Starlette
from starlette.responses import StreamingResponse
from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer
router = APIRouter()
security = HTTPBearer(auto_error=False)


# OpenZoo
from inference.infer import InferenceEngine
from validation.chat import ChatCompletionRequest
inferenceEngine = InferenceEngine()
from auth.APIKeyManager import APIKeyManager
apiKeyManager = APIKeyManager("auth/api_keys.json")


@router.post("/completions")
async def chat_completions(request: ChatCompletionRequest, bearer = Depends(security)):
    """
    Generate completions for a chat prompt.
    """

    # Check if the request is for streaming
    if request.stream:
        response = StreamingResponse(
            inferenceEngine.generate_stream(request), media_type="application/x-ndjson"
        )
    # If not, check for messages to generate a response
    elif request.messages:
        response = (
            inferenceEngine.generate(request)
        )
    # If no messages, return an error
    else:
        response = "Empty prompt. Please provide a message."

    # Convert the response to a dictionary to extract the total tokens used
    # response_dict = chat_completion_to_dict(response)    
    # total_tokens = response_dict['usage']['total_tokens']

    # # Get API key from the request
    # api_key = bearer.credentials
    # spec = request.model
    # print(spec)

    return response