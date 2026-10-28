"""AI 绘图模块（预留）。

绘图模型 API 选型待定，本模块仅预留统一接入点：
- 未配置 DRAW_API_KEY 时返回 503 与明确提示；
- 配置后按 OpenAI Images API 兼容协议转发（DRAW_BASE_URL/images/generations）。
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.deps import get_current_user
from app.models import User
from app.schemas import DrawRequest

settings = get_settings()
router = APIRouter(prefix="/api/draw", tags=["AI 绘图"])


@router.post("/generate")
def generate(payload: DrawRequest, user: User = Depends(get_current_user)):
    if not settings.DRAW_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="绘图服务尚未配置：请在 backend/.env 中填写 DRAW_API_KEY（绘图模型选型待定）",
        )

    # ---- 绘图模型接入点（选型确认后启用） ----
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="绘图模型 API 选型待定，当前版本暂未启用真实生成，请配置后重新尝试",
    )
