"""大模型服务商管理接口：新增 / 列表 / 更新 / 删除 / API Key 设置。"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user
from app.models import User
from app.schemas import ApiKeyIn, ProviderCreate, ProviderOut, ProviderUpdate
from app.services import providers as provider_svc

router = APIRouter(prefix="/api/providers", tags=["大模型服务商"])


@router.get("", response_model=list[ProviderOut])
def list_providers(user: User = Depends(get_current_user)):
    return provider_svc.list_providers()


@router.post("", response_model=ProviderOut, status_code=status.HTTP_201_CREATED)
def create_provider(payload: ProviderCreate, user: User = Depends(get_current_user)):
    return provider_svc.create_provider(
        name=payload.name,
        base_url=payload.base_url,
        models=payload.models,
        default_model=payload.default_model,
        no_auth=payload.no_auth,
    )


@router.patch("/{provider_id}", response_model=ProviderOut)
def update_provider(
    provider_id: str,
    payload: ProviderUpdate,
    user: User = Depends(get_current_user),
):
    updated = provider_svc.update_provider(
        provider_id=provider_id,
        name=payload.name,
        base_url=payload.base_url,
        models=payload.models,
        default_model=payload.default_model,
        no_auth=payload.no_auth,
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="服务商不存在")
    return updated


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_provider(provider_id: str, user: User = Depends(get_current_user)):
    if not provider_svc.delete_provider(provider_id):
        raise HTTPException(status_code=404, detail="服务商不存在")


@router.post("/{provider_id}/api-key", response_model=ProviderOut)
def set_api_key(
    provider_id: str,
    payload: ApiKeyIn,
    user: User = Depends(get_current_user),
):
    """保存 API Key（仅存后端，不返回明文）；传空串清除。"""
    updated = provider_svc.set_api_key(provider_id, payload.api_key)
    if updated is None:
        raise HTTPException(status_code=404, detail="服务商不存在")
    return updated
