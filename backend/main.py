import os
import base64
import uvicorn
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import json
import threading
import time
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from file_handler import FileHandler
from llm_planner import LLMPlanner
from image_gen import ImageGenerator
from database import (
    get_db,
    init_db,
    SessionLocal,
    migrate_add_deleted_at,
    migrate_add_slide_deleted_at,
    migrate_add_generation_fields,
    migrate_add_params,
    migrate_add_topic,
    migrate_add_user_id,
    migrate_points_to_scores,
    migrate_add_is_published,
    migrate_create_score_logs,
    migrate_add_score_logs_balance,
    migrate_add_score_logs_type,
    seed_default_admin,
    seed_system_config,
    seed_default_user,
)
from repository import (
    list_presentations,
    create_presentation,
    get_presentation,
    update_presentation,
    delete_presentation,
    restore_presentation,
    list_deleted_presentations,
    permanently_delete_presentation,
    clear_recycle_bin,
    set_presentation_published,
    list_published_presentations,
    get_presentation_public,
    add_slide_version,
    update_generation_progress,
    get_generation_progress,
    add_slide_version_by_slide_id,
    insert_slide_at_index,
    delete_slide_by_id,
    list_deleted_slides,
    restore_slide,
    set_slide_active_version,
    delete_slide_version,
    get_previous_slide_prompt,
    get_slide_context_messages,
    get_slide_by_id,
    get_slide_by_position,
    _slide_to_dict,
    _version_to_dict,
    get_user_by_username,
    create_user,
    use_invite_code,
    get_invite_code_by_code,
    get_user_scores,
    deduct_scores,
    add_scores,
    get_scores_per_slide,
    get_register_bonus_scores,
    record_score_log,
    get_config,
    set_config,
    use_redemption_code,
    create_redemption_codes,
    list_redemption_codes_admin,
    create_invite_code_by_user,
    count_invite_codes_by_user,
    list_invite_codes_by_user,
    create_invite_codes_by_admin,
    list_invite_codes_admin,
    list_all_presentations_admin,
    get_admin_by_username,
    list_users_admin,
    delete_redemption_code_admin,
    delete_invite_code_admin,
    list_score_logs_by_user,
    list_score_logs_admin,
)
from utils import save_image_locally, save_image_locally_sync
from auth import (
    create_access_token,
    get_current_user,
    get_current_admin,
    verify_password,
    hash_password,
)

load_dotenv()

app = FastAPI(title="AI PPT Agent Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_cors_headers_to_images(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/images/"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


os.makedirs("storage/images", exist_ok=True)
app.mount("/images", StaticFiles(directory="storage/images"), name="images")

planner = LLMPlanner()
image_gen = ImageGenerator()

PLAN_PROGRESS = {}
PLAN_RESULTS = {}


@app.on_event("startup")
def startup():
    init_db()
    try:
        migrate_add_deleted_at()
        migrate_add_slide_deleted_at()
        migrate_add_generation_fields()
        migrate_add_params()
        migrate_add_topic()
        migrate_add_user_id()
        migrate_points_to_scores()
        migrate_add_is_published()
        migrate_create_score_logs()
        migrate_add_score_logs_balance()
        migrate_add_score_logs_type()
        seed_default_admin()
        seed_system_config()
        seed_default_user()
    except Exception:
        pass


# --- Pydantic models ---


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    invite_code: str
    username: str
    password: str


class RedeemRequest(BaseModel):
    code: str


class CreatePresentationRequest(BaseModel):
    topic: str = "Untitled PPT"


class UpdatePresentationRequest(BaseModel):
    title: Optional[str] = None
    global_style: Optional[str] = None


class PlanRequest(BaseModel):
    topic: str
    page_count: int = Field(default=12, ge=1, le=50)
    context_text: Optional[str] = ""
    language: Optional[str] = "zh"
    presentation_mode: Optional[str] = "slides"
    style_preset_id: Optional[str] = None
    audience: Optional[str] = ""
    scene: Optional[str] = ""
    attention: Optional[str] = ""
    purpose: Optional[str] = ""


class GenerateBatchRequest(BaseModel):
    slides: List[dict]  # [ {"index": 0, "visual_prompt": "..." }, ... ]


class GenerateFromOutlineRequest(BaseModel):
    presentation_mode: Optional[str] = "slides"
    language: Optional[str] = "zh"
    topic: Optional[str] = None
    global_style_prompt: str
    style_preset_id: Optional[str] = None
    slides: List[dict]


class InsertSlideRequest(BaseModel):
    position: int
    prompt: str


class InsertSlideByOutlineRequest(BaseModel):
    position: int
    title: str
    content_summary: str
    presentation_mode: Optional[str] = "slides"
    language: Optional[str] = "zh"


class CreateVersionRequest(BaseModel):
    prompt: str
    is_modification: bool = False
    base_image_url: Optional[str] = None


class SetActiveVersionRequest(BaseModel):
    version_id: str


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminPasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UserPasswordRequest(BaseModel):
    old_password: str
    new_password: str


class AdminCreateUserRequest(BaseModel):
    username: str
    password: str
    initial_scores: Optional[int] = 0


class AdminRedemptionCodesRequest(BaseModel):
    scores: int
    count: int


class AdminInviteCodesRequest(BaseModel):
    count: int


class AdminConfigUpdateRequest(BaseModel):
    scores_per_slide: Optional[int] = None
    register_bonus_scores: Optional[int] = None


# --- Helpers ---

def encode_local_image(path_str: str) -> Optional[str]:
    try:
        if "/images/" in path_str:
            clean_path = path_str.split("/images/")[-1]
        elif "images/" in path_str:
            clean_path = path_str.split("images/")[-1]
        else:
            clean_path = path_str
        clean_path = clean_path.lstrip("/").lstrip("\\")
        file_path = os.path.join("storage", "images", clean_path)
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            return None
        with open(file_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Base64 encoding error: {e}")
        return None


# --- API ---

@app.get("/")
def health_check():
    return {"status": "running"}


# === Auth (user) ===

@app.post("/auth/register")
def api_register(req: RegisterRequest, db: Session = Depends(get_db)):
    inv = get_invite_code_by_code(db, req.invite_code)
    if not inv or inv.used_by_user_id is not None:
        raise HTTPException(400, "Invalid or already used invite code")
    if get_user_by_username(db, req.username):
        raise HTTPException(400, "Username already exists")
    initial_scores = get_register_bonus_scores(db)
    user = create_user(db, req.username, hash_password(req.password), initial_scores=initial_scores)
    if not user:
        raise HTTPException(400, "Failed to create user")
    use_invite_code(db, req.invite_code, user.id)
    # 记录注册赠送积分日志
    if initial_scores > 0:
        record_score_log(
            db,
            user.id,
            initial_scores,
            balance=user.scores,
            prompt="新用户注册赠送",
            image_path=None,
            log_type="recharge",
        )
    token = create_access_token(sub=user.id, role="user")
    scores_per_slide = get_scores_per_slide(db)
    return {
        "access_token": token,
        "user": {"id": user.id, "username": user.username, "scores": user.scores, "scores_per_slide": scores_per_slide},
    }


@app.post("/auth/login")
def api_login(req: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, req.username)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid username or password")
    token = create_access_token(sub=user.id, role="user")
    scores_per_slide = get_scores_per_slide(db)
    return {
        "access_token": token,
        "user": {"id": user.id, "username": user.username, "scores": user.scores, "scores_per_slide": scores_per_slide},
    }


@app.get("/auth/me")
def api_me(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    scores = get_user_scores(db, current_user.id)
    scores_per_slide = get_scores_per_slide(db)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "scores": scores,
        "scores_per_slide": scores_per_slide,
    }


# === User (member center: redeem, invite codes) ===

@app.post("/user/redeem")
def api_user_redeem(req: RedeemRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    result = use_redemption_code(db, req.code, current_user.id)
    if result[0] == "already_used":
        raise HTTPException(400, "兑换码已被使用")
    if result[0] == "invalid":
        raise HTTPException(400, "兑换码无效")
    # result == ("ok", added)
    new_balance = get_user_scores(db, current_user.id)
    # 记录兑换码充值积分日志
    record_score_log(
        db,
        current_user.id,
        result[1],
        balance=new_balance,
        prompt="兑换码充值",
        image_path=None,
        log_type="recharge",
    )
    return {"scores": new_balance, "added": result[1]}


@app.post("/user/invite-codes")
def api_user_create_invite_code(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if count_invite_codes_by_user(db, current_user.id) >= 3:
        raise HTTPException(400, "Maximum 3 invite codes per user")
    code = create_invite_code_by_user(db, current_user.id)
    if not code:
        raise HTTPException(400, "Cannot create more invite codes")
    return {"code": code}


@app.get("/user/invite-codes")
def api_user_list_invite_codes(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return {"invite_codes": list_invite_codes_by_user(db, current_user.id)}


@app.patch("/user/me/password")
def api_user_change_password(
    req: UserPasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(400, "当前密码错误")
    from models import User as UserModel

    user_row = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user_row:
        raise HTTPException(404, "用户不存在")
    user_row.password_hash = hash_password(req.new_password)
    db.commit()
    return {"status": "success"}


@app.get("/user/score-logs")
def api_user_score_logs(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """获取当前用户的积分日志。"""
    items, total = list_score_logs_by_user(db, current_user.id, skip=skip, limit=limit)
    return {"score_logs": items, "total": total}


# === Presentations ===

@app.get("/presentations")
def api_list_presentations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return list_presentations(db, user_id=current_user.id)


@app.post("/presentations")
def api_create_presentation(req: CreatePresentationRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    pid = create_presentation(db, topic=req.topic, title=req.topic, user_id=current_user.id)
    return {"id": pid, "presentation_id": pid, "message": "Presentation created"}


@app.get("/presentations/deleted")
def api_list_deleted_presentations(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return {"presentations": list_deleted_presentations(db, user_id=current_user.id)}


@app.delete("/presentations/deleted")
def api_clear_recycle_bin(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """清空回收站：永久删除当前用户已软删除的演示文稿。"""
    count = clear_recycle_bin(db, user_id=current_user.id)
    return {"status": "success", "deleted_count": count}


@app.get("/presentations/{presentation_id}")
def api_get_presentation(presentation_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    data = get_presentation(db, presentation_id, user_id=current_user.id)
    if not data:
        raise HTTPException(404, "Presentation not found")
    return data


@app.patch("/presentations/{presentation_id}")
def api_update_presentation(presentation_id: str, req: UpdatePresentationRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    data = get_presentation(db, presentation_id, user_id=current_user.id)
    if not data:
        raise HTTPException(404, "Presentation not found")
    ok = update_presentation(db, presentation_id, title=req.title, global_style=req.global_style)
    if not ok:
        raise HTTPException(404, "Presentation not found")
    return {"status": "success"}


@app.delete("/presentations/{presentation_id}")
def api_delete_presentation(presentation_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    data = get_presentation(db, presentation_id, user_id=current_user.id)
    if not data:
        raise HTTPException(404, "Presentation not found")
    ok = delete_presentation(db, presentation_id)
    if not ok:
        raise HTTPException(404, "Presentation not found")
    return {"status": "success"}


@app.post("/presentations/{presentation_id}/restore")
def api_restore_presentation(presentation_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    data = get_presentation(db, presentation_id, user_id=current_user.id)
    if not data:
        raise HTTPException(404, "Presentation not found")
    ok = restore_presentation(db, presentation_id)
    if not ok:
        raise HTTPException(404, "Presentation not found")
    return {"status": "success"}


@app.delete("/presentations/{presentation_id}/permanent")
def api_permanently_delete_presentation(presentation_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    data = get_presentation(db, presentation_id, user_id=current_user.id)
    if not data:
        raise HTTPException(404, "Presentation not found")
    ok = permanently_delete_presentation(db, presentation_id)
    if not ok:
        raise HTTPException(404, "Presentation not found or not in recycle bin")
    return {"status": "success"}


@app.post("/presentations/{presentation_id}/publish")
def api_publish_presentation(presentation_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """发布或取消发布演示文稿。"""
    # 先检查演示文稿是否存在且属于当前用户
    data = get_presentation(db, presentation_id, user_id=current_user.id)
    if not data:
        raise HTTPException(404, "Presentation not found")
    # 获取当前发布状态
    from models import Presentation
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        raise HTTPException(404, "Presentation not found")
    current_status = getattr(p, "is_published", None) or 0
    new_status = 1 if current_status == 0 else 0
    ok = set_presentation_published(db, presentation_id, new_status == 1)
    if not ok:
        raise HTTPException(404, "Presentation not found")
    return {"status": "success", "is_published": new_status}


# === Gallery (Public) ===

@app.get("/gallery")
def api_list_gallery(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """获取作品广场列表（公开，无需认证）。"""
    presentations = list_published_presentations(db, skip=skip, limit=limit)
    return {"presentations": presentations}


@app.get("/gallery/{presentation_id}")
def api_get_gallery_presentation(presentation_id: str, db: Session = Depends(get_db)):
    """获取作品广场中的演示文稿详情（公开，无需认证）。"""
    data = get_presentation_public(db, presentation_id)
    if not data:
        raise HTTPException(404, "Presentation not found or not published")
    return data


# === Plan & Batch Generate ===

@app.post("/presentations/{presentation_id}/plan")
async def api_plan(presentation_id: str, req: PlanRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    pres = get_presentation(db, presentation_id, user_id=current_user.id)
    if not pres:
        raise HTTPException(404, "Presentation not found")
    auto_title = None
    try:
        if hasattr(planner, "generate_short_title"):
            auto_title = planner.generate_short_title(req.topic)
            update_presentation(db, presentation_id, title=auto_title)
    except Exception as e:
        print(f"Auto-title failed: {e}")
    PLAN_PROGRESS[presentation_id] = {
        "stage": "parse_params",
        "label": "正在解析参数",
        "progress": 10,
    }
    def _progress_cb(stage, label, progress):
        PLAN_PROGRESS[presentation_id] = {
            "stage": stage,
            "label": label,
            "progress": progress,
        }
    plan = await asyncio.to_thread(
        planner.generate_ppt_outline,
        topic=req.topic,
        page_count=req.page_count,
        context_text=req.context_text or "",
        language=req.language or "zh",
        audience=req.audience or "",
        scene=req.scene or "",
        attention=req.attention or "",
        purpose=req.purpose or "",
        presentation_mode=req.presentation_mode or "slides",
        style_preset_id=req.style_preset_id,
        progress_cb=_progress_cb,
    )
    if "error" in plan:
        PLAN_PROGRESS[presentation_id] = {
            "stage": "failed",
            "label": "规划失败",
            "progress": 100,
        }
        raise HTTPException(500, detail=plan["error"])
    slides_list = plan.get("slides", [])
    if len(slides_list) != req.page_count:
        raise HTTPException(
            500,
            detail=f"Plan must return exactly {req.page_count} slides, got {len(slides_list)}",
        )
    if plan.get("global_style_prompt"):
        update_presentation(db, presentation_id, global_style=plan["global_style_prompt"])
    params_json = json.dumps({
        "language": req.language or "zh",
        "presentation_mode": req.presentation_mode or "slides",
        "style_preset_id": req.style_preset_id or "",
        "audience": req.audience or "",
        "scene": req.scene or "",
        "attention": req.attention or "",
        "purpose": req.purpose or "",
        "page_count": req.page_count,
        "outline": plan.get("slides", []),
    }, ensure_ascii=False)
    update_presentation(db, presentation_id, params=params_json)
    if auto_title:
        plan["session_title"] = auto_title
    PLAN_RESULTS[presentation_id] = plan
    PLAN_PROGRESS[presentation_id] = {
        "stage": "done",
        "label": "规划完成",
        "progress": 100,
    }
    return plan


def _run_generation_task(presentation_id: str, slides: list, user_id: Optional[str] = None):
    """后台任务：按序生成每张幻灯片，并更新进度。每成功生成一张扣减 user 积分（若已登录）。"""
    db = SessionLocal()
    scores_per_slide = get_scores_per_slide(db) if user_id else 0
    try:
        if slides:
            try:
                params_json = json.dumps({"outline": slides}, ensure_ascii=False)
                update_presentation(db, presentation_id, params=params_json)
            except Exception:
                pass
        total = len([
            s for s in slides
            if (s.get("visual_prompt") or s.get("prompt") or s.get("visual_subject") or s.get("global_style_prompt") or "")
        ])
        if total == 0:
            update_generation_progress(db, presentation_id, "completed", 0, 0)
            return
        prev_prompt = None
        completed = 0
        for i, item in enumerate(slides):
            if item.get("_generated"):
                continue
            prompt = item.get("visual_prompt") or item.get("prompt") or ""
            has_plan_fields = bool(item.get("visual_subject")) or bool(item.get("global_style_prompt"))
            if not prompt and not has_plan_fields:
                continue
            try:
                if has_plan_fields:
                    image_url = image_gen.generate_slide_image_from_plan(
                        slide_data=item,
                        global_style_prompt=item.get("global_style_prompt", ""),
                        presentation_mode=item.get("presentation_mode", "slides"),
                    )
                else:
                    image_url = image_gen.generate_slide_image(
                        prompt=prompt,
                        reference_style_prompt=prev_prompt,
                    )
                if not image_url:
                    continue
                local_path = save_image_locally_sync(image_url, session_id=presentation_id)
                if not local_path:
                    continue
                version_prompt = prompt
                if has_plan_fields and not prompt:
                    version_prompt = item.get("visual_subject", "") or "Generated from plan"
                version_id = add_slide_version(
                    db, presentation_id, i, image_path=local_path, prompt=version_prompt
                )
                if version_id:
                    if user_id and scores_per_slide > 0:
                        if deduct_scores(db, user_id, scores_per_slide):
                            balance = get_user_scores(db, user_id)
                            record_score_log(db, user_id, scores_per_slide, balance=balance, prompt=version_prompt, image_path=local_path)
                    item["_generated"] = True
                    completed += 1
                    update_generation_progress(db, presentation_id, "generating", completed, total)
                prev_prompt = prompt or item.get("visual_subject") or prev_prompt
            except Exception as e:
                update_generation_progress(
                    db, presentation_id, "failed", completed, total, error=str(e)
                )
                return
        if completed >= total:
            update_generation_progress(db, presentation_id, "completed", completed, total)
        else:
            update_generation_progress(db, presentation_id, "failed", completed, total, error="Generation interrupted")
    except Exception as e:
        try:
            update_generation_progress(
                db, presentation_id, "failed", 0, len(slides), error=str(e)
            )
        except Exception:
            pass
    finally:
        db.close()


@app.post("/presentations/{presentation_id}/generate")
async def api_generate_batch(
    presentation_id: str,
    req: GenerateBatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    pres = get_presentation(db, presentation_id, user_id=current_user.id)
    if not pres:
        raise HTTPException(404, "Presentation not found")
    slides = req.slides
    total = len([
        s for s in slides
        if (s.get("visual_prompt") or s.get("prompt") or s.get("visual_subject") or s.get("global_style_prompt") or "")
    ])
    if total == 0:
        return JSONResponse(status_code=202, content={"status": "accepted"})
    scores_per = get_scores_per_slide(db)
    need_scores = total * scores_per
    if get_user_scores(db, current_user.id) < need_scores:
        raise HTTPException(402, f"积分不足：需要 {need_scores} 积分，当前仅 {get_user_scores(db, current_user.id)}")
    update_generation_progress(db, presentation_id, "generating", 0, total)
    background_tasks.add_task(_run_generation_task, presentation_id, slides, current_user.id)
    return JSONResponse(status_code=202, content={"status": "accepted"})


@app.post("/presentations/{presentation_id}/generate-from-outline")
async def api_generate_from_outline(
    presentation_id: str,
    req: GenerateFromOutlineRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    pres = get_presentation(db, presentation_id, user_id=current_user.id)
    if not pres:
        raise HTTPException(404, "Presentation not found")
    topic = req.topic or pres.get("topic") or pres.get("title") or "Untitled PPT"
    presentation_mode = req.presentation_mode or "slides"
    language = req.language or "zh"
    enriched = planner.enrich_outline(
        topic=topic,
        slides=req.slides,
        language=language,
        presentation_mode=presentation_mode,
        global_style_prompt=req.global_style_prompt,
        style_preset_id=req.style_preset_id,
    )
    if "error" in enriched:
        raise HTTPException(500, detail=enriched["error"])
    enriched_slides = enriched.get("slides", [])
    slides_for_gen = []
    for idx, slide in enumerate(enriched_slides):
        slide["index"] = idx
        slide["global_style_prompt"] = req.global_style_prompt
        slide["presentation_mode"] = presentation_mode
        slides_for_gen.append(slide)
    if req.global_style_prompt:
        update_presentation(db, presentation_id, global_style=req.global_style_prompt)
    params_json = json.dumps({
        "language": language,
        "presentation_mode": presentation_mode,
        "style_preset_id": req.style_preset_id or "",
        "page_count": len(enriched_slides),
        "global_style_prompt": req.global_style_prompt,
        "outline": slides_for_gen,
    }, ensure_ascii=False)
    update_presentation(db, presentation_id, params=params_json)
    total = len([
        s for s in slides_for_gen
        if (s.get("visual_prompt") or s.get("prompt") or s.get("visual_subject") or s.get("global_style_prompt") or "")
    ])
    if total == 0:
        return JSONResponse(status_code=202, content={"status": "accepted"})
    scores_per = get_scores_per_slide(db)
    need_scores = total * scores_per
    if get_user_scores(db, current_user.id) < need_scores:
        raise HTTPException(402, f"积分不足：需要 {need_scores} 积分，当前仅 {get_user_scores(db, current_user.id)}")
    update_generation_progress(db, presentation_id, "generating", 0, total)
    background_tasks.add_task(_run_generation_task, presentation_id, slides_for_gen, current_user.id)
    return JSONResponse(status_code=202, content={"status": "accepted"})


@app.post("/presentations/{presentation_id}/resume-generate")
async def api_resume_generate(
    presentation_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    pres = get_presentation(db, presentation_id, user_id=current_user.id)
    if not pres:
        raise HTTPException(404, "Presentation not found")
    params_raw = pres.get("params") or ""
    try:
        params = json.loads(params_raw) if params_raw else {}
    except Exception:
        params = {}
    slides_for_gen = params.get("outline", [])
    if not slides_for_gen:
        raise HTTPException(400, "No outline to resume")
    total = len([
        s for s in slides_for_gen
        if (s.get("visual_prompt") or s.get("prompt") or s.get("visual_subject") or s.get("global_style_prompt") or "")
    ])
    if total == 0:
        return JSONResponse(status_code=202, content={"status": "accepted"})
    current_done = pres.get("generation_current", 0) or 0
    remaining = total - current_done
    if remaining > 0:
        scores_per = get_scores_per_slide(db)
        need_scores = remaining * scores_per
        if get_user_scores(db, current_user.id) < need_scores:
            raise HTTPException(402, f"积分不足：需要 {need_scores} 积分，当前仅 {get_user_scores(db, current_user.id)}")
    update_generation_progress(db, presentation_id, "generating", current_done, total)
    background_tasks.add_task(_run_generation_task, presentation_id, slides_for_gen, current_user.id)
    return JSONResponse(status_code=202, content={"status": "accepted"})


@app.get("/presentations/{presentation_id}/generation-progress")
def api_get_generation_progress(presentation_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """获取演示文稿的生成进度，用于轮询。"""
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    progress = get_generation_progress(db, presentation_id)
    if not progress:
        raise HTTPException(404, "Presentation not found")
    return progress


@app.get("/presentations/{presentation_id}/plan-progress")
def api_plan_progress(presentation_id: str):
    def event_stream():
        last_payload = None
        while True:
            payload = PLAN_PROGRESS.get(presentation_id, {"stage": "idle", "label": "等待开始", "progress": 0})
            data = json.dumps(payload, ensure_ascii=False)
            if data != last_payload:
                yield f"event: progress\ndata: {data}\n\n"
                last_payload = data
            if payload.get("stage") in ("done", "failed"):
                yield "event: done\ndata: {}\n\n"
                break
            time.sleep(0.5)
    return StreamingResponse(event_stream(), media_type="text/event-stream")


# === Slides ===

@app.get("/presentations/{presentation_id}/slides/deleted")
def api_list_deleted_slides(presentation_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    return {"slides": list_deleted_slides(db, presentation_id)}


@app.post("/presentations/{presentation_id}/slides/{slide_id}/restore")
def api_restore_slide(presentation_id: str, slide_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    ok = restore_slide(db, presentation_id, slide_id)
    if not ok:
        raise HTTPException(404, "Slide not found")
    return {"status": "success"}


@app.get("/presentations/{presentation_id}/slides/{slide_id}")
def api_get_slide(presentation_id: str, slide_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        raise HTTPException(404, "Slide not found")
    return _slide_to_dict(slide)


@app.delete("/presentations/{presentation_id}/slides/{slide_id}")
def api_delete_slide(presentation_id: str, slide_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    ok = delete_slide_by_id(db, presentation_id, slide_id)
    if not ok:
        raise HTTPException(404, "Slide not found")
    return {"status": "success"}


@app.post("/presentations/{presentation_id}/slides")
async def api_insert_slide(presentation_id: str, req: InsertSlideRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    pres = get_presentation(db, presentation_id, user_id=current_user.id)
    if not pres:
        raise HTTPException(404, "Presentation not found")
    scores_per = get_scores_per_slide(db)
    if get_user_scores(db, current_user.id) < scores_per:
        raise HTTPException(402, f"积分不足：每张需 {scores_per} 积分")
    prev_prompt = get_previous_slide_prompt(db, presentation_id, current_position=req.position)
    image_url = image_gen.generate_slide_image(
        prompt=req.prompt,
        reference_style_prompt=prev_prompt,
    )
    if not image_url:
        raise HTTPException(500, "Image generation failed")
    local_path = await save_image_locally(image_url, session_id=presentation_id)
    if not local_path:
        raise HTTPException(500, "Failed to save image")
    version_id = insert_slide_at_index(db, presentation_id, req.position, local_path, req.prompt)
    if not version_id:
        raise HTTPException(500, "Failed to insert slide")
    if deduct_scores(db, current_user.id, scores_per):
        balance = get_user_scores(db, current_user.id)
        record_score_log(db, current_user.id, scores_per, balance=balance, prompt=req.prompt, image_path=local_path)
    slide = get_slide_by_position(db, presentation_id, req.position)
    return {"status": "success", "slide_id": slide.id, "version_id": version_id, "image_url": local_path}


@app.post("/presentations/{presentation_id}/slides/insert")
async def api_insert_slide_by_outline(presentation_id: str, req: InsertSlideByOutlineRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    pres = get_presentation(db, presentation_id, user_id=current_user.id)
    if not pres:
        raise HTTPException(404, "Presentation not found")
    scores_per = get_scores_per_slide(db)
    if get_user_scores(db, current_user.id) < scores_per:
        raise HTTPException(402, f"积分不足：每张需 {scores_per} 积分")

    presentation_mode = req.presentation_mode or "slides"
    language = req.language or "zh"
    prev_prompt = get_previous_slide_prompt(db, presentation_id, current_position=req.position)
    next_slide = get_slide_by_position(db, presentation_id, req.position)
    next_prompt = ""
    if next_slide and next_slide.versions:
        next_prompt = next_slide.versions[-1].prompt or ""
    enriched = planner.enrich_outline(
        topic=pres.get("topic") or pres.get("title") or "Untitled PPT",
        slides=[{
            "index": 0,
            "title": req.title,
            "content_summary": req.content_summary,
        }],
        language=language,
        presentation_mode=presentation_mode,
        global_style_prompt=pres.get("global_style") or "",
        previous_context=prev_prompt or "",
        next_context=next_prompt or "",
    )
    if "error" in enriched:
        raise HTTPException(500, detail=enriched["error"])
    slide_data = (enriched.get("slides") or [{}])[0]
    slide_data["global_style_prompt"] = pres.get("global_style") or ""
    slide_data["presentation_mode"] = presentation_mode

    image_url = image_gen.generate_slide_image_from_plan(
        slide_data=slide_data,
        global_style_prompt=slide_data.get("global_style_prompt", ""),
        presentation_mode=presentation_mode,
    )
    if not image_url:
        raise HTTPException(500, "Image generation failed")
    local_path = await save_image_locally(image_url, session_id=presentation_id)
    if not local_path:
        raise HTTPException(500, "Failed to save image")
    prompt_text = req.title or req.content_summary or "New Slide"
    version_id = insert_slide_at_index(db, presentation_id, req.position, local_path, prompt_text)
    if not version_id:
        raise HTTPException(500, "Failed to insert slide")
    if deduct_scores(db, current_user.id, scores_per):
        balance = get_user_scores(db, current_user.id)
        record_score_log(db, current_user.id, scores_per, balance=balance, prompt=prompt_text, image_path=local_path)
    slide = get_slide_by_position(db, presentation_id, req.position)
    return {"status": "success", "slide_id": slide.id, "version_id": version_id, "image_url": local_path}


# === Versions ===

@app.post("/presentations/{presentation_id}/slides/{slide_id}/versions")
async def api_create_version(
    presentation_id: str,
    slide_id: str,
    req: CreateVersionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        raise HTTPException(404, "Slide not found")
    scores_per = get_scores_per_slide(db)
    if get_user_scores(db, current_user.id) < scores_per:
        raise HTTPException(402, f"积分不足：每张需 {scores_per} 积分")
    if req.is_modification:
        if not req.base_image_url:
            raise HTTPException(400, "Modification requires base_image_url")
        base64_image = encode_local_image(req.base_image_url)
        if not base64_image:
            raise HTTPException(404, "Base image file not found")
        history = get_slide_context_messages(db, presentation_id, slide_id)
        image_url = image_gen.modify_slide_image(
            req.prompt, base64_image, history
        )
    else:
        prev_prompt = get_previous_slide_prompt(db, presentation_id, slide_id=slide.id)
        image_url = image_gen.generate_slide_image(
            prompt=req.prompt,
            reference_style_prompt=prev_prompt,
        )
    if not image_url:
        raise HTTPException(500, "Image generation failed")
    local_path = await save_image_locally(image_url, session_id=presentation_id)
    if not local_path:
        raise HTTPException(500, "Failed to save image")
    version_id = add_slide_version_by_slide_id(
        db, presentation_id, slide_id, local_path, req.prompt,
        base_image_path=req.base_image_url if req.is_modification else None,
    )
    if not version_id:
        raise HTTPException(500, "Failed to add version")
    if deduct_scores(db, current_user.id, scores_per):
        balance = get_user_scores(db, current_user.id)
        record_score_log(db, current_user.id, scores_per, balance=balance, prompt=req.prompt, image_path=local_path)
    return {"status": "success", "version_id": version_id, "image_url": local_path}


@app.get("/presentations/{presentation_id}/slides/{slide_id}/versions")
def api_list_versions(presentation_id: str, slide_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        raise HTTPException(404, "Slide not found")
    return {"versions": [_version_to_dict(v) for v in slide.versions]}


@app.patch("/presentations/{presentation_id}/slides/{slide_id}/active-version")
def api_set_active_version(
    presentation_id: str,
    slide_id: str,
    req: SetActiveVersionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    ok = set_slide_active_version(db, presentation_id, slide_id, req.version_id)
    if not ok:
        raise HTTPException(404, "Slide or version not found")
    return {"status": "success", "current_version_id": req.version_id}


@app.delete("/presentations/{presentation_id}/slides/{slide_id}/versions/{version_id}")
def api_delete_version(
    presentation_id: str, slide_id: str, version_id: str, db: Session = Depends(get_db), current_user = Depends(get_current_user)
):
    if not get_presentation(db, presentation_id, user_id=current_user.id):
        raise HTTPException(404, "Presentation not found")
    ok = delete_slide_version(db, presentation_id, slide_id, version_id)
    if not ok:
        raise HTTPException(400, "Version not found or cannot delete the only version")
    return {"status": "success"}


# === Admin ===

@app.post("/admin/auth/login")
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = get_admin_by_username(db, req.username)
    if not admin or not verify_password(req.password, admin.password_hash):
        raise HTTPException(401, "Invalid username or password")
    token = create_access_token(sub=admin.id, role="admin")
    return {"access_token": token, "admin": {"id": admin.id, "username": admin.username}}


@app.get("/admin/me")
def admin_me(current_admin = Depends(get_current_admin)):
    return {"id": current_admin.id, "username": current_admin.username}


@app.patch("/admin/me/password")
def admin_change_password(req: AdminPasswordRequest, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    if not verify_password(req.old_password, current_admin.password_hash):
        raise HTTPException(400, "Wrong current password")
    from models import Admin as AdminModel
    admin_row = db.query(AdminModel).filter(AdminModel.id == current_admin.id).first()
    if not admin_row:
        raise HTTPException(404, "Admin not found")
    admin_row.password_hash = hash_password(req.new_password)
    db.commit()
    return {"status": "success"}


@app.get("/admin/users")
def admin_list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    items, total = list_users_admin(db, skip=skip, limit=limit)
    return {"users": items, "total": total}


@app.post("/admin/users")
def admin_create_user(req: AdminCreateUserRequest, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    if get_user_by_username(db, req.username):
        raise HTTPException(400, "Username already exists")
    user = create_user(db, req.username, hash_password(req.password), initial_scores=req.initial_scores or 0)
    if not user:
        raise HTTPException(400, "Failed to create user")
    return {"id": user.id, "username": user.username, "scores": user.scores}


@app.get("/admin/presentations")
def admin_list_presentations(user_id: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    items, total = list_all_presentations_admin(db, user_id_filter=user_id, skip=skip, limit=limit)
    return {"presentations": items, "total": total}


@app.get("/admin/presentations/{presentation_id}")
def admin_get_presentation(presentation_id: str, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    data = get_presentation(db, presentation_id, user_id=None)
    if not data:
        raise HTTPException(404, "Presentation not found")
    return data


@app.get("/admin/config")
def admin_get_config(db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    from repository import get_register_bonus_scores
    scores_per_slide = get_config(db, "scores_per_slide") or "1"
    register_bonus_scores = get_register_bonus_scores(db)
    return {
        "scores_per_slide": int(scores_per_slide),
        "register_bonus_scores": register_bonus_scores,
    }


@app.patch("/admin/config")
def admin_update_config(req: AdminConfigUpdateRequest, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    if req.scores_per_slide is not None:
        set_config(db, "scores_per_slide", str(max(1, req.scores_per_slide)))
    if req.register_bonus_scores is not None:
        set_config(db, "register_bonus_scores", str(max(0, req.register_bonus_scores)))
    return {"status": "success"}


@app.post("/admin/redemption-codes")
def admin_create_redemption_codes(req: AdminRedemptionCodesRequest, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    codes = create_redemption_codes(db, scores=req.scores, count=req.count, created_by_admin_id=current_admin.id)
    return {"codes": codes, "scores": req.scores}


@app.get("/admin/redemption-codes")
def admin_list_redemption_codes(used: Optional[bool] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    items, total = list_redemption_codes_admin(db, used_only=used, skip=skip, limit=limit)
    return {"redemption_codes": items, "total": total}


@app.delete("/admin/redemption-codes/{code_id}")
def admin_delete_redemption_code(code_id: str, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    status = delete_redemption_code_admin(db, code_id)
    if status == "not_found":
        raise HTTPException(404, "Redemption code not found")
    if status == "used":
        raise HTTPException(400, "Redemption code already used and cannot be deleted")
    return {"status": "success"}


@app.post("/admin/invite-codes")
def admin_create_invite_codes(req: AdminInviteCodesRequest, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    codes = create_invite_codes_by_admin(db, count=req.count, created_by_admin_id=current_admin.id)
    return {"codes": codes}


@app.get("/admin/invite-codes")
def admin_list_invite_codes(used: Optional[bool] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    items, total = list_invite_codes_admin(db, used_only=used, skip=skip, limit=limit)
    return {"invite_codes": items, "total": total}


@app.delete("/admin/invite-codes/{invite_id}")
def admin_delete_invite_code(invite_id: str, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    status = delete_invite_code_admin(db, invite_id)
    if status == "not_found":
        raise HTTPException(404, "Invite code not found")
    if status == "used":
        raise HTTPException(400, "Invite code already used and cannot be deleted")
    return {"status": "success"}


@app.get("/admin/score-logs")
def admin_list_score_logs(
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin),
):
    """管理员查询积分日志（可选按用户筛选）。"""
    items, total = list_score_logs_admin(db, skip=skip, limit=limit, user_id=user_id)
    return {"score_logs": items, "total": total}


# === File upload ===

@app.post("/upload/doc")
async def upload_document(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    allowed_ext = {"txt", "md", "doc", "docx", "pdf"}
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in allowed_ext:
        raise HTTPException(400, "Unsupported file type")
    text = await FileHandler.extract_text(file)
    if not text:
        raise HTTPException(400, "Could not extract text")
    return {"filename": file.filename, "extracted_text": text}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8002))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
