import asyncio
import json
import time

from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Request
from router.router import Router

from validations.chat import ChatCompletionRequest

app = FastAPI(title="OpenAI-compatible API")


# instantiate the router
router = Router()


@app.post("/chat/completions")
async def chat_completions(request: ChatCompletionRequest):

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8888)