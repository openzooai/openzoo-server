# OS, utils
import asyncio
import json
import time


# FastAPI, Starlette
from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Request


# OpenZoo
from router.router import Router
from validation.chat import ChatCompletionRequest


# Instantiate the FastAPI app
app = FastAPI(title="OpenZoo")


# instantiate the router
router = Router()


@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """
    Generate completions for a chat prompt.
    """
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