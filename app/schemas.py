from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl


# --- User ---
class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# --- URL ---
class URLCreate(BaseModel):
    original_url: HttpUrl
    expire_seconds: Optional[int] = None


class URLRead(BaseModel):
    id: int
    original_url: HttpUrl
    short_path: str
    created_at: datetime
    expires_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


# --- Click statistics ---
class ClickStatRead(BaseModel):
    id: int
    url_id: int
    clicked_at: datetime
    visitor_ip: Optional[str]
    user_agent: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# To give the aggregate statistics on the link:
class URLStats(BaseModel):
    url_id: int
    short_path: str
    total_clicks: int
    last_clicked_at: Optional[datetime]


# If you need to return a list of URLs along with their statistics:
class URLWithStats(BaseModel):
    id: int
    short_path: str
    original_url: HttpUrl
    total_clicks: int
    last_clicked_at: Optional[datetime]
    is_active: bool
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)
