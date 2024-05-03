# OS, utils
import asyncio
import json
import time
from typing import Optional
from utils.utils import chat_completion_to_dict
from pathlib import Path


# FastAPI, Starlette
from starlette.responses import StreamingResponse
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# OpenZoo
from inference.infer import InferenceEngine
from validation.chat import ChatCompletionRequest
inferenceEngine = InferenceEngine()
from routers import chat, completions, embeddings, admin
from auth.APIKeyManager import APIKeyManager
apiKeyManager = APIKeyManager("auth/api_keys.json")


# Instantiate the FastAPI app
app = FastAPI(title="OpenZoo")


# Set root as base directory
BASE_DIR = Path(__file__).resolve().parent.parent
print("BASE: ", BASE_DIR)


# Static files
app.mount("/static", StaticFiles(directory=str(Path(BASE_DIR, 'static'))), name="static")


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


# Embeddings
app.include_router(
    embeddings.router,
    prefix="/v1",
    dependencies=[Depends(apiKeyManager.verify_api_key)]
)


# Admin page
app.include_router(
    admin.router,
    prefix="/v1",
    # dependencies=[Depends(apiKeyManager.verify_api_key)]
)