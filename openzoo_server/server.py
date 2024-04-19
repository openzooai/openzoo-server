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
inferenceEngine = InferenceEngine()
from routers import chat, completions
from auth.APIKeyManager import APIKeyManager
apiKeyManager = APIKeyManager("auth/api_keys.json")


# Instantiate the FastAPI app
app = FastAPI(title="OpenZoo")


# Chat completions
app.include_router(
    chat.router,
    prefix="/v1/chat",
    dependencies=[Depends(apiKeyManager.verify_api_key)]
)


# Completions
app.include_router(
    completions.router,
    prefix="/v1",
    dependencies=[Depends(apiKeyManager.verify_api_key)]
)