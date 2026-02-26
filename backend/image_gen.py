import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# === 默认风格模板 (常量) ===
DEFAULT_STYLE_PROMPT = (
    "A modern Tech/Internet company presentation slide. "
    "Style: Modern SaaS aesthetic, clean UI, sleek vector art, soft shadows (glassmorphism). "
    "Background: Clean LIGHT background (white or very light grey) with SUBTLE tech accents (faint grids, soft blue/purple mesh gradients). "
    "Content: Minimalist infographics, rounded cards, sans-serif typography style. "
    "Avoid: Old-school academic look, heavy dark borders, realistic photos, cluttered text. "
)

class ImageGenerator:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "https://api.geekai.pro")
        self.api_key = os.getenv("API_KEY", "")
        self.image_model = os.getenv("MODEL_IMAGE", "gemini-3-pro-image-preview")

    def _call_gemini_api(self, prompt: str, image_data: str = None, max_retries: int = 3):
        """
        使用 Gemini 官方格式调用 API
        
        Args:
            prompt: 文本提示词
            image_data: base64 图片数据（可选，用于图生图）
            max_retries: 最大重试次数
            
        Returns:
            图片 URL 或 base64 数据，失败返回 None
        """
        url = f"{self.base_url}/v1beta/models/{self.image_model}:generateContent"
        print(f"[DEBUG ImageGenerator] API Base URL: {self.base_url}")
        print(f"[DEBUG ImageGenerator] Full API endpoint: {url}")
        print(f"[DEBUG ImageGenerator] Model: {self.image_model}")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 构建 parts
        parts = [{"text": prompt}]
        
        # 如果有图片数据，添加到 parts
        if image_data:
            # image_data 可能是 base64 data URL 格式 (data:image/png;base64,...)
            if image_data.startswith("data:"):
                # 提取 base64 部分
                header, encoded = image_data.split(",", 1)
                mime_type = header.split(":")[1].split(";")[0]
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": encoded
                    }
                })
            else:
                # 假设是纯 base64
                parts.append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": image_data
                    }
                })
        
        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "thinkingConfig": {
                    "thinkingBudget": 128,
                    "includeThoughts": False
                }
            }
        }
        
        for attempt in range(max_retries):
            try:
                print(f"[Gemini API] Attempt {attempt + 1}/{max_retries}...")
                
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                
                # 解析响应
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            # 检查是否有图片数据（支持两种命名格式：inline_data 和 inlineData）
                            image_data = None
                            mime_type = "image/png"
                            
                            if "inline_data" in part:
                                image_data = part["inline_data"].get("data")
                                mime_type = part["inline_data"].get("mime_type", "image/png")
                            elif "inlineData" in part:
                                image_data = part["inlineData"].get("data")
                                mime_type = part["inlineData"].get("mimeType", "image/png")
                            
                            if image_data:
                                # 返回 base64 data URL
                                return f"data:{mime_type};base64,{image_data}"
                            # 检查是否有文本中的 URL
                            elif "text" in part and "http" in part["text"]:
                                # 尝试从文本中提取 URL
                                import re
                                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', part["text"])
                                if urls:
                                    return urls[0]
                
                print(f"⚠️ [DEBUG] No image found in response. Response: {json.dumps(result, indent=2)[:500]}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"[Gemini API] Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"[Gemini API] All {max_retries} attempts failed.")
                    return None
            except Exception as e:
                print(f"[Gemini API] Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return None
        
        return None

    def generate_slide_image(self, prompt: str, reference_style_prompt: str = None, api_key: str = None, custom_style: str = None):
        """
        [创作模式]
        """
        original_api_key = self.api_key
        if api_key:
            self.api_key = api_key

        try:
            base_instruction = DEFAULT_STYLE_PROMPT

            if reference_style_prompt:
                full_prompt = (
                    f"{base_instruction} "
                    f"**TARGET SLIDE CONTENT**: {prompt}. "
                    f"**VISUAL CONSISTENCY**: Maintain the exact same style and color palette as this previous slide: [[ {reference_style_prompt} ]]."
                )
            else:
                full_prompt = f"{base_instruction} **SLIDE CONTENT**: {prompt}"

            return self._call_gemini_api(full_prompt)
        finally:
            if api_key:
                self.api_key = original_api_key

    def generate_slide_image_from_plan(self, slide_data: dict, global_style_prompt: str, presentation_mode: str = "slides", api_key: str = None):
        """
        基于规划结果生成图片：主体 + 全局风格 + 模式控制文字密度
        """
        original_api_key = self.api_key
        if api_key:
            self.api_key = api_key

        try:
            subject = slide_data.get("visual_subject") or slide_data.get("visual_prompt") or "A clean presentation slide background"
            title = slide_data.get("title", "")
            text_density = (
                "Minimal text density. Only short title and 2-4 concise bullets. Emphasize whitespace."
                if presentation_mode == "slides"
                else "Moderate text density. Allow 4-6 bullets with brief explanations while keeping clean layout."
            )
            constraints = (
                "No watermarks. No logos. Keep text readable. Use a professional layout."
            )
            full_prompt = (
                "Generate a presentation slide image.\n"
                f"SUBJECT: {subject}\n"
                f"GLOBAL STYLE: {global_style_prompt}\n"
                f"TEXT DENSITY: {text_density}\n"
                f"TITLE (if any): {title}\n"
                f"CONSTRAINTS: {constraints}\n"
                "COMPOSITION: Leave 35-45% whitespace for overlay text if needed.\n"
                "Aspect Ratio: 16:9."
            )
            return self._call_gemini_api(full_prompt)
        finally:
            if api_key:
                self.api_key = original_api_key

    def modify_slide_image(self, prompt: str, base_image_url: str, history_context: list = None, api_key: str = None, custom_style: str = None):
        """
        [修改模式] 精确微调幻灯片
        """
        original_api_key = self.api_key
        if api_key:
            self.api_key = api_key

        try:
            full_prompt = (
                "You are a precise slide editor. "
                "CRITICAL RULES:\n"
                "1. ONLY modify the specific part the user mentions. "
                "Do NOT change anything else.\n"
                "2. Keep the EXACT same layout, background, colors, fonts, "
                "and all other elements UNCHANGED.\n"
                "3. If the user says 'change the title', ONLY change the title text. "
                "Everything else stays pixel-perfect identical.\n"
                "4. Preserve all spacing, alignment, and visual hierarchy.\n\n"
                f"User's modification request: {prompt}\n\n"
                "Apply ONLY this change. Nothing else."
            )

            return self._call_gemini_api(full_prompt, image_data=base_image_url)
        finally:
            if api_key:
                self.api_key = original_api_key
