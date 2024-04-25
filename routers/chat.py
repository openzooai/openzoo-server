# OS, utils
from utils.utils import chat_completion_to_dict
import asyncio
from typing import Union


# FastAPI, Starlette
from starlette.responses import StreamingResponse
from fastapi import Depends, APIRouter
from fastapi.security import HTTPBearer
router = APIRouter()
security = HTTPBearer(auto_error=False)


# OpenZoo
from inference.infer import InferenceEngine
from inference.moderate import Moderator
from validation.chat import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionChoice, ChatCompletionMessage, Usage
from auth.APIKeyManager import APIKeyManager
inferenceEngine = InferenceEngine()
moderator = Moderator()
apiKeyManager = APIKeyManager("auth/api_keys.json")


@router.post("/completions")
async def chat_completions(request: ChatCompletionRequest, bearer = Depends(security)):
    """
    Generate completions for a chat prompt.
    """
    # If request.model contains 'safe', run moderation and inference in parallel
    if ' safe ' in request.model or ' safe' in request.model or 'safe ' in request.model:
        # Remove ' safe ' from the model
        request.model = request.model.replace('safe', '')

        # Create tasks for moderation and inference
        moderation_task = asyncio.create_task(moderator.moderate(request.messages[-1].content))
        inference_task = asyncio.create_task(generate_chat_response(request))

        # Wait for both tasks to complete
        responses = await asyncio.gather(moderation_task, inference_task)
        moderation_response, inference_response = responses

        # If moderation response is safe, return the inference response
        if moderation_response.choices[0].text == 'safe':
            response = inference_response
        # If not, return an error response
        else:
            choice = ChatCompletionChoice(
                index=0,
                message=ChatCompletionMessage(
                    role="system",
                    content="Your message was flagged as inappropriate. Please try again."
                ),
                finish_reason="error"
            )

            usage = Usage(
                prompt_tokens=moderation_response.usage.prompt_tokens,
                completion_tokens=moderation_response.usage.completion_tokens,
                total_tokens=moderation_response.usage.total_tokens
            )

            response = ChatCompletionResponse(
                id="",
                object="error",
                created=0,
                model=moderation_response.model,
                choices=[choice],
                usage= usage
            )
    # If not, generate a chat response
    else:
        response = await generate_chat_response(request)

    return response

async def generate_chat_response(request: ChatCompletionRequest) -> Union[StreamingResponse, str]:
    # Check if the request is for streaming
    if request.stream:
        response = StreamingResponse(
            inferenceEngine.generate_chat_completion_stream(request), 
            media_type="application/x-ndjson"
        )
    # If not, check for messages to generate a response
    elif request.messages:
        response = inferenceEngine.generate_chat_completion(request)
    # If no messages, return an error
    else:
        response = "Empty prompt. Please provide a message."
    
    return response