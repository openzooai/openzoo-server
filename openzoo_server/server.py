# OS, utils
import asyncio
import json
import time
from typing import Optional


# FastAPI, Starlette
from starlette.responses import StreamingResponse
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPBearer


# OpenZoo
from router.router import Router
from validation.chat import ChatCompletionRequest


# Instantiate the FastAPI app
app = FastAPI(title="OpenZoo")
security = HTTPBearer(auto_error=False)


# instantiate the router
router = Router()


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

    print(header)

    if request.stream:
        return StreamingResponse(
            router.generate_stream(request), media_type="application/x-ndjson"
        )
    
    if request.messages:
        resp_content = (
            router.generate(request)
        )
    else:
        resp_content = "Empty prompt. Please provide a message."

    return resp_content