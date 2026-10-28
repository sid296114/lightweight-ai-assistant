"""ORM 模型：user / chat_session / chat_message 三表首期全建。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="用户主键ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名，唯一")
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="登录邮箱，唯一")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment="bcrypt加密后的密码，不存明文")
    avatar: Mapped[str] = mapped_column(String(255), default="", comment="头像地址，预留")
    status: Mapped[int] = mapped_column(default=1, comment="账号状态：1正常 0禁用")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="注册时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="信息更新时间"
    )


class ChatSession(Base):
    __tablename__ = "chat_session"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("user.id"), nullable=False, index=True, comment="关联user.id")
    title: Mapped[str] = mapped_column(String(100), nullable=False, comment="会话标题")
    model_name: Mapped[str] = mapped_column(String(50), default="", comment="选用模型")
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat_session.id"), nullable=False, index=True, comment="关联会话id")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="user / assistant")
    content: Mapped[str] = mapped_column(LONGTEXT, nullable=False, comment="消息内容")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
