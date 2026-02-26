"""
数据访问层：演示文稿、幻灯片、版本的 CRUD。
"""
import os
import shutil
import uuid
import secrets
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from models import Presentation, Slide, SlideVersion, User, Admin, RedemptionCode, InviteCode, SystemConfig, ScoreLog


def _version_to_dict(v: SlideVersion) -> dict:
    return {
        "id": v.id,
        "image_url": v.image_path,
        "prompt": v.prompt,
        "base_image_url": v.base_image_path,
        "version_number": v.version_number,
        "timestamp": v.created_at.timestamp() if v.created_at else 0,
    }


def _slide_to_dict(s: Slide) -> dict:
    versions = [_version_to_dict(v) for v in s.versions]
    active = s.active_version_id or (versions[-1]["id"] if versions else None)
    return {
        "slide_id": s.id,
        "index": s.position,
        "position": s.position,
        "active_version_id": active,
        "versions": versions,
    }


# ---------- Presentations ----------


def list_presentations(db: Session, user_id: Optional[str] = None) -> List[dict]:
    q = db.query(Presentation).filter(Presentation.deleted_at == None).order_by(Presentation.created_at.desc())
    if user_id is not None:
        q = q.filter(Presentation.user_id == user_id)
    rows = q.all()
    result = []
    for p in rows:
        preview = None
        if p.slides:
            first_slide = min(p.slides, key=lambda s: s.position)
            if first_slide.versions:
                preview = first_slide.versions[-1].image_path
        _topic = getattr(p, "topic", None) or p.title
        item = {
            "id": p.id,
            "topic": _topic,
            "title": p.title,
            "created_at": p.created_at.timestamp() if p.created_at else 0,
            "preview_image": preview,
        }
        item["generation_status"] = getattr(p, "generation_status", None) or "idle"
        item["generation_current"] = getattr(p, "generation_current", None) or 0
        item["generation_total"] = getattr(p, "generation_total", None) or 0
        item["params"] = getattr(p, "params", None)
        item["user_id"] = getattr(p, "user_id", None)
        item["is_published"] = getattr(p, "is_published", None) or 0
        result.append(item)
    return result


def create_presentation(
    db: Session,
    topic: str,
    title: Optional[str] = None,
    user_id: Optional[str] = None,
) -> str:
    pid = str(uuid.uuid4())
    _title = title if title is not None else topic
    p = Presentation(id=pid, title=_title, topic=topic, user_id=user_id)
    db.add(p)
    db.commit()
    return pid


def get_presentation(
    db: Session,
    presentation_id: str,
    user_id: Optional[str] = None,
) -> Optional[dict]:
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return None
    if user_id is not None and getattr(p, "user_id", None) != user_id:
        return None
    # 只包含未删除的幻灯片
    active_slides = sorted([s for s in p.slides if s.deleted_at is None], key=lambda x: x.position)
    slides_data = [_slide_to_dict(s) for s in active_slides]
    _topic = getattr(p, "topic", None) or p.title
    return {
        "id": p.id,
        "user_id": getattr(p, "user_id", None),
        "topic": _topic,
        "title": p.title,
        "global_style": p.global_style,
        "created_at": p.created_at.timestamp() if p.created_at else 0,
        "updated_at": p.updated_at.timestamp() if p.updated_at else 0,
        "slides": slides_data,
        "chat_history": [],  # 重构后不再使用 chat_history，保留键以兼容
        "params": getattr(p, "params", None),
    }


def update_generation_progress(
    db: Session,
    presentation_id: str,
    status: str,
    current: int = 0,
    total: int = 0,
    error: Optional[str] = None,
) -> bool:
    """更新演示文稿的生成进度。"""
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return False
    p.generation_status = status
    p.generation_current = current
    p.generation_total = total
    p.generation_error = error
    p.updated_at = datetime.now(timezone.utc)
    db.commit()
    return True


def get_generation_progress(db: Session, presentation_id: str) -> Optional[dict]:
    """获取演示文稿的生成进度。"""
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return None
    status = p.generation_status or "idle"
    current = p.generation_current or 0
    total = p.generation_total or 0
    percentage = int((current / total) * 100) if total > 0 else 0
    result = {
        "status": status,
        "current": current,
        "total": total,
        "percentage": percentage,
    }
    if p.generation_error:
        result["error"] = p.generation_error
    return result


def update_presentation(
    db: Session,
    presentation_id: str,
    title: Optional[str] = None,
    global_style: Optional[str] = None,
    params: Optional[str] = None,
    is_published: Optional[int] = None,
    published_at: Optional[datetime] = None,
) -> bool:
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return False
    if title is not None:
        p.title = title
    if global_style is not None:
        p.global_style = global_style
    if params is not None:
        p.params = params
    if is_published is not None:
        p.is_published = is_published
    if published_at is not None:
        p.published_at = published_at
    p.updated_at = datetime.now(timezone.utc)
    db.commit()
    return True


def set_presentation_published(
    db: Session,
    presentation_id: str,
    is_published: bool,
) -> bool:
    """设置演示文稿的发布状态。"""
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return False
    p.is_published = 1 if is_published else 0
    if is_published:
        p.published_at = datetime.now(timezone.utc)
    else:
        p.published_at = None
    p.updated_at = datetime.now(timezone.utc)
    db.commit()
    return True


def list_published_presentations(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> List[dict]:
    """列出已发布的演示文稿（公开）。"""
    q = (
        db.query(Presentation)
        .join(User, Presentation.user_id == User.id)
        .filter(Presentation.deleted_at == None)
        .filter(Presentation.is_published == 1)
        .order_by(Presentation.published_at.desc())
    )
    total = q.count()
    rows = q.offset(skip).limit(limit).all()
    result = []
    for p in rows:
        preview = None
        if p.slides:
            first_slide = min(p.slides, key=lambda s: s.position)
            if first_slide.versions:
                preview = first_slide.versions[-1].image_path
        _topic = getattr(p, "topic", None) or p.title
        # 获取用户名
        username = None
        if p.user_id:
            user = db.query(User).filter(User.id == p.user_id).first()
            username = user.username if user else None
        item = {
            "id": p.id,
            "topic": _topic,
            "title": p.title,
            "created_at": p.created_at.timestamp() if p.created_at else 0,
            "published_at": p.published_at.timestamp() if p.published_at else 0,
            "preview_image": preview,
            "username": username,
            "user_id": getattr(p, "user_id", None),
        }
        result.append(item)
    return result


def get_presentation_public(
    db: Session,
    presentation_id: str,
) -> Optional[dict]:
    """获取已发布的演示文稿详情（公开，只读）。"""
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return None
    # 只返回已发布且未删除的演示文稿
    if getattr(p, "is_published", None) != 1 or p.deleted_at is not None:
        return None
    # 只包含未删除的幻灯片
    active_slides = sorted([s for s in p.slides if s.deleted_at is None], key=lambda x: x.position)
    # 只返回当前激活版本，不暴露版本历史
    slides_data = []
    for s in active_slides:
        active_version_id = s.active_version_id or (s.versions[-1].id if s.versions else None)
        if active_version_id:
            active_version = next((v for v in s.versions if v.id == active_version_id), None)
            if active_version:
                slides_data.append({
                    "slide_id": s.id,
                    "index": s.position,
                    "position": s.position,
                    "active_version_id": active_version_id,
                    "versions": [{
                        "id": active_version.id,
                        "image_url": active_version.image_path,
                        "prompt": active_version.prompt,
                        "base_image_url": active_version.base_image_path,
                        "version_number": active_version.version_number,
                        "timestamp": active_version.created_at.timestamp() if active_version.created_at else 0,
                    }],
                })
    _topic = getattr(p, "topic", None) or p.title
    # 获取用户名
    username = None
    if p.user_id:
        user = db.query(User).filter(User.id == p.user_id).first()
        username = user.username if user else None
    return {
        "id": p.id,
        "user_id": getattr(p, "user_id", None),
        "username": username,
        "topic": _topic,
        "title": p.title,
        "global_style": p.global_style,
        "created_at": p.created_at.timestamp() if p.created_at else 0,
        "updated_at": p.updated_at.timestamp() if p.updated_at else 0,
        "published_at": p.published_at.timestamp() if p.published_at else 0,
        "slides": slides_data,
        "chat_history": [],  # 不暴露聊天历史
        "params": getattr(p, "params", None),
    }


def delete_presentation(db: Session, presentation_id: str) -> bool:
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return False
    p.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


def restore_presentation(db: Session, presentation_id: str) -> bool:
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p:
        return False
    p.deleted_at = None
    db.commit()
    return True


def list_deleted_presentations(db: Session, user_id: Optional[str] = None) -> List[dict]:
    q = db.query(Presentation).filter(Presentation.deleted_at != None).order_by(Presentation.deleted_at.desc())
    if user_id is not None:
        q = q.filter(Presentation.user_id == user_id)
    rows = q.all()
    result = []
    for p in rows:
        preview = None
        if p.slides:
            first_slide = min(p.slides, key=lambda s: s.position)
            if first_slide.versions:
                preview = first_slide.versions[-1].image_path
        _topic = getattr(p, "topic", None) or p.title
        result.append({
            "id": p.id,
            "topic": _topic,
            "title": p.title,
            "created_at": p.created_at.timestamp() if p.created_at else 0,
            "deleted_at": p.deleted_at.timestamp() if p.deleted_at else 0,
            "preview_image": preview,
            "params": getattr(p, "params", None),
        })
    return result


STORAGE_IMAGES_ROOT = os.path.join("storage", "images")


def _delete_presentation_images(presentation_id: str) -> None:
    """删除演示文稿关联的图片目录。"""
    img_dir = os.path.join(STORAGE_IMAGES_ROOT, presentation_id)
    if os.path.isdir(img_dir):
        try:
            shutil.rmtree(img_dir)
        except OSError:
            pass


def permanently_delete_presentation(db: Session, presentation_id: str) -> bool:
    """
    彻底删除演示文稿（仅限已软删除的项目）。从数据库物理删除并清理图片目录。
    """
    p = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not p or p.deleted_at is None:
        return False
    _delete_presentation_images(presentation_id)
    db.delete(p)
    db.commit()
    return True


def clear_recycle_bin(db: Session, user_id: Optional[str] = None) -> int:
    """清空回收站：永久删除已软删除的演示文稿。若提供 user_id 则仅删除该用户的。返回删除数量。"""
    q = db.query(Presentation).filter(Presentation.deleted_at != None)
    if user_id is not None:
        q = q.filter(Presentation.user_id == user_id)
    rows = q.all()
    count = 0
    for p in rows:
        _delete_presentation_images(p.id)
        db.delete(p)
        count += 1
    db.commit()
    return count


def list_all_presentations_admin(
    db: Session,
    user_id_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    """管理员：列出所有用户的演示稿，可选按 user_id 筛选、分页，同时返回总数。"""
    q = db.query(Presentation).filter(Presentation.deleted_at == None)
    if user_id_filter is not None:
        q = q.filter(Presentation.user_id == user_id_filter)
    total = q.count()
    rows = (
        q.order_by(Presentation.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    result: list[dict] = []
    for p in rows:
        uid = getattr(p, "user_id", None)
        username = None
        if uid:
            u = db.query(User).filter(User.id == uid).first()
            username = u.username if u else None
        preview = None
        if p.slides:
            first_slide = min(p.slides, key=lambda s: s.position)
            if first_slide.versions:
                preview = first_slide.versions[-1].image_path
        _topic = getattr(p, "topic", None) or p.title
        result.append(
            {
                "id": p.id,
                "user_id": uid,
                "username": username,
                "topic": _topic,
                "title": p.title,
                "created_at": p.created_at.timestamp() if p.created_at else 0,
                "preview_image": preview,
                "generation_status": getattr(p, "generation_status", None)
                or "idle",
                "generation_current": getattr(p, "generation_current", None) or 0,
                "generation_total": getattr(p, "generation_total", None) or 0,
                "params": getattr(p, "params", None),
            }
        )
    return result, total


# ---------- Slides ----------


def get_slide_by_id(
    db: Session, presentation_id: str, slide_id: str, *, include_deleted: bool = False
) -> Optional[Slide]:
    q = db.query(Slide).filter(
        and_(Slide.presentation_id == presentation_id, Slide.id == slide_id)
    )
    if not include_deleted:
        q = q.filter(Slide.deleted_at == None)
    return q.first()


def get_slide_by_position(db: Session, presentation_id: str, position: int) -> Optional[Slide]:
    """返回「未删除的幻灯片按 position 排序」后的第 position 张（从 0 开始）。"""
    rows = (
        db.query(Slide)
        .filter(
            and_(Slide.presentation_id == presentation_id, Slide.deleted_at == None)
        )
        .order_by(Slide.position)
        .all()
    )
    if position < 0 or position >= len(rows):
        return None
    return rows[position]


def add_slide_version(
    db: Session,
    presentation_id: str,
    slide_index: int,
    image_path: str,
    prompt: str,
    base_image_path: Optional[str] = None,
) -> Optional[str]:
    """在指定 position 的幻灯片上增加一个版本；若该 position 无幻灯片则先创建幻灯片。返回 version_id。"""
    slide = get_slide_by_position(db, presentation_id, slide_index)
    if not slide:
        slide = Slide(
            id=str(uuid.uuid4()),
            presentation_id=presentation_id,
            position=slide_index,
        )
        db.add(slide)
        db.flush()

    version_number = (db.query(SlideVersion).filter(SlideVersion.slide_id == slide.id).count()) + 1
    version_id = str(uuid.uuid4())[:8]
    v = SlideVersion(
        id=version_id,
        slide_id=slide.id,
        image_path=image_path,
        prompt=prompt,
        base_image_path=base_image_path,
        version_number=version_number,
    )
    db.add(v)
    slide.active_version_id = version_id
    slide.updated_at = datetime.now(timezone.utc)
    db.commit()
    return version_id


def add_slide_version_by_slide_id(
    db: Session,
    presentation_id: str,
    slide_id: str,
    image_path: str,
    prompt: str,
    base_image_path: Optional[str] = None,
) -> Optional[str]:
    """在指定 slide_id 的幻灯片上增加一个版本。返回 version_id。"""
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        return None
    version_number = (db.query(SlideVersion).filter(SlideVersion.slide_id == slide.id).count()) + 1
    version_id = str(uuid.uuid4())[:8]
    v = SlideVersion(
        id=version_id,
        slide_id=slide.id,
        image_path=image_path,
        prompt=prompt,
        base_image_path=base_image_path,
        version_number=version_number,
    )
    db.add(v)
    slide.active_version_id = version_id
    slide.updated_at = datetime.now(timezone.utc)
    db.commit()
    return version_id


def insert_slide_at_index(
    db: Session,
    presentation_id: str,
    target_index: int,
    image_path: str,
    prompt: str,
) -> Optional[str]:
    """在 target_index 插入一张新幻灯片，后续 position 后移。返回新幻灯片的第一个 version_id。"""
    # 将 position >= target_index 的幻灯片后移
    for s in db.query(Slide).filter(Slide.presentation_id == presentation_id).all():
        if s.position >= target_index:
            s.position += 1
    db.flush()

    slide_id = str(uuid.uuid4())
    version_id = str(uuid.uuid4())[:8]
    slide = Slide(
        id=slide_id,
        presentation_id=presentation_id,
        position=target_index,
        active_version_id=version_id,
    )
    db.add(slide)
    db.flush()
    v = SlideVersion(
        id=version_id,
        slide_id=slide.id,
        image_path=image_path,
        prompt=prompt,
        version_number=1,
    )
    db.add(v)
    db.commit()
    return version_id


def delete_slide_at_index(db: Session, presentation_id: str, slide_index: int) -> bool:
    slide = get_slide_by_position(db, presentation_id, slide_index)
    if not slide:
        return False
    db.delete(slide)
    # 后续 position 前移
    for s in db.query(Slide).filter(Slide.presentation_id == presentation_id).all():
        if s.position > slide_index:
            s.position -= 1
    db.commit()
    return True


def delete_slide_by_id(db: Session, presentation_id: str, slide_id: str) -> bool:
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        return False
    # 软删除，不重排 position
    slide.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True


def list_deleted_slides(db: Session, presentation_id: str) -> List[dict]:
    """返回当前演示文稿下已软删除的幻灯片列表（用于回收站恢复）。"""
    rows = (
        db.query(Slide)
        .filter(
            and_(Slide.presentation_id == presentation_id, Slide.deleted_at != None)
        )
        .order_by(Slide.deleted_at.desc())
        .all()
    )
    return [_slide_to_dict(s) for s in rows]


def restore_slide(db: Session, presentation_id: str, slide_id: str) -> bool:
    slide = get_slide_by_id(db, presentation_id, slide_id, include_deleted=True)
    if not slide:
        return False
    slide.deleted_at = None
    db.commit()
    return True


def set_slide_active_version(db: Session, presentation_id: str, slide_id: str, version_id: str) -> bool:
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        return False
    exists = any(v.id == version_id for v in slide.versions)
    if not exists:
        return False
    slide.active_version_id = version_id
    slide.updated_at = datetime.now(timezone.utc)
    db.commit()
    return True


def delete_slide_version(db: Session, presentation_id: str, slide_id: str, version_id: str) -> bool:
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        return False
    v = next((x for x in slide.versions if x.id == version_id), None)
    if not v or len(slide.versions) <= 1:
        return False
    if slide.active_version_id == version_id:
        remaining = [x for x in slide.versions if x.id != version_id]
        if remaining:
            slide.active_version_id = remaining[-1].id
    db.delete(v)
    db.commit()
    return True


def get_previous_slide_prompt(
    db: Session,
    presentation_id: str,
    current_position: Optional[int] = None,
    *,
    slide_id: Optional[str] = None,
) -> Optional[str]:
    """取「上一张」幻灯片的 prompt。可用 current_position（可见列表中的索引）或 slide_id 指定当前张。"""
    if slide_id is not None:
        rows = (
            db.query(Slide)
            .filter(
                and_(Slide.presentation_id == presentation_id, Slide.deleted_at == None)
            )
            .order_by(Slide.position)
            .all()
        )
        try:
            idx = next(i for i, s in enumerate(rows) if s.id == slide_id)
        except StopIteration:
            return None
        if idx <= 0:
            return None
        prev = rows[idx - 1]
    else:
        if current_position is None or current_position <= 0:
            return None
        prev = get_slide_by_position(db, presentation_id, current_position - 1)
    if not prev or not prev.versions:
        return None
    active = next((x for x in prev.versions if x.id == prev.active_version_id), None) or prev.versions[-1]
    return active.prompt


def get_slide_context_messages(db: Session, presentation_id: str, slide_id: str) -> list:
    slide = get_slide_by_id(db, presentation_id, slide_id)
    if not slide:
        return []
    history = []
    for ver in slide.versions:
        history.append({"role": "user", "content": ver.prompt})
        history.append({"role": "assistant", "content": "Image generated."})
    return history


def get_slide_by_position_for_context(db: Session, presentation_id: str, slide_index: int) -> Optional[Slide]:
    return get_slide_by_position(db, presentation_id, slide_index)


# ---------- Users & Auth ----------


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_admin_by_username(db: Session, username: str) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.username == username).first()


def create_user(
    db: Session,
    username: str,
    password_hash: str,
    initial_scores: int = 0,
) -> Optional[User]:
    if get_user_by_username(db, username):
        return None
    user = User(
        id=str(uuid.uuid4()),
        username=username,
        password_hash=password_hash,
        scores=initial_scores,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users_admin(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    q = db.query(User)
    total = q.count()
    rows = (
        q.order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    items = [
        {
            "id": u.id,
            "username": u.username,
            "scores": u.scores,
            "created_at": u.created_at.timestamp() if u.created_at else 0,
        }
        for u in rows
    ]
    return items, total


# ---------- Scores & System Config ----------


def get_user_scores(db: Session, user_id: str) -> int:
    u = db.query(User).filter(User.id == user_id).first()
    return u.scores if u else 0


def deduct_scores(db: Session, user_id: str, amount: int) -> bool:
    u = db.query(User).filter(User.id == user_id).first()
    if not u or u.scores < amount:
        return False
    u.scores -= amount
    db.commit()
    return True


def add_scores(db: Session, user_id: str, amount: int) -> bool:
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return False
    u.scores += amount
    db.commit()
    return True


def get_config(db: Session, key: str) -> Optional[str]:
    row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    return row.value if row else None


def set_config(db: Session, key: str, value: str) -> None:
    row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if row:
        row.value = value
    else:
        db.add(SystemConfig(key=key, value=value))
    db.commit()


def get_scores_per_slide(db: Session) -> int:
    v = get_config(db, "scores_per_slide")
    if v is None:
        return 1
    try:
        return max(1, int(v))
    except ValueError:
        return 1


def get_register_bonus_scores(db: Session) -> int:
    """获取新用户注册赠送积分配置，默认返回 50。"""
    v = get_config(db, "register_bonus_scores")
    if v is None:
        return 50
    try:
        return max(0, int(v))  # 允许 0，不允许负数
    except ValueError:
        return 50


# ---------- Score Logs (积分日志) ----------


def record_score_log(
    db: Session,
    user_id: str,
    amount: int,
    balance: Optional[int] = None,
    prompt: Optional[str] = None,
    image_path: Optional[str] = None,
    log_type: str = "consume",
) -> bool:
    """记录一条积分日志。
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        amount: 积分变动数量（正数）
        balance: 变动后的积分余额，如果为None则自动查询
        prompt: 提示词或说明（最多500字符）
        image_path: 图片路径（消费类日志使用，充值类为空）
        log_type: 日志类型，"recharge"（充值）或 "consume"（消费），默认 "consume"
    """
    try:
        # 截断提示词，最多 500 字符
        truncated_prompt = prompt[:500] if prompt and len(prompt) > 500 else prompt
        # 如果没有传入余额，查询当前余额
        if balance is None:
            balance = get_user_scores(db, user_id)
        log = ScoreLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            amount=amount,
            balance=balance,
            prompt=truncated_prompt,
            image_path=image_path,
            log_type=log_type,
        )
        db.add(log)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def list_score_logs_by_user(
    db: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[dict], int]:
    """查询指定用户的积分日志（分页）。"""
    query = db.query(ScoreLog).filter(ScoreLog.user_id == user_id).order_by(ScoreLog.created_at.desc())
    total = query.count()
    rows = query.offset(skip).limit(limit).all()
    items = [
        {
            "id": log.id,
            "amount": log.amount,
            "balance": log.balance,
            "prompt": log.prompt,
            "image_path": log.image_path,
            "log_type": log.log_type,
            "created_at": log.created_at.timestamp() if log.created_at else 0,
        }
        for log in rows
    ]
    return items, total


def list_score_logs_admin(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[str] = None,
) -> tuple[List[dict], int]:
    """管理员查询积分日志（分页，可选按用户筛选）。"""
    query = db.query(ScoreLog, User.username).join(User, ScoreLog.user_id == User.id)
    if user_id:
        query = query.filter(ScoreLog.user_id == user_id)
    query = query.order_by(ScoreLog.created_at.desc())
    total = query.count()
    rows = query.offset(skip).limit(limit).all()
    items = [
        {
            "id": log.id,
            "user_id": log.user_id,
            "username": username,
            "amount": log.amount,
            "balance": log.balance,
            "prompt": log.prompt,
            "image_path": log.image_path,
            "log_type": log.log_type,
            "created_at": log.created_at.timestamp() if log.created_at else 0,
        }
        for log, username in rows
    ]
    return items, total


# ---------- Redemption Codes (积分兑换码) ----------


def _generate_random_code_32() -> str:
    """
    生成 32 位小写字符串形式的兑换码。
    使用 128bit 安全随机数并以十六进制编码，字符集 [0-9a-f]，长度固定 32。
    """
    return secrets.token_hex(16)


def _generate_unique_redemption_code(db: Session, existing_batch: set[str]) -> str:
    """
    在当前数据库与本批次内保证唯一的兑换码生成器。
    - 先在内存 set 中去重，避免同一批次重复；
    - 再查询数据库是否已存在，极小概率冲突时重试。
    """
    from models import RedemptionCode as RedemptionCodeModel  # 避免循环导入

    while True:
        code = _generate_random_code_32()
        if code in existing_batch:
            continue
        # 检查数据库是否已存在该 code
        exists = db.query(RedemptionCodeModel).filter(RedemptionCodeModel.code == code).first()
        if exists:
            continue
        existing_batch.add(code)
        return code


def create_redemption_codes(
    db: Session,
    scores: int,
    count: int,
    created_by_admin_id: str,
) -> List[str]:
    """
    批量创建积分兑换码。
    - 兑换码为 32 位小写字符串（十六进制），如：a19f0c...；
    - 在单批次与数据库层面尽可能保证不重复，数据库中仍建议保留唯一索引作为最终保障。
    """
    codes: List[str] = []
    batch_codes: set[str] = set()
    for _ in range(count):
        code_id = str(uuid.uuid4())
        code = _generate_unique_redemption_code(db, batch_codes)
        r = RedemptionCode(
            id=code_id,
            code=code,
            scores=scores,
            created_by_admin_id=created_by_admin_id,
        )
        db.add(r)
        codes.append(code)
    db.commit()
    return codes


def use_redemption_code(db: Session, code: str, user_id: str):
    """
    使用兑换码。
    成功返回 ("ok", added: int)；
    码不存在返回 ("invalid",)；
    码已使用返回 ("already_used",)。
    """
    r = db.query(RedemptionCode).filter(RedemptionCode.code == code).first()
    if not r:
        return ("invalid",)
    if r.used_by_id is not None:
        return ("already_used",)
    r.used_by_id = user_id
    r.used_at = datetime.now(timezone.utc)
    db.commit()
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        return ("invalid",)
    u.scores += r.scores
    db.commit()
    return ("ok", r.scores)


# ---------- Invite Codes (注册邀请码) ----------


INVITE_CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _generate_random_invite_code_8() -> str:
    """
    生成 8 位邀请码，字符集为大写字母与数字，去掉易混淆字符。
    示例：AB3D9K7M
    """
    return "".join(secrets.choice(INVITE_CODE_ALPHABET) for _ in range(8))


def _generate_unique_invite_code(db: Session, existing_batch: set[str]) -> str:
    """
    在当前数据库与本批次内保证唯一的邀请码生成器。
    - 先在内存 set 中去重，避免同一批次重复；
    - 再查询数据库是否已存在，极小概率冲突时重试。
    """
    from models import InviteCode as InviteCodeModel  # 避免循环导入

    while True:
        code = _generate_random_invite_code_8()
        if code in existing_batch:
            continue
        exists = (
            db.query(InviteCodeModel)
            .filter(InviteCodeModel.code == code)
            .first()
        )
        if exists:
            continue
        existing_batch.add(code)
        return code


def get_invite_code_by_code(db: Session, code: str) -> Optional[InviteCode]:
    return db.query(InviteCode).filter(InviteCode.code == code).first()


def count_invite_codes_by_user(db: Session, user_id: str) -> int:
    return db.query(InviteCode).filter(InviteCode.created_by_user_id == user_id).count()


def create_invite_code_by_user(db: Session, user_id: str) -> Optional[str]:
    """用户生成 1 个邀请码，最多 3 个。返回新 code 或 None。"""
    if count_invite_codes_by_user(db, user_id) >= 3:
        return None
    code_id = str(uuid.uuid4())
    batch_codes: set[str] = set()
    code = _generate_unique_invite_code(db, batch_codes)
    inv = InviteCode(
        id=code_id,
        code=code,
        created_by_user_id=user_id,
        created_by_admin_id=None,
    )
    db.add(inv)
    db.commit()
    return code


def create_invite_codes_by_admin(db: Session, count: int, created_by_admin_id: str) -> List[str]:
    codes: List[str] = []
    batch_codes: set[str] = set()
    for _ in range(count):
        code_id = str(uuid.uuid4())
        code = _generate_unique_invite_code(db, batch_codes)
        inv = InviteCode(
            id=code_id,
            code=code,
            created_by_user_id=None,
            created_by_admin_id=created_by_admin_id,
        )
        db.add(inv)
        codes.append(code)
    db.commit()
    return codes


def use_invite_code(db: Session, code: str, new_user_id: str) -> bool:
    """注册时使用邀请码，标记已用。返回是否成功。"""
    inv = get_invite_code_by_code(db, code)
    if not inv or inv.used_by_user_id is not None:
        return False
    inv.used_by_user_id = new_user_id
    inv.used_at = datetime.now(timezone.utc)
    db.commit()
    return True


def list_invite_codes_by_user(db: Session, user_id: str) -> List[dict]:
    rows = (
        db.query(InviteCode)
        .filter(InviteCode.created_by_user_id == user_id)
        .order_by(InviteCode.created_at.desc())
        .all()
    )
    return [
        {
            "code": r.code,
            "used": r.used_by_user_id is not None,
            "used_at": r.used_at.timestamp() if r.used_at else None,
            "created_at": r.created_at.timestamp() if r.created_at else 0,
        }
        for r in rows
    ]


def list_invite_codes_admin(
    db: Session,
    used_only: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    q = db.query(InviteCode)
    if used_only is True:
        q = q.filter(InviteCode.used_by_user_id != None)
    elif used_only is False:
        q = q.filter(InviteCode.used_by_user_id == None)
    total = q.count()
    rows = (
        q.order_by(InviteCode.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    items = [
        {
            "id": r.id,
            "code": r.code,
            "created_by_user_id": r.created_by_user_id,
            "created_by_admin_id": r.created_by_admin_id,
            "used_by_user_id": r.used_by_user_id,
            "used_at": r.used_at.timestamp() if r.used_at else None,
            "created_at": r.created_at.timestamp() if r.created_at else 0,
        }
        for r in rows
    ]
    return items, total


def list_redemption_codes_admin(
    db: Session,
    used_only: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[dict], int]:
    q = db.query(RedemptionCode)
    if used_only is True:
        q = q.filter(RedemptionCode.used_by_id != None)
    elif used_only is False:
        q = q.filter(RedemptionCode.used_by_id == None)
    total = q.count()
    rows = (
        q.order_by(RedemptionCode.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    items = [
        {
            "id": r.id,
            "code": r.code,
            "scores": r.scores,
            "used_by_id": r.used_by_id,
            "used_at": r.used_at.timestamp() if r.used_at else None,
            "created_at": r.created_at.timestamp() if r.created_at else 0,
        }
        for r in rows
    ]
    return items, total


def delete_redemption_code_admin(db: Session, code_id: str) -> str:
    """
    管理员删除积分兑换码。
    返回值：
    - "ok"：删除成功
    - "used"：已被使用，不能删除
    - "not_found"：未找到记录
    """
    row = db.query(RedemptionCode).filter(RedemptionCode.id == code_id).first()
    if not row:
        return "not_found"
    if row.used_by_id is not None:
        return "used"
    db.delete(row)
    db.commit()
    return "ok"


def delete_invite_code_admin(db: Session, invite_id: str) -> str:
    """
    管理员删除注册邀请码。
    返回值：
    - "ok"：删除成功
    - "used"：已被使用，不能删除
    - "not_found"：未找到记录
    """
    row = db.query(InviteCode).filter(InviteCode.id == invite_id).first()
    if not row:
        return "not_found"
    if row.used_by_user_id is not None:
        return "used"
    db.delete(row)
    db.commit()
    return "ok"
