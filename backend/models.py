"""
SQLAlchemy ORM 模型：用户、管理员、演示文稿、幻灯片、版本、兑换码、邀请码、系统配置。
"""
from datetime import datetime, timezone

def _utc_now():
    return datetime.now(timezone.utc)
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    scores = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=_utc_now)


class Admin(Base):
    __tablename__ = "admins"

    id = Column(String(36), primary_key=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=_utc_now)


class RedemptionCode(Base):
    """积分兑换码：会员中心兑换用，每个码仅能用一次。"""
    __tablename__ = "redemption_codes"

    id = Column(String(36), primary_key=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    scores = Column(Integer, nullable=False)
    used_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_by_admin_id = Column(String(36), ForeignKey("admins.id"), nullable=True)
    created_at = Column(DateTime, default=_utc_now)


class InviteCode(Base):
    """注册邀请码：邀请制注册用，每个码仅能用一次。用户最多生成 3 个；管理员可批量生成。"""
    __tablename__ = "invite_codes"

    id = Column(String(36), primary_key=True)
    code = Column(String(64), unique=True, nullable=False, index=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_by_admin_id = Column(String(36), ForeignKey("admins.id"), nullable=True)
    used_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utc_now)


class SystemConfig(Base):
    """系统配置键值表。"""
    __tablename__ = "system_config"

    key = Column(String(128), primary_key=True)
    value = Column(Text, nullable=True)


class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # 兼容旧数据
    title = Column(String(512), nullable=False, default="Untitled PPT")
    topic = Column(Text, nullable=True)  # 用户提交的主题原文，不随规划/生成覆盖
    global_style = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    deleted_at = Column(DateTime, nullable=True)  # 软删除标记
    # 生成进度：idle | planning | generating | completed | failed
    generation_status = Column(String(32), nullable=True, default="idle")
    generation_current = Column(Integer, nullable=True, default=0)  # 已完成的幻灯片索引
    generation_total = Column(Integer, nullable=True, default=0)  # 计划生成总数
    generation_error = Column(Text, nullable=True)  # 失败时的错误信息
    params = Column(Text, nullable=True)  # 生成参数 JSON：language, presentation_mode, style_preset_id, audience, scene, attention, purpose, page_count
    is_published = Column(Integer, nullable=True, default=0)  # 0=未发布 1=已发布
    published_at = Column(DateTime, nullable=True)  # 发布时间

    slides = relationship("Slide", back_populates="presentation", order_by="Slide.position", cascade="all, delete-orphan")


class Slide(Base):
    __tablename__ = "slides"

    id = Column(String(36), primary_key=True)
    presentation_id = Column(String(36), ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False, default=0)  # 从 0 开始
    active_version_id = Column(String(36), nullable=True)  # 当前激活的 slide_version.id
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)
    deleted_at = Column(DateTime, nullable=True)  # 软删除，恢复后可重新显示

    presentation = relationship("Presentation", back_populates="slides")
    versions = relationship("SlideVersion", back_populates="slide", order_by="SlideVersion.version_number", cascade="all, delete-orphan")


class SlideVersion(Base):
    __tablename__ = "slide_versions"

    id = Column(String(36), primary_key=True)  # 8 位或完整 UUID
    slide_id = Column(String(36), ForeignKey("slides.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String(512), nullable=False)  # 相对路径，如 /images/{presentation_id}/{filename}.png
    prompt = Column(Text, nullable=False)
    base_image_path = Column(String(512), nullable=True)  # 修改模式下的基础图路径
    version_number = Column(Integer, nullable=False, default=1)  # 版本序号
    created_at = Column(DateTime, default=_utc_now)

    slide = relationship("Slide", back_populates="versions")


class ScoreLog(Base):
    """积分使用日志：记录用户每次积分变动（充值或消费）、提示词和图片地址。"""
    __tablename__ = "score_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # 积分变动数量（正数）
    balance = Column(Integer, nullable=True)  # 变动后的积分余额
    prompt = Column(Text, nullable=True)  # 提示词（可截断，如 500 字）
    image_path = Column(String(512), nullable=True)  # 图片相对路径，如 /images/xxx/yyy.png
    log_type = Column(String(32), nullable=False, default="consume")  # 类型：recharge（充值）或 consume（消费）
    created_at = Column(DateTime, default=_utc_now)
