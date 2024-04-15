# OS, utils
from utils.utils import chat_completion_to_dict


# FastAPI, Starlette
from starlette.responses import StreamingResponse
from fastapi import APIRouter

router = APIRouter()


# OpenZoo
from inference.infer import InferenceEngine
from validation.chat import ChatCompletionRequest
inferenceEngine = InferenceEngine()


@router.post("/completions")
async def chat_completions(request: ChatCompletionRequest):
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

    response_dict = chat_completion_to_dict(response)
    print(response_dict['usage'])

    return response