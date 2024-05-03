# FastAPI
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

# OpenZoo
from inference.infer import InferenceEngine
inferenceEngine = InferenceEngine()

router = APIRouter()


@router.post("/embeddings")
async def get_embeddings(request: Request):

    # Get request data
    request_dict = await request.json()
    input = request_dict['input']
    model = request_dict['model']

    # Generate embeddings
    embeddings = await inferenceEngine.generate_embeddings(input, model)

    return embeddings