import random
import string

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app import models
from app.config import settings


# --- Function for shortest path generation (short_path) ---
def generate_short_path(length: int = 8) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))


def get_unique_short_path(db: Session, length: int = 8) -> str:
    """Try to generate a unique short_path; if it already exists in the database, try again."""
    while True:
        candidate = generate_short_path(length)
        existing = (
            db.query(models.URL).filter(models.URL.short_path == candidate).first()
        )
        if not existing:
            return candidate


# --- CRUD for User ---
def create_user(db: Session, username: str, password_hash: str) -> models.User:
    db_user = models.User(username=username, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str) -> models.User:
    return db.query(models.User).filter(models.User.username == username).first()


# --- CRUD for URL ---
def create_url(
    db: Session, owner_id: int, original_url, expire_seconds: int = None
) -> models.URL:
    if expire_seconds is None:
        expire_seconds = settings.ACCESS_TOKEN_EXPIRE_SECONDS
    original_str = str(original_url)
    short_path = get_unique_short_path(db)
    db_url = models.URL(
        original_url=original_str,
        short_path=short_path,
        owner_id=owner_id,
        is_active=True,
    )
    db_url.set_expiration(expire_seconds)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_url_by_short_path(db: Session, short_path: str) -> models.URL:
    return db.query(models.URL).filter(models.URL.short_path == short_path).first()


def list_urls(db: Session, owner_id: int):
    return db.query(models.URL).filter(models.URL.owner_id == owner_id).all()


def deactivate_url(db: Session, url_id: int, owner_id: int) -> models.URL:
    db_url = (
        db.query(models.URL)
        .filter(models.URL.id == url_id, models.URL.owner_id == owner_id)
        .first()
    )
    if not db_url:
        return None
    db_url.is_active = False
    db.commit()
    db.refresh(db_url)
    return db_url


# --- CRUD for clicks ---
def log_click(
    db: Session, url: models.URL, visitor_ip: str = None, user_agent: str = None
) -> None:
    db_click = models.ClickStat(
        url_id=url.id, visitor_ip=visitor_ip, user_agent=user_agent
    )
    db.add(db_click)
    db.commit()


# --- Obtaining statistics ---
def get_url_stats(db: Session, owner_id: int):
    """
    Return a list of references (owned by owner),
    sorted by the number of clicks (descending).
    """
    # JOIN URL and ClickStat, group by URL.id
    subq = (
        db.query(
            models.ClickStat.url_id,
            func.count(models.ClickStat.id).label("total_clicks"),
            func.max(models.ClickStat.clicked_at).label("last_clicked_at"),
        )
        .group_by(models.ClickStat.url_id)
        .subquery()
    )
    # External request: all owner + left join links to subq
    query = (
        db.query(
            models.URL.id,
            models.URL.short_path,
            models.URL.original_url,
            models.URL.is_active,
            models.URL.expires_at,
            func.coalesce(subq.c.total_clicks, 0).label("total_clicks"),
            subq.c.last_clicked_at,
        )
        .outerjoin(subq, models.URL.id == subq.c.url_id)
        .filter(models.URL.owner_id == owner_id)
        .order_by(desc("total_clicks"))
    )
    return query.all()
