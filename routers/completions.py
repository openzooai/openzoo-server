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
from validation.completion import CompletionRequest
inferenceEngine = InferenceEngine()
from auth.APIKeyManager import APIKeyManager
apiKeyManager = APIKeyManager("auth/api_keys.json")


@router.post("/completions")
async def completions(request: CompletionRequest, bearer = Depends(security)):
    """
    Generate completions for a chat prompt.
    """

    # If request.stream is True, generate a streaming response
    if request.stream:
        response = StreamingResponse(
            inferenceEngine.generate_completion_stream(request),
            media_type="application/x-ndjson"
        )
    # If request.prompt is not empty, generate a completion
    elif request.prompt:
        response = inferenceEngine.generate_completion(request)
    # If no prompt, return an error
    else:
        response = "Empty prompt. Please provide a message."

    return response