from pydantic import BaseModel
from typing import List, Optional

class OutlineNode(BaseModel):
    id: str
    title: str
    level: int  # 1: H1, 2: H2, 3: H3
    children: List['OutlineNode'] = []

class OutlineRequest(BaseModel):
    location: str
    days: Optional[int] = None
    budget: Optional[str] = None

class OutlineResponse(BaseModel):
    location: str
    outline: List[OutlineNode]

class ArticleContent(BaseModel):
    title: str
    content: str  # HTML or Markdown
    level: int

class GenerateContentRequest(BaseModel):
    location: str
    outline: List[OutlineNode]
    style: Optional[str] = "friendly"

class GenerateContentResponse(BaseModel):
    html_content: str
    download_url: str
    node_downloads: Optional[dict] = {}

class ImageRequest(BaseModel):
    location: str
    count: int = 1
    type: str # "product" or "note"
    content: Optional[str] = None

class ImageResponse(BaseModel):
    urls: List[str]
