from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
import os
from pathlib import Path
from jinja2 import Environment

def intersect(a, b):
    return list(set(a) & set(b))

# Add intersect filter to Jinja2
env = Environment()
env.filters['intersect'] = intersect


# Set root as base directory
BASE_DIR = Path(__file__).resolve().parent.parent
print(BASE_DIR)


router = APIRouter()
templates = Jinja2Templates(directory=str(Path(BASE_DIR, 'templates')))

# Path to the JSON file
json_file_path = str(Path(BASE_DIR, 'model_mapping.json'))

def read_json():
    if not os.path.exists(json_file_path):
        return {}
    with open(json_file_path, 'r') as file:
        return json.load(file)

def write_json(data):
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def calculate_intersections(mapping):
    categories = ['chat', 'code', 'summarization', 'math', 'XL-context', 'L-context', 'M-context', 'S-context']
    sizes = ['XL', 'L', 'M', 'S', 'XS']
    table_data = {size: {} for size in sizes}
    for size in sizes:
        for category in categories:
            size_set = set(mapping.get(size, []))
            category_set = set(mapping.get(category, []))
            intersection = list(size_set & category_set)
            table_data[size][category] = intersection
    return table_data

@router.get("/admin", response_class=HTMLResponse)
def get_models(request: Request):
    model_mapping = read_json()
    table_data = calculate_intersections(model_mapping)
    return templates.TemplateResponse("table.html", {"request": request, "table_data": table_data})


# @router.post("/admin")
# def update_models(request: dict):
#     write_json(request)
#     return {"message": "Data updated successfully"}


@router.get("/model-names")
async def get_model_names():
    # Assuming you have a function to read this from a file or database
    model_names = [
        "databricks/dbrx-instruct",
        "meta-llama/Llama-3-70b-chat-hf",
        "google/gemma-2b-it",
        # Add more model names here
    ]
    return JSONResponse(model_names)
