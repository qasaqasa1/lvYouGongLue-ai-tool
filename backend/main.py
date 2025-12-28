from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import zipfile
import sys
from dotenv import load_dotenv

load_dotenv()

# Add current directory to sys.path to allow importing modules from backend folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai_service import generate_outline, generate_article, generate_images
from services.docx_service import create_docx
from models import OutlineRequest, OutlineResponse, GenerateContentRequest, GenerateContentResponse, OutlineNode, ImageRequest, ImageResponse

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
if not os.path.exists("outputs"):
    os.makedirs("outputs")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Templates
templates = Jinja2Templates(directory="backend/templates")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/generate-outline", response_model=OutlineResponse)
async def api_generate_outline(request: OutlineRequest):
    try:
        outline = generate_outline(request.location, request.days, request.budget)
        return OutlineResponse(location=request.location, outline=outline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import re

class GenerateContentResponse(BaseModel):
    html_content: str
    download_url: str
    node_downloads: Optional[dict] = {} # Mapping of node_id to download_url

class SingleContentRequest(BaseModel):
    location: str
    node: OutlineNode

@app.post("/api/generate-single-content", response_model=GenerateContentResponse)
async def api_generate_single_content(request: SingleContentRequest):
    try:
        output_dir = "outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Generate content for this specific node
        content = generate_article(request.location, request.node)
        
        # Create individual DOCX
        filename = f"{request.location}_{request.node.title}.docx"
        # Sanitize filename
        filename = "".join([c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')]).strip()
        filepath = create_docx(request.location, request.node.title, content, filename=filename)
        
        html_content = f'<div id="node-{request.node.id}" class="mb-8 scroll-mt-4">\n{content}\n</div>\n'
        
        return GenerateContentResponse(
            html_content=html_content,
            download_url=f"/outputs/{os.path.basename(filepath)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-content", response_model=GenerateContentResponse)
async def api_generate_content(request: GenerateContentRequest):
    try:
        # Ensure output directory exists
        output_dir = "outputs"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Generate content for each top-level node (H1)
        generated_files = []
        node_downloads = {}
        html_response_content = ""
        
        # Track used filenames to handle duplicates
        used_filenames = set()
        
        def get_unique_filename(title):
            base = "".join([c for c in title if c.isalnum() or c in (' ', '.', '_', '-')]).strip()
            if not base: base = "article"
            filename = f"{request.location}_{base}.docx"
            counter = 1
            while filename in used_filenames:
                filename = f"{request.location}_{base}_{counter}.docx"
                counter += 1
            used_filenames.add(filename)
            return filename

        def traverse(n: OutlineNode):
            nonlocal html_response_content
            
            # Generate content for this node
            content = generate_article(request.location, n)
            
            # Create individual DOCX for this node
            unique_filename = get_unique_filename(n.title)
            filepath = create_docx(request.location, n.title, content, filename=unique_filename)
            generated_files.append(filepath)
            
            # Store individual download URL
            node_downloads[n.id] = f"/outputs/{os.path.basename(filepath)}"
            
            # Append to HTML response with ID for scrolling
            html_response_content += f'<div id="node-{n.id}" class="mb-8 scroll-mt-4">\n{content}\n</div>\n'
            
            # Recurse for children
            for child in n.children:
                traverse(child)

        for node in request.outline:
            traverse(node)

        # Zip files
        zip_filename = f"{request.location}_guide.zip"
        zip_filepath = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for file in generated_files:
                zipf.write(file, os.path.basename(file))
                
        return GenerateContentResponse(
            html_content=html_response_content,
            download_url=f"/outputs/{zip_filename}",
            node_downloads=node_downloads
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-images", response_model=ImageResponse)
async def api_generate_images(request: ImageRequest):
    try:
        urls = generate_images(request.location, request.count, request.type, request.content)
        return ImageResponse(urls=urls)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    # Use PORT from environment variable for deployment (e.g., Render)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
