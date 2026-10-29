"""Pydantic 请求/响应模型。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- 账号 ----------
class UserRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=64, description="密码最少 6 位")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=64)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- 会话与消息 ----------
class SessionCreate(BaseModel):
    title: str = Field("新对话", max_length=100)
    model_name: Optional[str] = ""
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)


class SessionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)


class SessionOut(BaseModel):
    id: int
    title: str
    model_name: str
    temperature: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------- 对话请求 ----------
class ChatRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=20000, description="用户输入")
    session_id: Optional[int] = None  # 为空则后端自动新建会话
    provider_id: Optional[str] = None  # 所选大模型服务商（多 OpenAI 兼容接入）
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)
    file_id: Optional[str] = None  # 上传解析后的文档 ID，注入上下文


# ---------- 文件解析 ----------
class FileParseOut(BaseModel):
    file_id: str
    filename: str
    size_bytes: int
    pages: Optional[int] = None
    chars: int
    preview: str
    truncated: bool


# ---------- AI 绘图（预留） ----------
class DrawRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    negative_prompt: str = Field("", max_length=1000)
    size: str = Field("1024x1024", pattern=r"^\d{2,4}x\d{2,4}$")
    n: int = Field(1, ge=1, le=4)


# ---------- 大模型服务商 ----------
class ProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    base_url: str = Field(..., min_length=1, max_length=300, description="OpenAI 兼容接口地址，本地模型如 http://127.0.0.1:11434/v1")
    models: list[str] = Field(default_factory=list)
    default_model: str = Field("", max_length=100)
    no_auth: bool = Field(False, description="该服务无需 API Key（自部署推理，如魔搭/私有 vLLM 等）")
    system_prompt: str = Field("", max_length=4000, description="系统提示词 / 人设，留空则使用默认助手人设")


class ProviderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    base_url: Optional[str] = Field(None, min_length=1, max_length=300)
    models: Optional[list[str]] = None
    default_model: Optional[str] = Field(None, max_length=100)
    no_auth: Optional[bool] = None
    system_prompt: Optional[str] = Field(None, max_length=4000)


class ProviderOut(BaseModel):
    id: str
    name: str
    base_url: str
    models: list[str]
    default_model: str
    api_key_configured: bool
    is_local: bool
    no_auth: bool
    system_prompt: str


class ApiKeyIn(BaseModel):
    api_key: str = Field("", max_length=300, description="传入空串清除 API Key")
