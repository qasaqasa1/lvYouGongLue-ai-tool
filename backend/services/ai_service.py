import os
import json
import random
from typing import List
from models import OutlineNode
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
# Using environment variable OPENAI_API_KEY
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_outline(location: str, days: int = None, budget: str = None) -> List[OutlineNode]:
    """
    Generates a travel outline for the given location using OpenAI.
    """
    if not client:
        # Fallback to mock data if no API key
        print(f"No API key found. Generating mock outline for {location}")
        return [
            OutlineNode(id="1", title="目的地概览与核心亮点", level=1, children=[
                OutlineNode(id="1-1", title="地理与气候特征", level=2, children=[]),
                OutlineNode(id="1-2", title="历史文化背景", level=2, children=[]),
                OutlineNode(id="1-3", title="必体验的3大特色", level=2, children=[]),
            ]),
            OutlineNode(id="2", title="美食与餐厅建议", level=1, children=[
                OutlineNode(id="2-1", title="当地必吃特色菜", level=2, children=[]),
                OutlineNode(id="2-2", title="高性价比餐厅推荐", level=2, children=[]),
            ]),
            OutlineNode(id="3", title="住宿推荐", level=1, children=[
                OutlineNode(id="3-1", title="区域选择建议", level=2, children=[]),
                OutlineNode(id="3-2", title="热门酒店/民宿推荐", level=2, children=[]),
            ])
        ]

    prompt = f"""
    Create a professional travel guide outline for {location}.
    {'Duration: ' + str(days) + ' days.' if days else ''}
    {'Budget level: ' + budget if budget else ''}
    
    The outline should be structured as a list of nodes. Each node has:
    - id: unique string (e.g., "1", "1-1")
    - title: name of the section in Chinese
    - level: 1 for main headings, 2 for subheadings
    - children: list of sub-nodes
    
    Return ONLY a valid JSON array of OutlineNode objects.
    Example structure:
    [
      {{"id": "1", "title": "目的地简介", "level": 1, "children": [
        {{"id": "1-1", "title": "最佳旅游时间", "level": 2, "children": []}}
      ]}}
    ]
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional travel planner. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        data = json.loads(response.choices[0].message.content)
        # The response might be wrapped in an object like {"outline": [...]} or just the array
        if isinstance(data, dict):
            if "outline" in data:
                nodes_data = data["outline"]
            else:
                # If it's a dict but not "outline", maybe it's the list itself in a wrapper or just one key
                nodes_data = list(data.values())[0] if isinstance(list(data.values())[0], list) else []
        else:
            nodes_data = data

        return [OutlineNode(**node) for node in nodes_data]
    except Exception as e:
        print(f"Error calling OpenAI for outline: {e}")
        return []

def generate_article(location: str, node: OutlineNode) -> str:
    """
    Generates content for a specific outline node using a specific persona and detailed requirements.
    """
    persona = """
    # 角色
    你是一位网红旅游博主和专业的小红书运营和资深旅游杂志编辑，擅长依据用户提供的旅游目的地、旅游攻略大纲，进行当前标题的攻略编写。
    你拥有丰富的旅游经验，擅长找出各种好玩及便宜又安全，体验感十足的路线。你熟悉风土人情，掌握最新资讯及价格。

    ## 核心要求
    1. **真实实用**：内容必须基于真实的旅游逻辑，提供详细的避坑指南和实用建议。
    2. **详细深入**：
       - 在【主题路线推荐】、【本地专题体验】和【必访景点分块介绍】中，必须定制详细的旅行全程讲解。
       - 在【美食与餐厅建议】和【住宿推荐】中，必须使用真实的当地信息。
       - 包含：具体项目/店名、详细费用（必须包含人民币换算）、详细地址（最好有联系方式）、景点评分（5分制）等。
    3. **结构化呈现**：
       - 适当插入 HTML 表格（使用 Tailwind CSS 类名：min-w-full border-collapse border border-gray-200），清晰展示流程、开支、地址和联系方式。
       - 每个景点要有深度讲解，美食要有口感描述、地址和推荐理由。
    4. **文风**：亲切活泼，高度口语化与网络化，多用 Emoji。
    """

    if not client:
        # Return mock data as fallback (already implemented in the previous code)
        return f"""
        <div class="article-container p-6 bg-white rounded-lg shadow-sm mb-12 border border-gray-100">
            <h2 class="text-3xl font-bold text-blue-900 mb-6 pb-2 border-b-2 border-blue-100">{node.title}</h2>
            <div class="prose max-w-none text-gray-700 leading-relaxed">
                <p class="mb-4">【演示模式 - 未配置 API Key】这里是关于 <strong>{location}</strong> - <strong>{node.title}</strong> 的精彩内容...</p>
                <p>请在部署环境中配置 <code>OPENAI_API_KEY</code> 以获取 AI 生成的真实内容！✨</p>
            </div>
        </div>
        """

    prompt = f"""
    请作为一位{persona}。
    目的地：{location}
    当前章节标题：{node.title}

    要求：
    - 仅针对当前标题编写攻略，不要写其他章节的内容。
    - 必须包含具体的店名、地址、评分、以及价格（含RMB换算）。
    - 必须使用 HTML 格式输出，使用 Tailwind CSS 类名进行美化。
    - 包含至少一个项目明细表格或推荐清单表格。
    - 结尾包含一个博主私藏贴士。
    - 在末尾添加一个下载按钮的 HTML 代码（保持原样）：
      <div class="mt-6 flex justify-end gap-3">
          <button onclick="downloadNodeDocxById('{node.id}')" class="flex items-center gap-1 px-3 py-1.5 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition text-sm font-medium border border-green-200">
              <i data-lucide="download" class="w-4 h-4"></i> 下载本篇 (DOCX)
          </button>
      </div>
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a travel expert writing in HTML."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"<p>Error generating article: {e}</p>"

def generate_images(location: str, count: int, type: str, content: str = None) -> List[str]:
    """
    Generates image URLs for the given location using DALL-E 3 with specific prompt logic.
    """
    if not client:
        # Mock implementation for images
        images = []
        base_url = "https://placehold.co/600x800"
        for i in range(count):
            text = f"{location} {type} {i+1}"
            images.append(f"{base_url}/blue/white?text={text}")
        return images

    urls = []
    for _ in range(count):
        if type == "product":
            # Product Image Prompt Logic
            sample_content = content[:1000] if content else f"关于{location}的旅游特色和手账风格排版"
            prompt = f"""
            As a professional graphic artist and AI image expert specializing in hand-drawn journal (Techo) style.
            Create a 3:4 aspect ratio image based on this travel content for {location}:
            ---
            {sample_content[:300]}
            ---
            Logic: Analyze the hierarchy and progressive relationship of headings. Summarize the core content into a simple, beautiful layout.
            Visual Elements: Use numbers, vector graphics, arrows, and shapes for layout. Include cute cartoon illustrations for decoration.
            Style: Hand-drawn, clean, minimalist, artistic travel journal page.
            No real human photos, only artistic drawing.
            """
        else:
            # Note Image Prompt Logic
            line1 = random.choice(["00年摄影博主", "05年女大学生", "旅游体验师", "95后职场新人"])
            line2 = f"{location}{random.choice(['两天一晚', '48小时速刷', '深度游'])}"
            line3 = f"人均{random.randint(300, 3000)}元"
            
            prompt = f"""
            Create a travel vlog collage cover for {location}.
            Aspect ratio: 3:4.
            Scene: A collage of multiple natural travel photos (sceneries, local food, landmarks) of {location}.
            Style: Bright, fresh, mobile photography style, authentic and natural.
            Text Overlays (MUST INCLUDE THESE CHINESE TEXTS IN BOLD, THICK FONTS):
            1. "{line1}" (Top or small text)
            2. "{line2}" (Center, largest font, very bold)
            3. "{line3}" (Bottom, clear budget info)
            Typography: Bold, thick stroke fonts (like 'Zongyi' or 'Cu-yuan' style).
            Colors: High contrast (e.g., white text with red border, or yellow text with black border).
            Vibe: Youthful, energetic, student travel style, highly eye-catching for social media.
            """

        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1792", # This is roughly 9:16 or 3:4-ish tall
                quality="standard",
                n=1
            )
            urls.append(response.data[0].url)
        except Exception as e:
            print(f"Error generating image: {e}")
            urls.append("https://placehold.co/600x800?text=Image+Generation+Failed")
            
    return urls