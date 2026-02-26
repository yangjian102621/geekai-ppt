import os
import uuid
import base64
from typing import Optional

import aiohttp
import requests

# 确保存储根目录存在
STORAGE_ROOT = os.path.join("storage", "images")
os.makedirs(STORAGE_ROOT, exist_ok=True)


def save_image_locally_sync(image_data: str, session_id: str) -> Optional[str]:
    """同步版本，供后台任务使用。"""
    session_dir = os.path.join(STORAGE_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)
    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(session_dir, filename)
    if image_data.startswith("data:"):
        header, encoded = image_data.split(",", 1)
        data = base64.b64decode(encoded)
        with open(filepath, "wb") as f:
            f.write(data)
    elif image_data.startswith("http"):
        resp = requests.get(image_data, timeout=60)
        if resp.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(resp.content)
        else:
            return None
    else:
        try:
            data = base64.b64decode(image_data)
            with open(filepath, "wb") as f:
                f.write(data)
        except Exception:
            return None
    return f"/images/{session_id}/{filename}"


async def save_image_locally(image_data: str, session_id: str) -> str:
    """
    将图片保存到 storage/images/{session_id}/ 目录下
    """
    # 1. 创建会话专属文件夹
    session_dir = os.path.join(STORAGE_ROOT, session_id)
    os.makedirs(session_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.png"
    # 物理保存路径
    filepath = os.path.join(session_dir, filename)
    
    # 逻辑 1: Base64 数据
    if image_data.startswith("data:"):
        header, encoded = image_data.split(",", 1)
        data = base64.b64decode(encoded)
        with open(filepath, "wb") as f:
            f.write(data)
            
    # 逻辑 2: HTTP URL
    elif image_data.startswith("http"):
        async with aiohttp.ClientSession() as session:
            async with session.get(image_data) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    with open(filepath, "wb") as f:
                        f.write(data)
                else:
                    return None
    # 逻辑 3: 纯 Base64
    else:
        try:
            data = base64.b64decode(image_data)
            with open(filepath, "wb") as f:
                f.write(data)
        except:
            return None

    # 返回相对路径 (StaticFiles 会自动处理子目录)
    # 结果类似: /images/session_uuid/image_uuid.png
    return f"/images/{session_id}/{filename}"