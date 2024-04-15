# OS, utils
import asyncio
import json
import time
from typing import Optional
from utils.utils import chat_completion_to_dict


# FastAPI, Starlette
from starlette.responses import StreamingResponse
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPBearer


# OpenZoo
from inference.infer import InferenceEngine
from validation.chat import ChatCompletionRequest


# Instantiate the FastAPI app
app = FastAPI(title="OpenZoo")
security = HTTPBearer(auto_error=False)


# instantiate the router
inferenceEngine = InferenceEngine()


# Authorization
def check_bearer_credentials(token: str = Depends(security)):
    if token.credentials is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if token.credentials != "d56f4hd45hd23h4d86h4e5rgstwetgljew":
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {"credentials": token}


@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest, header= Depends(check_bearer_credentials)):
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