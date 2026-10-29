"""会话与消息模块 + SSE 流式对话接口。

- 会话：创建 / 列表 / 重命名（参数更新）/ 删除（级联删除消息）
- 消息：历史加载
- 流式对话：POST /api/chat/stream，SSE 协议：
    data: {"type": "delta", "content": "..."}
    data: {"type": "done", "session_id": 1, "message_id": 2}
    data: {"type": "error", "message": "..."}
"""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import ChatMessage, ChatSession, User
from app.schemas import (
    ChatRequest,
    MessageOut,
    SessionCreate,
    SessionOut,
    SessionUpdate,
)
from app.services.file_parser import load_parsed_text
from app.services.llm import build_messages, stream_chat
from app.services.providers import get_provider

router = APIRouter(prefix="/api/chat", tags=["对话"])

MAX_HISTORY_MESSAGES = 20       # 携带的历史消息条数
MAX_HISTORY_ITEM_CHARS = 4000   # 单条历史消息截断长度
DEFAULT_TITLE_CHARS = 20


def _get_owned_session(db: Session, session_id: int, user_id: int) -> ChatSession:
    session = db.get(ChatSession, session_id)
    if session is None or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="会话不存在")
    return session


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = ChatSession(
        user_id=user.id,
        title=payload.title.strip() or "新对话",
        model_name=payload.model_name or "",
        temperature=payload.temperature if payload.temperature is not None else 0.7,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == user.id)
            .order_by(ChatSession.updated_at.desc())
        )
    )


@router.patch("/sessions/{session_id}", response_model=SessionOut)
def update_session(
    session_id: int,
    payload: SessionUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, user.id)
    if payload.title is not None:
        session.title = payload.title.strip() or session.title
    if payload.model_name is not None:
        session.model_name = payload.model_name
    if payload.temperature is not None:
        session.temperature = payload.temperature
    db.commit()
    db.refresh(session)
    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = _get_owned_session(db, session_id, user.id)
    db.execute(delete(ChatMessage).where(ChatMessage.session_id == session.id))
    db.delete(session)
    db.commit()


@router.get("/sessions/{session_id}/messages", response_model=list[MessageOut])
def list_messages(
    session_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_owned_session(db, session_id, user.id)
    return list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        )
    )


@router.post("/stream")
def chat_stream(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # ---- 同步准备：会话归属、历史消息、文档上下文（全部在线程池中执行） ----
    session: ChatSession
    if payload.session_id is None:
        session = ChatSession(
            user_id=user.id,
            title=payload.content.strip()[:DEFAULT_TITLE_CHARS] or "新对话",
            model_name=payload.model_name or "",
            temperature=payload.temperature if payload.temperature is not None else 0.7,
        )
        db.add(session)
        db.flush()
    else:
        session = _get_owned_session(db, payload.session_id, user.id)

    if payload.model_name:
        session.model_name = payload.model_name
    if payload.temperature is not None:
        session.temperature = payload.temperature
    from datetime import datetime

    session.updated_at = datetime.now()  # 触达更新时间，使会话在列表中置顶

    user_message = ChatMessage(session_id=session.id, role="user", content=payload.content)
    db.add(user_message)
    db.commit()
    db.refresh(session)

    history_rows = list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id, ChatMessage.id != user_message.id)
            .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
            .limit(MAX_HISTORY_MESSAGES)
        )
    )
    history_rows.reverse()
    history = [
        {"role": m.role, "content": m.content[:MAX_HISTORY_ITEM_CHARS]}
        for m in history_rows
    ]

    file_text = None
    if payload.file_id:
        file_text = load_parsed_text(payload.file_id)
        if file_text is None:
            raise HTTPException(status_code=400, detail="文档不存在或已过期，请重新上传")

    # 解析所选大模型服务商（各类 OpenAI 兼容接口 + 本地模型）
    provider = None
    if payload.provider_id:
        provider = get_provider(payload.provider_id)
        if provider is None:
            raise HTTPException(status_code=400, detail="所选服务商不存在，请到设置中重新选择")

    # 优先使用服务商配置的人设（system_prompt），未配置则回退默认助手人设
    system_prompt = (provider or {}).get("system_prompt") or None
    messages = build_messages(payload.content, history, file_text, system_prompt=system_prompt)

    model_name = session.model_name or (provider or {}).get("default_model") or None
    temperature = session.temperature

    # ---- SSE 流式输出 ----
    async def event_stream():
        collected: list[str] = []
        try:
            async for chunk in stream_chat(
                messages,
                provider=provider,
                model=model_name,
                temperature=temperature,
                max_tokens=payload.max_tokens,
            ):
                collected.append(chunk)
                yield f"data: {json.dumps({'type': 'delta', 'content': chunk}, ensure_ascii=False)}\n\n"
        except Exception as exc:  # 模型调用失败等
            yield f"data: {json.dumps({'type': 'error', 'message': f'生成失败：{exc}'}, ensure_ascii=False)}\n\n"
            return

        # 落库助手消息（线程池中执行，避免阻塞事件循环）
        from starlette.concurrency import run_in_threadpool

        def save_assistant() -> int:
            full = "".join(collected)
            assistant = ChatMessage(session_id=session.id, role="assistant", content=full or "（无内容）")
            db.add(assistant)
            db.commit()
            db.refresh(assistant)
            return assistant.id

        assistant_id = await run_in_threadpool(save_assistant)
        yield f"data: {json.dumps({'type': 'done', 'session_id': session.id, 'message_id': assistant_id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
