"""
SQLite 数据库连接与初始化。
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库文件路径：项目根目录下的 storage 目录
STORAGE_DIR = os.path.join(os.path.dirname(__file__), "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(STORAGE_DIR, 'presentations.db')}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """创建所有表。确保在调用前已加载 models（例如通过 main 先 import repository）。"""
    import models  # noqa: F401 - 注册 ORM 到 Base.metadata
    Base.metadata.create_all(bind=engine)


def migrate_add_deleted_at():
    """为 presentations 表添加 deleted_at 列（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(presentations)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "deleted_at" in columns:
            return
        conn.execute(text("ALTER TABLE presentations ADD COLUMN deleted_at DATETIME"))
        conn.commit()


def migrate_add_slide_deleted_at():
    """为 slides 表添加 deleted_at 列（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(slides)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "deleted_at" in columns:
            return
        conn.execute(text("ALTER TABLE slides ADD COLUMN deleted_at DATETIME"))
        conn.commit()


def migrate_add_generation_fields():
    """为 presentations 表添加生成进度相关列（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(presentations)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "generation_status" not in columns:
            conn.execute(text("ALTER TABLE presentations ADD COLUMN generation_status VARCHAR(32)"))
        if "generation_current" not in columns:
            conn.execute(text("ALTER TABLE presentations ADD COLUMN generation_current INTEGER"))
        if "generation_total" not in columns:
            conn.execute(text("ALTER TABLE presentations ADD COLUMN generation_total INTEGER"))
        if "generation_error" not in columns:
            conn.execute(text("ALTER TABLE presentations ADD COLUMN generation_error TEXT"))
        conn.commit()


def migrate_add_params():
    """为 presentations 表添加 params 列（若不存在），用于存储生成参数 JSON。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(presentations)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "params" in columns:
            return
        conn.execute(text("ALTER TABLE presentations ADD COLUMN params TEXT"))
        conn.commit()


def migrate_add_topic():
    """为 presentations 表添加 topic 列（若不存在），用于存储用户提交的主题原文。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(presentations)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "topic" in columns:
            return
        conn.execute(text("ALTER TABLE presentations ADD COLUMN topic TEXT"))
        conn.commit()


def migrate_add_user_id():
    """为 presentations 表添加 user_id 列（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(presentations)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "user_id" in columns:
            return
        conn.execute(text("ALTER TABLE presentations ADD COLUMN user_id VARCHAR(36)"))
        conn.commit()


def _bcrypt_hash(password: str) -> str:
    """使用 bcrypt 哈希密码，避免 passlib 与 bcrypt 4.1+ 的兼容性问题。"""
    import bcrypt
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_default_admin():
    """若 admins 表为空，则插入默认管理员 admin / admin123。"""
    from sqlalchemy import text
    import uuid
    from datetime import datetime, timezone
    with engine.connect() as conn:
        r = conn.execute(text("SELECT COUNT(*) FROM admins"))
        n = r.scalar()
        if n and n > 0:
            return
        admin_id = str(uuid.uuid4())
        password_hash = _bcrypt_hash("admin123")
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            text(
                "INSERT INTO admins (id, username, password_hash, created_at) VALUES (:id, 'admin', :ph, :created_at)"
            ),
            {"id": admin_id, "ph": password_hash, "created_at": now},
        )
        conn.commit()


def seed_system_config():
    """确保 system_config 中有 scores_per_slide 和 register_bonus_scores 默认值。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        # scores_per_slide
        r = conn.execute(text("SELECT value FROM system_config WHERE key = 'scores_per_slide'"))
        row = r.fetchone()
        if row is None:
            conn.execute(
                text("INSERT INTO system_config (key, value) VALUES ('scores_per_slide', '1')")
            )
        # register_bonus_scores
        r = conn.execute(text("SELECT value FROM system_config WHERE key = 'register_bonus_scores'"))
        row = r.fetchone()
        if row is None:
            conn.execute(
                text("INSERT INTO system_config (key, value) VALUES ('register_bonus_scores', '50')")
            )
        conn.commit()


def migrate_points_to_scores():
    """将 points 字段重命名为 scores，并迁移系统配置键。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        # 检查 users 表是否有 points 列
        r = conn.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in r.fetchall()]
        if "points" in columns and "scores" not in columns:
            conn.execute(text("ALTER TABLE users RENAME COLUMN points TO scores"))

        # 检查 redemption_codes 表是否有 points 列
        r = conn.execute(text("PRAGMA table_info(redemption_codes)"))
        columns = [row[1] for row in r.fetchall()]
        if "points" in columns and "scores" not in columns:
            conn.execute(text("ALTER TABLE redemption_codes RENAME COLUMN points TO scores"))

        # 迁移系统配置：points_per_slide → scores_per_slide
        r = conn.execute(text("SELECT value FROM system_config WHERE key = 'points_per_slide'"))
        row = r.fetchone()
        if row is not None:
            value = row[0]
            # 插入新 key
            conn.execute(
                text("INSERT OR IGNORE INTO system_config (key, value) VALUES ('scores_per_slide', :val)"),
                {"val": value}
            )
            # 删除旧 key
            conn.execute(text("DELETE FROM system_config WHERE key = 'points_per_slide'"))

        conn.commit()


def migrate_add_is_published():
    """为 presentations 表添加 is_published 和 published_at 列（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(presentations)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "is_published" not in columns:
            conn.execute(text("ALTER TABLE presentations ADD COLUMN is_published INTEGER"))
        if "published_at" not in columns:
            conn.execute(text("ALTER TABLE presentations ADD COLUMN published_at DATETIME"))
        conn.commit()


def seed_default_user():
    """若不存在 id=1 的用户，则插入默认用户 18575670125 / 123456，并将所有 presentations.user_id 设为 1。"""
    from sqlalchemy import text
    from datetime import datetime, timezone

    default_user_id = "1"
    default_username = "18575670125"
    default_password_hash = _bcrypt_hash("123456")
    now = datetime.now(timezone.utc).isoformat()

    with engine.connect() as conn:
        r = conn.execute(text("SELECT id FROM users WHERE id = :id"), {"id": default_user_id})
        if r.fetchone() is not None:
            # 用户已存在，仅统一 presentations.user_id
            conn.execute(text("UPDATE presentations SET user_id = :uid WHERE user_id IS NULL OR user_id != :uid"), {"uid": default_user_id})
            conn.commit()
            return
        conn.execute(
            text(
                "INSERT INTO users (id, username, password_hash, scores, created_at) "
                "VALUES (:id, :username, :ph, 0, :created_at)"
            ),
            {"id": default_user_id, "username": default_username, "ph": default_password_hash, "created_at": now},
        )
        conn.execute(text("UPDATE presentations SET user_id = :uid"), {"uid": default_user_id})
        conn.commit()


def migrate_create_score_logs():
    """创建 score_logs 表（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        # 检查表是否存在
        r = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='score_logs'"))
        if r.fetchone() is not None:
            return
        # 创建表
        conn.execute(text("""
            CREATE TABLE score_logs (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                amount INTEGER NOT NULL,
                balance INTEGER,
                prompt TEXT,
                image_path VARCHAR(512),
                created_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """))
        # 创建索引
        conn.execute(text("CREATE INDEX idx_score_logs_user_id ON score_logs(user_id)"))
        conn.commit()


def migrate_add_score_logs_balance():
    """为 score_logs 表添加 balance 列（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(score_logs)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "balance" in columns:
            return
        conn.execute(text("ALTER TABLE score_logs ADD COLUMN balance INTEGER"))
        conn.commit()


def migrate_add_score_logs_type():
    """为 score_logs 表添加 log_type 列（若不存在）。"""
    from sqlalchemy import text
    with engine.connect() as conn:
        r = conn.execute(text("PRAGMA table_info(score_logs)"))
        columns = [row[1] for row in r.fetchall()]
        if not columns:
            return
        if "log_type" in columns:
            return
        conn.execute(text("ALTER TABLE score_logs ADD COLUMN log_type VARCHAR(32) DEFAULT 'consume'"))
        conn.commit()


def get_db():
    """依赖注入用：获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
