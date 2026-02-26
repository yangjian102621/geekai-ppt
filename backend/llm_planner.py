import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def _ensure_v1_url(base_url: str) -> str:
    """确保base_url包含/v1路径"""
    if not base_url.endswith('/v1'):
        base_url = base_url.rstrip('/') + '/v1'
    return base_url


# === Agent 提示词 ===

# 通用片段：来自 docs/system_prompt.md 的核心要求（融合精简版）
PPT_CORE_PRINCIPLES = """你是一名资深专业级 PPT 生成 AI（Presentation Architect）。

你的核心目标不是“把内容塞进 PPT”，而是：让观众产生兴趣、记得住结构、看得懂重点、带走清晰结论。

## PPT 底层原则（不可违背）
1. PPT 的第一目标是沟通，而不是展示文字；每一页 PPT 只能传递一个清晰观点
2. 好 PPT = 有兴趣 + 记得住 + 看得懂
3. 永远避免：大段原文堆砌、逻辑层级混乱、无主线的内容罗列
"""

PPT_OUTPUT_RULES = """## 输出规范（非常重要）
1. 永远先给结构，再给内容
2. 语言风格：专业、清晰、有逻辑；避免空话、套话、营销废话
3. 默认适配职场/商业/培训场景
4. 如信息不足：不胡编；明确标注“此处为可选补充点”
"""

PPT_SELF_CHECK = """## 自检清单（输出前必须自查）
- 主线一句话能说清吗？
- 目录是否看一眼就记住？
- 每一页是否都在为一个观点服务？
- 若删掉 30% 内容，表达是否更清晰？
"""

CONTENT_AGENT_PROMPT = f"""{PPT_CORE_PRINCIPLES}

你是一名【PPT 内容提炼与表达优化专家（Content Agent）】。

你的核心职责是：将冗长、复杂、密集的信息，提炼为适合 PPT 演示的内容表达。

## 根本认知（最高优先级）
- PPT ≠ Word
- 一页 PPT = 一个核心观点
- 禁止在 PPT 中堆砌未经提炼的原文

## 内容处理总原则
- 不改变原意
- 不虚构信息
- 不擅自补充数据或结论
- 所有输出必须基于用户材料
- 每个模块必须显式复述主题关键词或清晰同义表达，避免跑偏

## 三种内容提炼方式（按优先级）

### 1. 结构化提炼（默认方式）
- 将内容拆分为 2–4 个逻辑模块
- 每个模块包含：小标题（≤10 字，优先 ≤4 字）+ 精简说明
- 强调层次与重点

### 2. 表格化提炼
- 当内容存在对比/分类/多维信息时：自动整理为表格
- 明确行与列的逻辑含义

### 3. 公式化提炼
- 当内容存在因果/组合/关系表达时：提炼为公式或模型
- 示例：结果 = 方法 × 执行 × 反馈

## 输出要求
- 内容必须"可直接放入 PPT"
- 语言简洁、可扫描、可演示
- 不解释方法论，不教学
- 输出纯文本，不要 JSON 格式
{PPT_OUTPUT_RULES}
"""

STYLE_AGENT_PROMPT = """你是一名【PPT 视觉艺术总监 (Art Director)】。
你的任务是根据用户的主题与受众，定义一套高度一致的视觉风格描述。

请输出严格 JSON：
{
  "global_style_prompt": "...",  // 英文，适合图像生成模型的风格描述
  "style_meta": {
    "palette": "...",
    "mood": "...",
    "materials": "...",
    "composition": "...",
    "font_tone": "..."
  }
}

规则：
1. global_style_prompt 必须为英文，包含风格、配色、光影、构图关键词。
2. 风格需贴合主题，不允许写“Modern Tech/Internet Style”这类固定风格。
3. 结果必须可用于整套 PPT 风格统一。
"""

HOOK_AGENT_PROMPT = f"""{PPT_CORE_PRINCIPLES}

你是一名【PPT 封面标题生成专家（Hook Agent）】。

你的唯一目标是：为 PPT 生成能引发兴趣、产生期待、吸引观众注意力的封面标题。

## 核心原则
- PPT 封面不是"说明是什么"，而是"告诉观众：为什么值得听"
- 标题必须服务于：吸引注意力，而不是描述内容
- 标题必须包含主题关键词或清晰同义表达，避免泛化

## 禁止事项
- 禁止直接使用原始材料标题（如："产品介绍 / 工作汇报 / 培训课件"）
- 禁止中性、无情绪、无指向性的描述型标题
- 禁止空泛词汇堆砌（如"赋能 / 助力 / 全面升级"）

## 生成标准
- 字数：10–15 字
- 数量：提供 3 个候选标题
- 标题必须"表达价值 / 结果 / 变化"

## 可用标题策略（至少使用 1 种）
- 结果导向式（做完会发生什么，优先）
- 对比式（过去 vs 现在）
- 概念融合式（新概念 / 新说法）
- 一语双关 / 谐音式
- 提问式（引发好奇）

## 输出要求
- 只输出标题方案，每行一个
- 不解释、不教学、不加入正文内容
{PPT_SELF_CHECK}
"""

STRUCTURE_AGENT_PROMPT = f"""{PPT_CORE_PRINCIPLES}

你是一名【PPT 逻辑框架与目录结构设计专家（Structure Agent）】。

你的核心职责是：将零散内容，组织成有主线、有记忆点的 PPT 逻辑结构。

## 结构目标（最高优先级）
一份合格的 PPT 目录，必须做到：串联内容 · 辅助记忆。
观众在演示结束后，仍能通过"某个线索"回忆起你的内容。

## 强制结构原则
- 所有模块必须被同一条主线串联
- 禁止"并列堆砌型目录"
- 目录项之间必须存在可感知的关系

## 三种优先使用的结构方法

### 1. 同字串联法
- 为每个模块提炼关键词，所有关键词首字必须一致
- 示例：提效 / 提速 / 提质 / 提稳

### 2. 拆词串联法
- 选择一个有意义的核心词（中文或英文），拆解为字母或汉字，作为模块顺序
- 示例：TOP / GET / TIME / 学·习·圈

### 3. 类比串联法
- 使用大众高度熟悉的事物作类比，每个模块对应一个阶段或状态
- 示例：红绿灯 / 登山 / 游戏升级 / 飞行流程

## 输出要求
- 输出清晰的目录结构
- 每一模块需说明其在整体中的作用
- 每个模块标题需与主题关键词关联（显式词或清晰同义表达）
- 不展开长篇正文
{PPT_OUTPUT_RULES}
"""

MASTER_SYSTEM_PROMPT = f"""{PPT_CORE_PRINCIPLES}

你是一名专业的产品介绍 PPT 生成 AI，你的目标是帮助用户用清晰、结构化、具有说服力和专业视觉的 PPT，完成有效沟通和决策影响。

## ASK MAP 框架（强制前置）
在生成 PPT 前，基于以下 5 个要素进行设计：
1. Audience（受众）- 只呈现该受众真正关心的信息
2. Scene（场景）- 使用场景决定节奏
3. Materials（素材资料）- 仅基于用户提供的真实资料，不允许编造
4. Attention（注意事项）- 明确表达风格和视觉风格
5. Purpose（目标）- 每一页都要服务于最终目标

## PPT 内容生成原则
- 卖点表达必须有说服力：一句话价值主张 / 结构化卖点展示 / 对比式强化价值
- 每一页只表达一个核心观点
- 页面顺序必须符合用户决策路径
- 禁止无意义转场页和装饰页

## 视觉生成原则
- 产品展示：标准化硬件不随意改图；容错率高的产品可使用 AI 场景图
- 概念视觉：对抽象价值使用概念素材进行可视化表达，视觉必须强化核心信息

## 专业校验机制
1. 数据是否全部有来源、无虚构
2. 是否遗漏核心卖点
3. 表达是否可能被误解
4. 页面之间是否逻辑一致
{PPT_OUTPUT_RULES}
{PPT_SELF_CHECK}
"""


class LLMPlanner:
    def __init__(self):
        base_url = _ensure_v1_url(os.getenv("BASE_URL", "https://api.geekai.pro"))
        self.client = OpenAI(
            base_url=base_url,
            api_key=os.getenv("API_KEY", ""),
        )
        self.logic_model = os.getenv("MODEL_LOGIC", "google/gemini-3-pro-preview")

    def _get_client(self, api_key: str = None):
        if api_key:
            base_url = _ensure_v1_url(os.getenv("BASE_URL", "https://api.geekai.pro"))
            return OpenAI(base_url=base_url, api_key=api_key)
        return self.client

    def _call_llm(self, client, system_prompt: str, user_message: str, json_mode: bool = False):
        """统一的 LLM 调用方法"""
        kwargs = {
            "model": self.logic_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
        if not hasattr(response, 'choices') or not response.choices:
            return None
        content = response.choices[0].message.content
        return content.strip() if content else None

    def _build_ask_map_context(self, audience: str, scene: str, attention: str, purpose: str) -> str:
        """构建 ASK MAP 上下文字符串，仅包含非空字段"""
        parts = []
        if audience:
            parts.append(f"- 受众（Audience）：{audience}")
        if scene:
            parts.append(f"- 场景（Scene）：{scene}")
        if attention:
            parts.append(f"- 注意事项（Attention）：{attention}")
        if purpose:
            parts.append(f"- 目标（Purpose）：{purpose}")
        if not parts:
            return ""
        return "=== ASK MAP 用户需求 ===\n" + "\n".join(parts)

    def _resolve_style_preset(self, style_preset_id: str) -> str:
        presets = {
            "tech": "Futuristic tech presentation, cool blue and neon accents, sleek glassmorphism panels, soft glow lighting, clean grid layout, vector UI elements.",
            "business": "Minimal business presentation, neutral gray and navy palette, crisp typography, clean whitespace, subtle shadows, professional tone.",
            "education": "Education-friendly presentation, warm and approachable palette, clear icons, paper-like textures, tidy layout, soft lighting.",
            "healthcare": "Healthcare presentation, clean white and teal palette, sterile and calm atmosphere, soft diffused lighting, minimalist medical icons.",
            "finance": "Financial presentation, deep navy and gold accents, structured grids, sharp contrasts, premium corporate feel, restrained textures.",
            "agriculture": "Agriculture presentation, earthy green and brown palette, natural textures, sunlight atmosphere, organic shapes and fields imagery.",
            "sustainability": "Sustainability presentation, green and blue palette, eco-friendly motifs, natural light, recycled paper texture.",
            "consumer": "Consumer brand presentation, vibrant yet balanced palette, bold imagery, rounded shapes, modern lifestyle vibe.",
            "creative": "Creative presentation, colorful gradients, playful shapes, dynamic composition, artistic mood.",
            "saas": "SaaS product presentation, light background, soft gradients, bento layouts, clean cards, modern UI feel.",
            "government": "Government presentation, stable and formal palette, conservative layout, clear hierarchy, low-saturation colors.",
            "industrial": "Industrial presentation, steel gray and amber accents, geometric structure, robust textures, technical diagrams style.",
        }
        if not style_preset_id:
            return ""
        return presets.get(style_preset_id, "")

    def _trim_content_summary(self, content_summary: str, language: str, presentation_mode: str) -> str:
        if not content_summary:
            return content_summary

        is_ch = language == "zh"
        if presentation_mode == "slides":
            max_items = 5
            min_items = 3
            max_total = 70 if is_ch else 45
            max_item_len = 12 if is_ch else 10
        else:
            max_items = 6
            min_items = 4
            max_total = 120 if is_ch else 70
            max_item_len = 18 if is_ch else 14

        lines = [line.strip(" -•\t") for line in content_summary.splitlines() if line.strip()]
        if not lines:
            return content_summary

        # Trim per item length
        trimmed_lines = []
        for line in lines:
            if is_ch:
                if len(line) > max_item_len:
                    line = line[:max_item_len] + "…"
            else:
                words = line.split()
                if len(words) > max_item_len:
                    line = " ".join(words[:max_item_len]) + "…"
            trimmed_lines.append(line)

        # Enforce item count
        if len(trimmed_lines) > max_items:
            trimmed_lines = trimmed_lines[:max_items]
        elif len(trimmed_lines) < min_items:
            trimmed_lines = trimmed_lines[:]

        # Enforce total length
        def total_len(items):
            if is_ch:
                return sum(len(i) for i in items)
            return sum(len(i.split()) for i in items)

        while trimmed_lines and total_len(trimmed_lines) > max_total:
            trimmed_lines[-1] = trimmed_lines[-1][:-1] if is_ch else " ".join(trimmed_lines[-1].split()[:-1])
            if not trimmed_lines[-1]:
                trimmed_lines.pop()

        return "\n".join(f"- {line}" for line in trimmed_lines)

    def _get_language_labels(self, language: str):
        mapping = {
            "zh": ("Chinese", "中文"),
            "en": ("English", "English"),
            "ja": ("Japanese", "日本語"),
            "ko": ("Korean", "한국어"),
            "fr": ("French", "Français"),
            "es": ("Spanish", "Español"),
            "de": ("German", "Deutsch"),
            "pt": ("Portuguese", "Português"),
        }
        return mapping.get(language, ("English", "English"))

    def _expand_topic_keywords(self, client, topic: str, language: str = "zh") -> str:
        """基于主题生成关键词/同义表达清单，用于强化相关性"""
        if not topic:
            return ""
        lang_label, _ = self._get_language_labels(language)
        lang_instruction = "请用中文输出。" if language == "zh" else f"Please output in {lang_label}."
        system_prompt = (
            "You are a keyword extraction assistant. "
            "Output 3-5 concise keywords or short phrases. "
            "Each line one item. No explanation."
        )
        user_msg = f"主题：{topic}\n{lang_instruction}"
        result = self._call_llm(client, system_prompt, user_msg)
        if not result:
            return ""
        # 规范化为最多 5 行，去空
        items = [line.strip(" -•\t") for line in result.splitlines() if line.strip()]
        if not items:
            return ""
        return "=== 主题关键词清单 ===\n" + "\n".join(items[:5])

    def enrich_outline(self, topic: str, slides: list, language: str = "zh", presentation_mode: str = "slides", global_style_prompt: str = "", api_key: str = None, style_preset_id: str = None, previous_context: str = "", next_context: str = ""):
        """对用户编辑后的大纲进行补全：生成 visual_subject 与 narrative_bridge。"""
        client = self._get_client(api_key)
        lang_label, lang_short = self._get_language_labels(language)
        mode_label = "演示用幻灯片" if presentation_mode == "slides" else "详细演示文稿"
        preset_style = self._resolve_style_preset(style_preset_id)
        effective_style = preset_style or global_style_prompt
        narrative_rule = (
            "For each slide, narrative_bridge MUST include BOTH: "
            "(1) how it continues from previous slide, and "
            "(2) how it leads into the next slide. "
            "Use two short clauses separated by a semicolon."
        ) if presentation_mode == "script" else (
            "For each slide, narrative_bridge should explain how it connects to the previous slide in one concise sentence."
        )

        system_prompt = f"""You are a PPT outline refiner.

# LANGUAGE RULES
- title/content_summary/narrative_bridge MUST be in {lang_label}.
- visual_subject MUST be in English.

# MODE: {mode_label}
{narrative_rule}

# OUTPUT JSON (strict)
{{
  "slides": [
    {{
      "index": 0,
      "title": "...",
      "content_summary": "...",
      "narrative_bridge": "...",
      "visual_subject": "..."
    }}
  ]
}}"""

        user_msg = f"""主题: {topic}
输出语言: {lang_short}
模式: {mode_label}
全局风格提示词: {effective_style}

上一页上下文（可为空）：
{previous_context}

下一页上下文（可为空）：
{next_context}

以下是用户确认后的幻灯片大纲（可能缺少 narrative_bridge/visual_subject）：
{json.dumps(slides, ensure_ascii=False)}
"""
        content = self._call_llm(client, system_prompt, user_msg, json_mode=True)
        if not content:
            return {"error": "Empty response from outline refiner"}
        try:
            data = json.loads(content)
            return data
        except Exception as e:
            return {"error": f"Invalid JSON response: {e}"}

    def _generate_style(self, client, topic: str, audience: str = "", scene: str = "", attention: str = "", purpose: str = "", style_preset: str = ""):
        if style_preset:
            return {
                "global_style_prompt": style_preset,
                "style_meta": {"preset": "custom"},
            }
        user_msg = f"""主题: {topic}
受众: {audience}
场景: {scene}
注意事项: {attention}
目标: {purpose}
"""
        try:
            content = self._call_llm(client, STYLE_AGENT_PROMPT, user_msg, json_mode=True)
            if not content:
                return {
                    "global_style_prompt": "Clean modern presentation style, balanced color palette, soft lighting, minimal noise, professional layout.",
                    "style_meta": {},
                }
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError("Style agent response not dict")
            if "global_style_prompt" not in data:
                data["global_style_prompt"] = "Clean modern presentation style, balanced color palette, soft lighting, minimal noise, professional layout."
            if "style_meta" not in data or not isinstance(data["style_meta"], dict):
                data["style_meta"] = {}
            return data
        except Exception as e:
            print(f"[Planner] Style agent failed: {e}")
            return {
                "global_style_prompt": "Clean modern presentation style, balanced color palette, soft lighting, minimal noise, professional layout.",
                "style_meta": {},
            }

    def _extract_content(self, client, context_text: str, topic: str, language: str = "zh") -> str:
        """Content Agent: 提炼用户上传的文档内容"""
        lang_label, _ = self._get_language_labels(language)
        lang_instruction = "请用中文输出。" if language == "zh" else f"Please output in {lang_label}."
        user_msg = f"主题：{topic}\n{lang_instruction}\n\n以下是用户提供的原始材料，请提炼为适合 PPT 演示的内容：\n\n{context_text}"
        result = self._call_llm(client, CONTENT_AGENT_PROMPT, user_msg)
        return result or context_text

    def _generate_hook_titles(self, client, topic: str, refined_content: str = "", language: str = "zh", ask_map_context: str = "", keyword_context: str = "") -> str:
        """Hook Agent: 生成封面标题候选"""
        lang_label, _ = self._get_language_labels(language)
        lang_instruction = "请用中文生成标题。" if language == "zh" else f"Please generate titles in {lang_label}."
        user_msg = f"PPT 主题：{topic}\n{lang_instruction}"
        if refined_content:
            user_msg += f"\n\n提炼后的核心内容摘要：\n{refined_content[:1000]}"
        if ask_map_context:
            user_msg += f"\n\n{ask_map_context}"
        if keyword_context:
            user_msg += f"\n\n{keyword_context}"
        result = self._call_llm(client, HOOK_AGENT_PROMPT, user_msg)
        return result or topic

    def _generate_structure(self, client, topic: str, refined_content: str = "", language: str = "zh", ask_map_context: str = "", keyword_context: str = "") -> str:
        """Structure Agent: 生成 PPT 逻辑框架"""
        lang_label, _ = self._get_language_labels(language)
        lang_instruction = "请用中文输出框架结构。" if language == "zh" else f"Please output the framework in {lang_label}."
        user_msg = f"PPT 主题：{topic}\n{lang_instruction}"
        if refined_content:
            user_msg += f"\n\n提炼后的内容：\n{refined_content[:2000]}"
        if ask_map_context:
            user_msg += f"\n\n{ask_map_context}"
        if keyword_context:
            user_msg += f"\n\n{keyword_context}"
        result = self._call_llm(client, STRUCTURE_AGENT_PROMPT, user_msg)
        return result or ""

    def generate_ppt_outline(self, topic: str, page_count: int = 5, context_text: str = "", language: str = "zh", api_key: str = None, audience: str = "", scene: str = "", attention: str = "", purpose: str = "", presentation_mode: str = "slides", style_preset_id: str = None, progress_cb=None):
        """
        三阶段 Agent 协作生成 PPT 大纲。
        1. Content Agent: 提炼用户上传的文档（如有）
        2. Hook Agent + Structure Agent: 生成标题和框架
        3. 最终整合为带 visual_prompt 的 JSON 大纲
        """
        client = self._get_client(api_key)
        lang_label, lang_short = self._get_language_labels(language)

        try:
            print(f"[Planner] Planning PPT for: {topic} (language={language})")

            # === 构建 ASK MAP 上下文 ===
            ask_map_context = self._build_ask_map_context(audience, scene, attention, purpose)
            if ask_map_context:
                print(f"[Planner] ASK MAP context provided")

            # === 主题关键词扩展（强化相关性）===
            keyword_context = self._expand_topic_keywords(client, topic, language)

            # === 阶段 1: Content Agent 提炼内容（如有上传文档）===
            if progress_cb:
                progress_cb("extract_content", "正在提炼主题", 20)
            refined_content = ""
            if context_text and context_text.strip():
                print("[Planner] Stage 1: Content Agent extracting...")
                refined_content = self._extract_content(client, context_text, topic, language)
                print(f"[Planner] Content extracted: {len(refined_content)} chars")

            # === 阶段 2: Hook Agent 生成标题 ===
            if progress_cb:
                progress_cb("hook_titles", "正在生成标题", 30)
            print("[Planner] Stage 2: Hook Agent generating titles...")
            hook_titles = self._generate_hook_titles(client, topic, refined_content, language, ask_map_context, keyword_context)
            print(f"[Planner] Hook titles: {hook_titles[:200]}")

            # === 阶段 3: Structure Agent 生成框架 ===
            if progress_cb:
                progress_cb("structure", "正在规划结构", 50)
            print("[Planner] Stage 3: Structure Agent designing framework...")
            structure = self._generate_structure(client, topic, refined_content, language, ask_map_context, keyword_context)
            print(f"[Planner] Structure: {structure[:200]}")

            # === 阶段 3.5: Style Agent 生成全局风格 ===
            if progress_cb:
                progress_cb("style", "正在生成视觉风格", 60)
            print("[Planner] Stage 3.5: Style Agent generating global style...")
            style_data = self._generate_style(
                client,
                topic=topic,
                audience=audience,
                scene=scene,
                attention=attention,
                purpose=purpose,
                style_preset=self._resolve_style_preset(style_preset_id),
            )
            global_style_prompt = style_data.get("global_style_prompt", "")
            style_meta = style_data.get("style_meta", {})

            # === 阶段 4: 最终整合 - 生成完整的 visual_prompt JSON ===
            if progress_cb:
                progress_cb("integrate", "正在生成大纲", 70)
            print("[Planner] Stage 4: Final integration...")
            result = self._integrate_final_outline(
                client, topic, hook_titles, structure,
                refined_content, page_count, language, ask_map_context, keyword_context,
                global_style_prompt, style_meta, presentation_mode
            )
            if progress_cb:
                progress_cb("done", "规划完成", 100)
            return result

        except Exception as e:
            print(f"[Planner] Error: {type(e).__name__}: {e}")
            return {"error": str(e)}

    def _integrate_final_outline(self, client, topic, hook_titles, structure, refined_content, page_count, language, ask_map_context: str = "", keyword_context: str = "", global_style_prompt: str = "", style_meta: dict = None, presentation_mode: str = "slides"):
        """最终整合：将三个 Agent 的输出合并为带 visual_subject 的 JSON"""
        lang_label, lang_short = self._get_language_labels(language)
        style_meta = style_meta or {}
        mode_label = "演示用幻灯片" if presentation_mode == "slides" else "详细演示文稿"
        content_rules = (
            "- 内容精简：每页 2-4 个要点，标题清晰，避免长句。\n"
            "- 内容字数控制在 40-80 字或 25-40 words 以内。\n"
        ) if presentation_mode == "slides" else (
            "- 内容更完整：每页 4-6 个要点，允许更具体说明。\n"
            "- 内容字数控制在 80-160 字或 50-90 words 以内。\n"
        )

        narrative_rule = (
            "For each slide, narrative_bridge MUST include BOTH: "
            "(1) how it continues from previous slide, and "
            "(2) how it leads into the next slide. "
            "Use two short clauses separated by a semicolon."
        ) if presentation_mode == "script" else (
            "For each slide, narrative_bridge should explain how it connects to the previous slide in one concise sentence."
        )

        system_prompt = f"""{MASTER_SYSTEM_PROMPT}

You are now the Final Integration Agent. Combine the outputs from Hook Agent, Structure Agent, and Content Agent into a complete PPT plan.

# LANGUAGE RULE (CRITICAL)
- ALL text on slides (title, content_summary, narrative_bridge) MUST be in {lang_label}.
- ALL visual_subject MUST be in English for image generation.

# RULES FOR SLIDE COUNT (STRICT)
1. You MUST output exactly {page_count} slides, no more, no less.
2. The "slides" array in your JSON must have exactly {page_count} items.

# RULES FOR STRUCTURE
1. Slide 1 (Index 0): MUST be a Title/Cover Slide using the best Hook title.
2. Middle Slides: Follow the Structure Agent's framework.
3. Last Slide: Strategic Closing.

# CONTENT DENSITY RULES (MODE: {mode_label})
{content_rules}

# NARRATIVE BRIDGE RULES
{narrative_rule}

# OUTPUT FORMAT (strict JSON)
{{
    "slides": [
        {{
            "index": 0,
            "title": "...",
            "content_summary": "...",
            "narrative_bridge": "...",
            "visual_subject": "..."
        }}
    ]
}}"""

        user_msg = f"""主题: {topic}
目标页数: {page_count}
输出语言: {lang_short}
模式: {mode_label}
全局风格提示词: {global_style_prompt}
风格元信息: {json.dumps(style_meta, ensure_ascii=False)}

=== Hook Agent 生成的标题候选 ===
{hook_titles}

=== Structure Agent 生成的框架 ===
{structure}
"""
        if refined_content:
            user_msg += f"\n=== Content Agent 提炼的内容 ===\n{refined_content[:3000]}"
        if ask_map_context:
            user_msg += f"\n\n{ask_map_context}"
        if keyword_context:
            user_msg += f"\n\n{keyword_context}"

        content = self._call_llm(client, system_prompt, user_msg, json_mode=True)
        if not content:
            return {"error": "Empty response from integration agent"}
        result = json.loads(content)
        slides_list = result.get("slides", [])
        if len(slides_list) != page_count:
            print(f"[Planner] Slide count mismatch: expected {page_count}, got {len(slides_list)}")
            return {"error": f"Slide count mismatch: expected {page_count} slides, got {len(slides_list)}"}
        result["global_style_prompt"] = global_style_prompt
        result["style_meta"] = style_meta
        result["presentation_mode"] = presentation_mode
        return result

    def plan_insertion_prompts(self, user_requirement: str, previous_context: str = "", api_key: str = None):
        """插入模式的微型规划。"""
        client = self._get_client(api_key)

        system_prompt = """You are a Presentation Assistant. The user wants to INSERT new slides.

1. Analyze request to determine slide count (default 1).
2. Generate visual_prompt for each slide.
3. Style Rule: Modern Tech / Internet style. Light background, clean UI elements, soft shadows.
4. Maintain consistency with 'Previous Context' style.

Output strictly in JSON:
{
    "slides_to_insert": [ { "visual_prompt": "..." } ]
}"""

        user_msg = f"Request: {user_requirement}\nPrevious Slide Context: {previous_context}"

        try:
            content = self._call_llm(client, system_prompt, user_msg, json_mode=True)
            if not content:
                return [f"A clean modern presentation slide. {user_requirement}"]
            data = json.loads(content)
            return [item["visual_prompt"] for item in data.get("slides_to_insert", [])]
        except Exception as e:
            print(f"Insertion plan failed: {e}")
            return [f"A clean modern presentation slide. {user_requirement}"]

    def generate_short_title(self, user_input: str, api_key: str = None):
        """生成短标题"""
        client = self._get_client(api_key)
        try:
            content = self._call_llm(
                client,
                "Summarize user input into a concise title (max 6 words). Output raw text only, no quotes.",
                user_input,
            )
            return content or "New Project"
        except:
            return "New Project"
