from datetime import datetime, timedelta

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    urls = relationship("URL", back_populates="owner")


class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String(2048), nullable=False)
    short_path = Column(String(16), unique=True, index=True)  # for example: "aB3kdE"
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="urls")
    clicks = relationship("ClickStat", back_populates="url")

    def set_expiration(self, expire_seconds: int):
        self.expires_at = datetime.utcnow() + timedelta(seconds=expire_seconds)


class ClickStat(Base):
    __tablename__ = "click_stats"
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    clicked_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    visitor_ip = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(512), nullable=True)

    url = relationship("URL", back_populates="clicks")
